"""AI Provider and Model configurations."""

from typing import Optional

PROVIDERS = {
    "google": {
        "name": "Google",
        "models": [
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash"},
            {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash-Lite"},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
        ],
    },
    "groq": {
        "name": "Groq",
        "models": [
            {"id": "openai/gpt-oss-120b", "name": "OpenAI GPT OSS 120B"},
            {"id": "moonshotai/kimi-k2-instruct-0905", "name": "Kimi K2 Instruct"},
        ],
    },
}

# Default settings
DEFAULT_PROVIDER = "google"
DEFAULT_MODEL = "gemini-2.5-flash"


def get_provider_names():
    """Get list of provider names."""
    return list(PROVIDERS.keys())


def get_models_for_provider(provider: str):
    """Get list of models for a specific provider."""
    return PROVIDERS.get(provider, {}).get("models", [])


def get_provider_display_name(provider: str) -> Optional[str]:
    """Get display name for a provider."""
    name = PROVIDERS.get(provider, {}).get("name")
    if isinstance(name, str):
        return name
    return str(provider) if provider is not None else None
