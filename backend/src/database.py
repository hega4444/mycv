"""MongoDB database connection and repository functions."""

import base64
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List, Optional

import bcrypt
from bson import ObjectId
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pymongo import MongoClient

from src.service.providers import DEFAULT_MODEL, DEFAULT_PROVIDER
from src.models import CV, CVStatus, User

load_dotenv()


# Encryption key for API keys - derived from APP_SECRET_KEY
def _get_encryption_key() -> bytes:
    """Get or create encryption key for API keys."""
    secret = os.getenv("APP_SECRET_KEY", "change-this-to-a-random-secret-key")
    # Derive a proper 32-byte key from the secret
    key = base64.urlsafe_b64encode(secret.encode().ljust(32)[:32])
    return key


_fernet = Fernet(_get_encryption_key())

# Global client instance (reused across requests)
_client: MongoClient | None = None


def _get_client():
    """Get or create the global MongoDB client."""
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        # Create client with connection pool and generous timeouts
        _client = MongoClient(uri, maxPoolSize=5, minPoolSize=1)
    return _client


@contextmanager
def get_database():
    """
    Get MongoDB database session using connection pool.

    Yields:
        MongoDB Database instance

    Example:
        with get_database() as db:
            users = db.users.find_one({"email": "test@example.com"})
    """
    db_name = os.getenv("MONGODB_DATABASE", "mycv")
    client = _get_client()

    try:
        yield client[db_name]
    except Exception as e:
        # Don't close the client on error, just re-raise
        raise e


# Password utilities


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# User operations


def create_user(db, email: str, password: str) -> bool:
    """
    Create a new user with default provider and model settings.

    Returns:
        True if user created, False if user already exists
    """
    if db.users.find_one({"email": email}):
        return False

    user = User(email=email, password_hash=hash_password(password))
    user_data = user.model_dump()
    user_data["provider"] = DEFAULT_PROVIDER
    user_data["model"] = DEFAULT_MODEL

    db.users.insert_one(user_data)
    return True


def authenticate_user(db, email: str, password: str) -> Optional[str]:
    """
    Authenticate a user.

    Returns:
        User email if authenticated, None otherwise
    """
    user_doc = db.users.find_one({"email": email})
    if not user_doc:
        return None

    if verify_password(password, user_doc["password_hash"]):
        return user_doc["email"]
    return None


# CV operations


def create_cv(
    db,
    user_email: str,
    description: str,
    job_description: str,
    model: str,
    provider: str,
    link: Optional[str] = None,
) -> str:
    """
    Create a new CV entry.

    Returns:
        CV ID as string
    """
    cv = CV(
        user_email=user_email,
        description=description,
        job_description=job_description,
        link=link,
        status=CVStatus.PROCESSING,
        model=model,
        provider=provider,
    )
    result = db.cvs.insert_one(cv.model_dump())
    return str(result.inserted_id)


def get_user_cvs(db, user_email: str) -> List[dict]:
    """
    Get all CVs for a user, sorted by creation date (newest first).

    Returns:
        List of CV documents with _id converted to string
    """
    cvs = list(db.cvs.find({"user_email": user_email}).sort("created_at", -1))
    for cv in cvs:
        cv["_id"] = str(cv["_id"])
    return cvs


def get_cv_by_id(db, cv_id: str) -> Optional[dict]:
    """
    Get a CV by ID.

    Returns:
        CV document with _id as string, or None if not found
    """
    cv = db.cvs.find_one({"_id": ObjectId(cv_id)})
    if cv:
        cv["_id"] = str(cv["_id"])
    return cv


def update_cv_status(
    db, cv_id: str, status: CVStatus, error_message: Optional[str] = None
):
    """Update CV status."""
    update_data = {"status": status.value, "updated_at": datetime.now(timezone.utc)}
    if error_message:
        update_data["error_message"] = error_message

    db.cvs.update_one({"_id": ObjectId(cv_id)}, {"$set": update_data})


