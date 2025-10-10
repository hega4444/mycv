"""AI providers and models endpoints."""

from typing import Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.service.providers import PROVIDERS, get_models_for_provider

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])


# Response Models
class ModelResponse(BaseModel):
    id: str
    name: str


class ProviderResponse(BaseModel):
    id: str
    name: str
    models: List[ModelResponse]


class ProvidersListResponse(BaseModel):
    providers: List[ProviderResponse]


# Endpoints
@router.get("", response_model=ProvidersListResponse)
def list_providers():
    """Get list of all available AI providers and their models."""
    providers = [
        ProviderResponse(
            id=provider_id,
            name=provider_data["name"],
            models=[
                ModelResponse(id=model["id"], name=model["name"])
                for model in provider_data["models"]
            ]
        )
        for provider_id, provider_data in PROVIDERS.items()
    ]

    return ProvidersListResponse(providers=providers)


@router.get("/{provider_id}/models", response_model=List[ModelResponse])
def get_provider_models(provider_id: str):
    """Get list of models for a specific provider."""
    models = get_models_for_provider(provider_id)

    if not models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found"
        )

    return [ModelResponse(id=model["id"], name=model["name"]) for model in models]
