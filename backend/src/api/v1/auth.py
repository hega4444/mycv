"""Authentication endpoints."""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt

from src.database import authenticate_user, create_user, get_database

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("APP_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer()


# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


class UserResponse(BaseModel):
    email: str


# JWT Utilities
def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = {"sub": email}

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """Decode JWT token and return email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    email = decode_access_token(token)
    return email


# Endpoints
@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest):
    """Create a new user account."""
    with get_database() as db:
        success = create_user(db, request.email, request.password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Auto-login after signup
        access_token = create_access_token(request.email)
        return TokenResponse(
            access_token=access_token,
            email=request.email
        )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Login with email and password."""
    with get_database() as db:
        user_email = authenticate_user(db, request.email, request.password)

        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token(user_email)
        return TokenResponse(
            access_token=access_token,
            email=user_email
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: str = Depends(get_current_user)):
    """Logout (client should discard token)."""
    # With JWT, logout is handled client-side by discarding the token
    # This endpoint exists for consistency and future token blacklisting if needed
    return None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: str = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse(email=current_user)
