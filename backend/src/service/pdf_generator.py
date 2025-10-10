#!/usr/bin/env python3
"""
CV Generator - Generate PDF version of CV from JSON data and Jinja2 templates.
"""

from pathlib import Path
from typing import Any, Dict

import weasyprint  # type: ignore
from jinja2 import Environment, FileSystemLoader


def generate_pdf(
    cv_content: Dict[str, Any],
    personal_data: Dict[str, Any],
    template_name: str = "cv_template.html",
    output_postfix: str = "",
) -> str:
    """
    Generate PDF version of CV directly from template.

    Args:
        cv_content: CV content dictionary
        personal_data: Personal data dictionary
        template_name: Name of the Jinja2 template file
        output_postfix: Postfix for output filename (e.g., "_optimized")

    Returns:
        Path to generated PDF file
    """
    # Set up directories
    base_dir = Path(__file__).resolve().parents[2]
    templates_dir = base_dir / "data" / "templates"
    output_dir = base_dir / "output"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Merge data
    cv_data = {**personal_data, **cv_content}

    # Load template
    template = env.get_template(template_name)

    # Render HTML
    html_content = template.render(**cv_data)

    # Convert HTML to PDF with proper pagination
    output_name = f"cv{output_postfix}.pdf"
    pdf_path = output_dir / output_name

    try:
        # Configure weasyprint for proper pagination
        html_doc = weasyprint.HTML(string=html_content)
        css_string = """
            @page {
                size: A4;
                margin: 1.2cm 1.5cm 2cm 1.5cm;
            }

            /* Remove background and styling for PDF */
            body {
                background: white !important;
            }

            .cv-container {
                box-shadow: none !important;
                padding: 0 !important;
            }
        """

        css = weasyprint.CSS(string=css_string)
        html_doc.write_pdf(pdf_path, stylesheets=[css])

        return str(pdf_path)

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        raise