def update_cv_result(db, cv_id: str, cv_optimized: dict):
    """Update CV with optimized result."""
    db.cvs.update_one(
        {"_id": ObjectId(cv_id)},
        {
            "$set": {
                "status": CVStatus.COMPLETED.value,
                "cv_optimized": cv_optimized,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )


def delete_cv(db, cv_id: str) -> bool:
    """
    Delete a CV by ID.

    Returns:
        True if deleted, False if not found
    """
    result = db.cvs.delete_one({"_id": ObjectId(cv_id)})
    return result.deleted_count > 0


# API Key utilities


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key using Fernet symmetric encryption."""
    return _fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key."""
    return _fernet.decrypt(encrypted_key.encode()).decode()


def get_api_key_last_chars(api_key: str, num_chars: int = 4) -> str:
    """Get the last N characters of an API key for display."""
    return api_key[-num_chars:] if len(api_key) >= num_chars else api_key


# API Key operations


def store_api_key(db, user_email: str, provider: str, api_key: str) -> bool:
    """
    Store or update an encrypted API key for a user and provider.

    Args:
        db: Database connection
        user_email: User's email
        provider: Provider name (e.g., "google", "openai")
        api_key: Plain text API key

    Returns:
        True if stored successfully
    """
    encrypted_key = encrypt_api_key(api_key)
    last_chars = get_api_key_last_chars(api_key)

    db.api_keys.update_one(
        {"user_email": user_email, "provider": provider},
        {
            "$set": {
                "api_key_encrypted": encrypted_key,
                "last_chars": last_chars,
                "updated_at": datetime.now(timezone.utc),
            },
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
        },
        upsert=True,
    )
    return True


def get_api_key(db, user_email: str, provider: str) -> Optional[str]:
    """
    Get the decrypted API key for a user and provider.

    Args:
        db: Database connection
        user_email: User's email
        provider: Provider name

    Returns:
        Plain text API key or None if not found
    """
    key_doc = db.api_keys.find_one({"user_email": user_email, "provider": provider})
    if not key_doc:
        return None

    encrypted_key = key_doc.get("api_key_encrypted")
    if not encrypted_key:
        return None

    try:
        return decrypt_api_key(encrypted_key)
    except Exception:
        return None


def get_api_key_display(db, user_email: str, provider: str) -> Optional[str]:
    """
    Get the masked API key for display (shows only last 4 chars).

    Args:
        db: Database connection
        user_email: User's email
        provider: Provider name

    Returns:
        Masked key string (e.g., "••••••••5a2f") or None if not found
    """
    key_doc = db.api_keys.find_one({"user_email": user_email, "provider": provider})
    if not key_doc:
        return None

    last_chars = key_doc.get("last_chars", "")
    return f"{'•' * 3}{last_chars}"


def delete_api_key(db, user_email: str, provider: str) -> bool:
    """
    Delete an API key for a user and provider.

    Args:
        db: Database connection
        user_email: User's email
        provider: Provider name

    Returns:
        True if deleted, False if not found
    """
    result = db.api_keys.delete_one({"user_email": user_email, "provider": provider})
    return result.deleted_count > 0


# User settings operations


def get_user_settings(db, user_email: str) -> dict:
    """
    Get user settings including API key status.

    Returns:
        Dict with provider, model, api_key (decrypted), and api_key_display (masked)
    """
    user_doc = db.users.find_one({"email": user_email})
    if not user_doc:
        raise KeyError("No user found")
    
    provider = user_doc.get("provider")
    if not provider:
        raise AttributeError("Missing provider in user settings")
    
    model = user_doc.get("model")
    if not provider:
        raise AttributeError("Missing model in user settings")
    
    api_key = get_api_key(db, user_email, provider)
    api_key_display = get_api_key_display(db, user_email, provider)
    
    return {
        "provider": provider,
        "model": model,
        "api_key": api_key,  # Decrypted key for actual use
        "api_key_display": api_key_display,  # Masked for display
        "has_api_key": api_key is not None,
    }


def update_user_settings(
    db, user_email: str, provider: str, model: str, api_key: Optional[str] = None
):
    """
    Update user's provider and model settings, optionally with API key.

    Args:
        db: Database connection
        user_email: User's email
        provider: Provider name
        model: Model name
        api_key: Optional new API key to store
    """
    db.users.update_one(
        {"email": user_email}, {"$set": {"provider": provider, "model": model}}
    )

    # Store API key if provided
    if api_key:
        store_api_key(db, user_email, provider, api_key)
