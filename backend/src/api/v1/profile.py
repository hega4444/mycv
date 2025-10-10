"""Profile and CV template management endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.v1.auth import get_current_user
from src.database import get_database
from src.service.cv_renderer import render_cv

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


# Request/Response Models
class PersonalDataUpdate(BaseModel):
    full_name: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    nationality: str | None = None
    website: str | None = None
    linkedin: str | None = None
    github: str | None = None


class CVContentUpdate(BaseModel):
    cv_content: Dict[str, Any]


class ProfileResponse(BaseModel):
    personal_data: Dict[str, Any]
    cv_content: Dict[str, Any]


class PreviewResponse(BaseModel):
    html: str


# Helper function to transform personal_data structure
def transform_personal_data_to_api(db_personal_data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Transform DB personal_data to API format."""
    if not db_personal_data:
        return {
            "full_name": "",
            "job_title": "",
            "email": "",
            "phone": "",
            "location": "",
            "nationality": "",
            "website": "",
            "linkedin": "",
            "github": ""
        }

    # Extract from nested structure if it exists
    if "personal_info" in db_personal_data:
        personal_info = db_personal_data["personal_info"]
        return {
            "full_name": personal_info.get("name", ""),
            "job_title": personal_info.get("title", ""),
            "email": personal_info.get("email", ""),
            "phone": personal_info.get("phone", ""),
            "location": personal_info.get("location", ""),
            "nationality": personal_info.get("nationality", ""),
            "website": personal_info.get("portfolio", ""),
            "linkedin": personal_info.get("linkedin", ""),
            "github": personal_info.get("github", ""),
        }

    # Fallback: already in API format
    return db_personal_data


def transform_personal_data_to_db(api_personal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform API personal_data to DB format."""
    return {
        "personal_info": {
            "name": api_personal_data.get("full_name", ""),
            "title": api_personal_data.get("job_title", ""),
            "email": api_personal_data.get("email", ""),
            "phone": api_personal_data.get("phone", ""),
            "location": api_personal_data.get("location", ""),
            "nationality": api_personal_data.get("nationality", ""),
            "portfolio": api_personal_data.get("website", ""),
            "linkedin": api_personal_data.get("linkedin", ""),
            "github": api_personal_data.get("github", ""),
        }
    }


# Endpoints
@router.get("", response_model=ProfileResponse)
def get_profile(current_user: str = Depends(get_current_user)):
    """Get user's personal data and CV content."""
    with get_database() as db:
        user_doc = db.users.find_one({"email": current_user})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Transform personal data to API format
        personal_data = transform_personal_data_to_api(user_doc.get("personal_data"))
        cv_content = user_doc.get("cv_content", {})

        return ProfileResponse(
            personal_data=personal_data,
            cv_content=cv_content
        )


@router.put("/personal", status_code=status.HTTP_204_NO_CONTENT)
def update_personal_data(
    update: PersonalDataUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update user's personal data."""
    with get_database() as db:
        # Get current personal data
        user_doc = db.users.find_one({"email": current_user})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get existing data
        current_personal_data = transform_personal_data_to_api(user_doc.get("personal_data"))

        # Update only provided fields
        update_dict = update.model_dump(exclude_unset=True)
        current_personal_data.update(update_dict)

        # Transform to DB format
        db_format = transform_personal_data_to_db(current_personal_data)

        # Update in database
        db.users.update_one(
            {"email": current_user},
            {"$set": {"personal_data": db_format}}
        )

        return None


@router.put("/content", status_code=status.HTTP_204_NO_CONTENT)
def update_cv_content(
    update: CVContentUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update user's CV content (sections)."""
    with get_database() as db:
        result = db.users.update_one(
            {"email": current_user},
            {"$set": {"cv_content": update.cv_content}}
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return None


@router.get("/preview", response_model=PreviewResponse)
def get_cv_preview(current_user: str = Depends(get_current_user)):
    """Generate HTML preview of CV template."""
    with get_database() as db:
        user_doc = db.users.find_one({"email": current_user})

        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        personal_data = transform_personal_data_to_api(user_doc.get("personal_data"))
        cv_content = user_doc.get("cv_content", {})

        # Convert cv_content to sections_state format expected by render_cv
        sections_state = {
            "professional_summary": {
                "title": "Professional Summary",
                "display_as": "Professional Summary",
                "order": 0,
                "content": cv_content.get("professional_summary", ""),
            },
            "core_competencies": {
                "title": "Core Competencies",
                "display_as": "Core Competencies",
                "order": 1,
                "content": cv_content.get("core_competencies", {}),
            },
            "professional_experience": {
                "title": "Professional Experience",
                "display_as": "Professional Experience",
                "order": 2,
                "content": cv_content.get("professional_experience", []),
            },
            "education": {
                "title": "Education",
                "display_as": "Education",
                "order": 3,
                "content": cv_content.get("education", []),
            },
            "courses": {
                "title": "Courses",
                "display_as": "Courses",
                "order": 4,
                "content": cv_content.get("courses", []),
            },
            "key_projects": {
                "title": "Key Projects",
                "display_as": "Key Projects",
                "order": 5,
                "content": cv_content.get("key_projects", []),
            },
            "languages": {
                "title": "Languages",
                "display_as": "Languages",
                "order": 6,
                "content": cv_content.get("languages", []),
            },
        }

        # Render CV
        html = render_cv(personal_data, sections_state)

        return PreviewResponse(html=html)
