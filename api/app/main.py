"""
main.py — FastAPI entrypoint.

stub phase: serves /health only.
Phase 1 will add /api/v1/mask, /api/v1/unmask, /api/v1/verify-erasure.
"""

from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings


# ─── app instance ───────────────────────────────────────────────
# disable interactive docs in production — small attack-surface reduction
app = FastAPI(
    title="MaskWise API",
    description="Production PII masking service for LLMs.",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    openapi_url="/openapi.json" if settings.app_env != "production" else None,
)


# ─── routes ─────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health() -> JSONResponse:
    """
    health check — pinged by docker, nginx, and Uptime Kuma.

    returns 200 with a metadata-only payload.
    NO user data, NO secrets, NO env values — even on this endpoint.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "maskwise-api",
            "version": "0.1.0",
            "environment": settings.app_env,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """
    root — points clients at /health and the public site.
    """
    return JSONResponse(
        status_code=200,
        content={
            "service": "MaskWise API",
            "health": "/health",
            "docs": "/docs (development only)",
            "website": "https://maskwise.nakularora.tech",
        },
    )
