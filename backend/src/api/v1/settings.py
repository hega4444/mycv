"""User settings endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.v1.auth import get_current_user
from src.database import delete_api_key, get_user_settings, update_user_settings, get_database

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


# Request/Response Models
class SettingsResponse(BaseModel):
    provider: str
    model: str
    api_key_display: str | None
    has_api_key: bool


class SettingsUpdateRequest(BaseModel):
    provider: str
    model: str
    api_key: str | None = None


# Endpoints
@router.get("", response_model=SettingsResponse)
def get_settings(current_user: str = Depends(get_current_user)):
    """Get user settings."""
    with get_database() as db:
        try:
            settings = get_user_settings(db, current_user)

            return SettingsResponse(
                provider=settings["provider"],
                model=settings["model"],
                api_key_display=settings["api_key_display"],
                has_api_key=settings["has_api_key"]
            )
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except AttributeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def update_settings(
    request: SettingsUpdateRequest,
    current_user: str = Depends(get_current_user)
):
    """Update user settings (provider, model, and optionally API key)."""
    with get_database() as db:
        update_user_settings(
            db,
            user_email=current_user,
            provider=request.provider,
            model=request.model,
            api_key=request.api_key
        )

        return None


@router.delete("/api-key", status_code=status.HTTP_204_NO_CONTENT)
def delete_settings_api_key(current_user: str = Depends(get_current_user)):
    """Delete the API key for the current provider."""
    with get_database() as db:
        # Get current provider
        try:
            settings = get_user_settings(db, current_user)
            provider = settings["provider"]
        except (KeyError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )

        # Delete API key
        success = delete_api_key(db, current_user, provider)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return None
