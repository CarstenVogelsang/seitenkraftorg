"""
Health Check Endpoint
"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns system status and configuration info.
    """
    settings = get_settings()

    return HealthResponse(
        status="ok",
        version="0.1.0-poc",
        environment="production" if settings.is_production else "development"
    )
