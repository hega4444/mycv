"""
AI Service for optimizing CV content based on job descriptions.
Uses Pydantic AI to generate structured, tailored CV content.
"""

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.groq import GroqProvider

from src.service.pdf_generator import generate_pdf  # type: ignore

# Load environment variables from .env file
load_dotenv()


class TechnicalSkills(BaseModel):
    """Technical skills list."""

    technical_skills: list[str]


class Experience(BaseModel):
    """Work experience entry."""

    job_title: str
    company: str
    location: str
    start_date: str
    end_date: str
    stack: str
    achievements: list[str]


class Education(BaseModel):
    """Education entry."""

    degree: str
    institution: str
    location: str
    graduation_year: str
    start_year: str | None = None
    details: str | None = None


class Course(BaseModel):
    """Course or certification entry."""

    name: str
    provider: str
    location: str
    year: str
    description: str


class Project(BaseModel):
    """Key project entry."""

    name: str
    period: str
    description: str
    technologies: list[str]
    details: str


class Language(BaseModel):
    """Language proficiency entry."""

    language: str
    proficiency: str


class CVContent(BaseModel):
    """Validated CV content structure matching cv_content.json schema."""

    professional_summary: str = Field(
        ..., description="Impactful 2-3 sentence professional summary"
    )
    core_competencies: TechnicalSkills = Field(
        ..., description="Technical skills organized by category"
    )
    professional_experience: list[Experience] = Field(
        ..., description="Work experience with achievements"
    )
    education: list[Education] = Field(..., description="Educational background")
    courses: list[Course] = Field(
        default_factory=list, description="Relevant courses and certifications"
    )
    key_projects: list[Project] = Field(
        default_factory=list, description="Notable projects"
    )
    languages: list[Language] = Field(
        default_factory=list, description="Language proficiencies"
    )


# System prompt template for CV optimization
SYSTEM_PROMPT_TEMPLATE = """Expert CV optimizer. Mission: Maximize chances of
landing THIS specific job by presenting existing experience optimally.

TARGET JOB DESCRIPTION:
{job_description}

CURRENT CV JSON DATA:
{current_cv}

RULES:
1. NEVER over fabricate/exaggerate - only reorder, rephrase, emphasize
2. Preserve all work experiences, projects, education
3. Skills: REMOVE least/not relevant skills, ADD/ADAPT keywords matching job terminology
4. Rephrase achievements for relevance, don't create new ones
5. NEVER include markdown like **bold** or *italic*
6. NEVER use typical LLM generated symbols like M-dashes —

STRATEGY:
1. Craft 3-line summary positioning candidate as perfect fit
2. Reorder skills/achievements - most relevant first (recruiters scan 6 sec)
3. Integrate job keywords naturally (ATS scoring)
4. Use action verbs, metrics, results-driven language
5. Make every bullet point scream relevance to target role

OUTPUT:
Return optimized CV matching the exact structure of the input CV with:
- professional_summary: 3-line hook for THIS role
- core_competencies: Relevant skills first (job keywords)
- professional_experience: Rewritten for relevance
- All sections reordered by relevance to THIS job

Goal: Make recruiter think "This is EXACTLY who we need" and ATS score 85%+"""


