"""CV rendering service - loads templates at startup."""

from datetime import datetime
from pathlib import Path

from jinja2 import Template


# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "data" / "templates"

# Load templates at module import time
_base_template: Template = None     # type: ignore
_header_template: Template = None   # type: ignore
_section_templates = {}


def _load_templates():
    """Load all templates into memory."""
    global _base_template, _header_template, _section_templates

    # Load base template
    with open(TEMPLATES_DIR / "cv_base.html", "r", encoding="utf-8") as f:
        _base_template = Template(f.read())

    # Load header template
    with open(TEMPLATES_DIR / "header.html", "r", encoding="utf-8") as f:
        _header_template = Template(f.read())

    # Load section templates
    section_files = {
        "professional_summary": "professional_summary.html",
        "core_competencies": "core_competencies.html",
        "professional_experience": "professional_experience.html",
        "education": "education.html",
        "courses": "courses.html",
        "key_projects": "key_projects.html",
        "languages": "languages.html"
    }

    for key, filename in section_files.items():
        with open(TEMPLATES_DIR / filename, "r", encoding="utf-8") as f:
            _section_templates[key] = Template(f.read())


# Load templates when module is imported
_load_templates()


def render_cv(personal_data: dict, sections_state: dict) -> str:
    """
    Render complete CV HTML from personal data and sections state.

    Args:
        personal_data: Dict with personal information (name, email, etc.)
        sections_state: Dict with section keys and their content/order

    Returns:
        Complete HTML string
    """
    # Render header
    header_html = _header_template.render(
        personal_info={
            "name": personal_data.get("full_name", ""),
            "title": personal_data.get("job_title", ""),
            "location": personal_data.get("location", ""),
            "phone": personal_data.get("phone", ""),
            "email": personal_data.get("email", ""),
            "linkedin": personal_data.get("linkedin", ""),
            "github": personal_data.get("github", ""),
            "nationality": personal_data.get("nationality", ""),
            "portfolio": personal_data.get("website", ""),
        }
    )

    # Render sections in order
    sorted_sections = sorted(sections_state.items(), key=lambda x: x[1]["order"])
    sections_html = ""

    for section_key, section_data in sorted_sections:
        if section_key in _section_templates:
            sections_html += _section_templates[section_key].render(
                display_as=section_data["display_as"],
                content=section_data["content"]
            )

    # Render complete HTML
    return _base_template.render(
        personal_info={
            "name": personal_data.get("full_name", ""),
        },
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        header=header_html,
        sections=sections_html
    )
