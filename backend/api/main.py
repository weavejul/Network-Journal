"""
Main FastAPI application for the Network Journal API.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from shared.config import get_settings, is_development
from shared.utils import setup_logging

# Import routers
from backend.api.routers import people, companies, interactions, topics, events, locations, graph, ai

# Setup logging
logger = setup_logging(__name__)

# Get settings
settings = get_settings()

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Network Journal API",
    description="A personal intelligence system for mapping and understanding your network",
    version="1.0.0",
    docs_url="/docs" if is_development() else None,
    redoc_url="/redoc" if is_development() else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(people.router, prefix=f"{settings.API_PREFIX}/people", tags=["people"])
app.include_router(companies.router, prefix=f"{settings.API_PREFIX}/companies", tags=["companies"])
app.include_router(interactions.router, prefix=f"{settings.API_PREFIX}/interactions", tags=["interactions"])
app.include_router(topics.router, prefix=f"{settings.API_PREFIX}/topics", tags=["topics"])
app.include_router(events.router, prefix=f"{settings.API_PREFIX}/events", tags=["events"])
app.include_router(locations.router, prefix=f"{settings.API_PREFIX}/locations", tags=["locations"])
app.include_router(graph.router, prefix=f"{settings.API_PREFIX}/graph", tags=["graph"])
app.include_router(ai.router, prefix=f"{settings.API_PREFIX}/ai", tags=["ai"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Network Journal API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Add database health check here
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    logger.error(f"Request validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc):
    logger.error(f"Pydantic validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=is_development(),
        log_level=settings.LOG_LEVEL.lower()
    ) 