def remove_markdown_formatting(data: Any) -> Any:
    """
    Recursively remove markdown formatting from strings in data structure.

    Args:
        data: Any data structure (dict, list, str, etc.)

    Returns:
        Data with markdown formatting removed from all strings
    """
    import re

    if isinstance(data, str):
        # Remove bold (**text** or __text__)
        data = re.sub(r"\*\*(.+?)\*\*", r"\1", data)
        data = re.sub(r"__(.+?)__", r"\1", data)
        # Remove italic (*text* or _text_)
        data = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", data)
        data = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"\1", data)
        if data[-1] == ".":
            data = data[:-1]
        return data
    elif isinstance(data, dict):
        return {k: remove_markdown_formatting(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [remove_markdown_formatting(item) for item in data]
    else:
        return data


def validate_cv_structure(
    original_cv: Dict[str, Any], optimized_cv: Dict[str, Any]
) -> None:
    """
    Validate that optimized CV maintains structure and critical data.

    Args:
        original_cv: Original CV data
        optimized_cv: Optimized CV data

    Raises:
        ValueError: If validation fails
    """
    # Check critical sections exist
    required = [
        "professional_summary",
        "core_competencies",
        "professional_experience",
        "education",
    ]

    missing = [s for s in required if s not in optimized_cv]
    if missing:
        raise ValueError(f"Missing sections: {missing}")

    # Check experience count preserved
    orig_exp = len(original_cv.get("professional_experience", []))
    opt_exp = len(optimized_cv.get("professional_experience", []))

    if opt_exp < orig_exp:
        raise ValueError(f"Lost {orig_exp - opt_exp} work experience entries")


def get_model_instance(model_name: str, provider: str, api_key: str):
    """
    Create a model instance based on provider.

    Args:
        model: Model identifier (e.g., "gemini-2.5-flash")
        provider: Provider name (currently only "google" supported)
        api_key: API key for the provider

    Returns:
        Model instance ready for use with Agent

    Raises:
        ValueError: If provider is not supported
    """
    match provider.lower():
        case "google":
            google_provider = GoogleProvider(api_key=api_key)
            return GoogleModel(model_name, provider=google_provider)

        case "groq":
            groq_provider = GroqProvider(api_key=api_key)
            return GroqModel(model_name, provider=groq_provider)

        case _:
            raise ValueError(f"Provider '{provider}' not supported yet.")


def optimize_cv_for_job(
    job_description: str,
    cv_content: Dict[str, Any],
    model: str = "gemini-2.5-flash",
    provider: str = "google",
    api_key: str | None = None,
) -> Dict[str, Any]:
    """
    Optimize CV content for a specific job description.

    Args:
        job_description: The target job description text
        cv_content: CV content dictionary
        model: AI model to use (default: gemini-2.5-flash)
        provider: AI provider (default: "google")
        api_key: API key (if None, reads from GOOGLE_API_KEY env var)

    Returns:
        Optimized CV content as dictionary

    Raises:
        ValidationError: If the optimized CV fails validation
        ValueError: If provider is not supported or API key missing
    """
    current_cv = cv_content

    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not provided and default GOOGLE_API_KEY not found in environment"
        )

    # Create model instance
    model_instance = get_model_instance(model, provider, api_key)

    # Create agent with system prompt including job description and CV
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        job_description=job_description, current_cv=json.dumps(current_cv, indent=2)
    )

    agent = Agent(
        model=model_instance, output_type=CVContent, system_prompt=system_prompt
    )

    # Simple user prompt
    prompt = "Optimize the CV data for the target job description."

    # Run the agent
    result = agent.run_sync(prompt)

    # Convert result to dict
    optimized_cv = result.output.model_dump()

    # Remove markdown formatting
    optimized_cv = remove_markdown_formatting(optimized_cv)

    # Validate structure
    validate_cv_structure(current_cv, optimized_cv)

    return optimized_cv


def save_optimized_cv(
    optimized_cv: Dict[str, Any], output_path: str = "data/cv_content_optimized.json"
) -> None:
    """
    Save optimized CV to a JSON file.

    Args:
        optimized_cv: Optimized CV content dictionary
        output_path: Output file path
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(optimized_cv, f, indent=2, ensure_ascii=False)

    print(f"💾 Optimized CV saved to: {output_path}")


def generate_optimized_cv(
    job_description: str,
    cv_content: Dict[str, Any],
    personal_data: Dict[str, Any],
    output_postfix: str = "_optimized",
    model: str = "gemini-2.5-flash",
    provider: str = "google",
    api_key: str | None = None,
) -> str:
    """
    Full pipeline: optimize CV and generate PDF.

    Args:
        job_description: Target job description
        cv_content: Original CV content dictionary
        personal_data: Personal data dictionary
        output_postfix: Postfix for output filename
        model: AI model to use
        provider: AI provider
        api_key: Optional API key

    Returns:
        Path to generated PDF file
    """

    # Optimize CV with AI Agent
    print("🦕 Optimizing content for target role...")
    optimized_cv = optimize_cv_for_job(
        job_description=job_description,
        cv_content=cv_content,
        model=model,
        provider=provider,
        api_key=api_key,
    )

    # Generate PDF
    pdf_path = generate_pdf(
        cv_content=optimized_cv,
        personal_data=personal_data,
        output_postfix=output_postfix,
    )
    print(f"✅ PDF CV generated: {pdf_path}")

    return pdf_path
