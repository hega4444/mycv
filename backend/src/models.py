"""Pydantic models for CV application."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class CVStatus(str, Enum):
    """CV processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(BaseModel):
    """User model."""

    email: EmailStr
    password_hash: str
    personal_data: Optional[Dict[str, Any]] = Field(
        default=None, description="User's personal information for CV"
    )
    cv_content: Optional[Dict[str, Any]] = Field(
        default=None, description="User's CV content (experience, skills, etc.)"
    )
    created_at: datetime = Field(default_factory=utc_now)


class CV(BaseModel):
    """CV document model."""

    user_email: EmailStr
    description: str = Field(..., description="Name/description for this CV")
    job_description: str = Field(..., description="Job description text")
    link: Optional[str] = Field(
        default=None, description="Optional link related to the job"
    )
    model: str = Field(...,)
    provider: str = Field(...,)
    status: CVStatus = Field(default=CVStatus.PENDING)
    cv_optimized: Optional[Dict[str, Any]] = Field(
        default=None, description="Optimized CV JSON"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CVCreate(BaseModel):
    """Model for creating a new CV."""

    description: str = Field(..., min_length=1, max_length=200)
    job_description: str = Field(..., min_length=10)
    link: Optional[str] = Field(default=None)
    model: str = Field(...,)
    provider: str = Field(...,)
