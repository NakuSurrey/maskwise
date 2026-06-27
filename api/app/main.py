"""
main.py — FastAPI entrypoint.
Phase 1: adds /mask (PII detection + masking).
wires together masker (Presidio), auth (API key), and rate_limit (slowapi).
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth import require_api_key
from app.config import settings
from app.masker import Masker
from app.db import engine, Base
from app import models  # noqa: F401 - import registers User + ApiKey tables on Base
from app.rate_limit import limiter
from app.schemas import MaskRequest, MaskResponse


# ─── lifespan — runs once on startup, once on shutdown ──────────
# Presidio + spaCy take ~10-15 sec to load on first import
# we do this in the lifespan so the container only pays the cost once,
# and the model is ready before the first request lands
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.masker = Masker()
    # create users + api_keys tables if they do not exist yet
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown — nothing to clean up; spaCy releases RAM on process exit


# ─── app instance ───────────────────────────────────────────────
# disable interactive docs in production — small attack-surface reduction
app = FastAPI(
    title="MaskWise API",
    description="Production PII masking service for LLMs.",
    version="0.2.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    openapi_url="/openapi.json" if settings.app_env != "production" else None,
    lifespan=lifespan,
)


# ─── rate limiter wiring ────────────────────────────────────────
# attach the limiter to app.state so slowapi's middleware can find it
# register the 429 handler so over-limit requests get a clean JSON response
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
            "version": "0.2.0",
            "environment": settings.app_env,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """
    root — points clients at /health, /mask, and the public site.
    """
    return JSONResponse(
        status_code=200,
        content={
            "service": "MaskWise API",
            "health": "/health",
            "mask":   "POST /mask  (requires X-API-Key header)",
            "docs":   "/docs (development only)",
            "website": "https://maskwise.nakularora.tech",
        },
    )


@app.post(
    "/mask",
    tags=["mask"],
    response_model=MaskResponse,
    dependencies=[Depends(require_api_key)],
    summary="Detect and mask PII in text",
    description=(
        "POST text → receive masked text + list of PII entities found. "
        "Requires X-API-Key header. Rate-limited per IP."
    ),
)
@limiter.limit(settings.rate_limit)
async def mask(request: Request, body: MaskRequest) -> MaskResponse:
    """run Presidio on the request text, return the masked result.

    note on `request: Request` — slowapi needs the raw Request object
    to read the client IP. it must be the FIRST parameter.
    """
    result = request.app.state.masker.mask(
        text=body.text,
        entities=body.entities,
    )
    return MaskResponse(**result)
