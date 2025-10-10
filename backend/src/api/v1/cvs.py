"""CV generation and management endpoints."""

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.api.v1.auth import get_current_user
from src.app.background import generate_pdf_for_cv, process_cv_background
from src.database import delete_cv, get_cv_by_id, get_user_cvs, get_user_settings, create_cv as db_create_cv, get_database
from src.models import CVCreate, CVStatus

router = APIRouter(prefix="/api/v1/cvs", tags=["CVs"])


# Request/Response Models
class CVCreateRequest(BaseModel):
    description: str
    job_description: str
    link: str | None = None


class CVResponse(BaseModel):
    id: str
    description: str
    job_description: str
    link: str | None
    model: str
    provider: str
    status: str
    cv_optimized: Dict[str, Any] | None
    error_message: str | None
    created_at: str
    updated_at: str


class CVListResponse(BaseModel):
    cvs: List[CVResponse]


class CVStatusResponse(BaseModel):
    status: str
    error_message: str | None = None


# Endpoints
@router.get("", response_model=CVListResponse)
def list_cvs(current_user: str = Depends(get_current_user)):
    """Get all CVs for the current user."""
    with get_database() as db:
        cvs = get_user_cvs(db, current_user)

        cv_responses = [
            CVResponse(
                id=cv["_id"],
                description=cv["description"],
                job_description=cv["job_description"],
                link=cv.get("link", "NA"),
                model=cv.get("model", "NA"),
                provider=cv.get("provider", "NA"),
                status=cv["status"],
                cv_optimized=cv.get("cv_optimized"),
                error_message=cv.get("error_message"),
                created_at=cv["created_at"].isoformat(),
                updated_at=cv["updated_at"].isoformat(),
            )
            for cv in cvs
        ]

        return CVListResponse(cvs=cv_responses)


@router.post("", response_model=CVResponse, status_code=status.HTTP_201_CREATED)
def create_cv(
    request: CVCreateRequest,
    current_user: str = Depends(get_current_user)
):
    """Create a new CV and start optimization process."""
    with get_database() as db:
        # Get user settings for model/provider and API key
        settings = get_user_settings(db, current_user)
        api_key = settings.get("api_key")

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing API key in settings. Please configure your API key first."
            )

        # Create CV document
        cv_id = db_create_cv(
            db,
            user_email=current_user,
            description=request.description,
            job_description=request.job_description,
            model=settings.get("model"),
            provider=settings.get("provider"),
            link=request.link,
        )

        # Create CVCreate model for background processing
        cv_create = CVCreate(
            description=request.description,
            job_description=request.job_description,
            link=request.link,
            model=settings.get("model"),
            provider=settings.get("provider")
        )

        # Start background processing
        process_cv_background(cv_id, cv_create, api_key, current_user)

        # Return the created CV
        cv = get_cv_by_id(db, cv_id)

        return CVResponse(
            id=cv["_id"],
            description=cv["description"],
            job_description=cv["job_description"],
            link=cv.get("link"),
            model=cv["model"],
            provider=cv["provider"],
            status=cv["status"],
            cv_optimized=cv.get("cv_optimized"),
            error_message=cv.get("error_message"),
            created_at=cv["created_at"].isoformat(),
            updated_at=cv["updated_at"].isoformat(),
        )


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv(cv_id: str, current_user: str = Depends(get_current_user)):
    """Get a specific CV by ID."""
    with get_database() as db:
        cv = get_cv_by_id(db, cv_id)

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )

        # Verify ownership
        if cv["user_email"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this CV"
            )

        return CVResponse(
            id=cv["_id"],
            description=cv["description"],
            job_description=cv["job_description"],
            link=cv.get("link"),
            model=cv["model"],
            provider=cv["provider"],
            status=cv["status"],
            cv_optimized=cv.get("cv_optimized"),
            error_message=cv.get("error_message"),
            created_at=cv["created_at"].isoformat(),
            updated_at=cv["updated_at"].isoformat(),
        )


@router.delete("/{cv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cv_endpoint(cv_id: str, current_user: str = Depends(get_current_user)):
    """Delete a CV."""
    with get_database() as db:
        # Verify ownership first
        cv = get_cv_by_id(db, cv_id)

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )

        if cv["user_email"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this CV"
            )

        # Delete
        success = delete_cv(db, cv_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )

        return None


@router.get("/{cv_id}/pdf")
def get_cv_pdf(cv_id: str, current_user: str = Depends(get_current_user)):
    """Generate and download PDF for a CV."""
    with get_database() as db:
        cv = get_cv_by_id(db, cv_id)

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )

        # Verify ownership
        if cv["user_email"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this CV"
            )

        # Check if CV is completed
        if cv["status"] != CVStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CV is not ready. Current status: {cv['status']}"
            )

        # Generate PDF
        try:
            pdf_path = generate_pdf_for_cv(cv_id, cv["cv_optimized"], current_user)
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="PDF generation failed"
                )

            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=f"{cv['description']}.pdf"
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating PDF: {str(e)}"
            )


@router.get("/{cv_id}/status", response_model=CVStatusResponse)
def get_cv_status(cv_id: str, current_user: str = Depends(get_current_user)):
    """Get the current status of a CV (for polling)."""
    with get_database() as db:
        cv = get_cv_by_id(db, cv_id)

        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )

        # Verify ownership
        if cv["user_email"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this CV"
            )

        return CVStatusResponse(
            status=cv["status"],
            error_message=cv.get("error_message")
        )
