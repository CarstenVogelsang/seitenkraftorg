"""
seitenkraft.org Backend API

FastAPI application for domain management and website generation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, wizard, domains
from app.core.config import get_settings

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="seitenkraft.org API",
    description="Domain-Verwaltung & Website-Generierung für SaaS-Partner",
    version="0.1.0-poc",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(wizard.router)
app.include_router(domains.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint

    Returns basic API information.
    """
    return {
        "name": "seitenkraft.org API",
        "version": "0.1.0-poc",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print("🚀 seitenkraft.org API starting...")
    print(f"   Environment: {'Production' if settings.is_production else 'Development'}")
    print(f"   INWX API: {settings.inwx_api_url}")
    print(f"   Debug: {settings.debug}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("👋 seitenkraft.org API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
