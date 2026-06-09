"""
auth.py — API key authentication dependency.
checks the X-API-Key header against the list of valid keys in settings.
runs AFTER the rate limiter — invalid keys cost the attacker rate-limit budget.
"""
from fastapi import Header, HTTPException, status

from app.config import settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    """FastAPI dependency — attach to any route to require a valid API key.

    usage:
        @app.post("/mask", dependencies=[Depends(require_api_key)])

    returns the validated key string (useful for per-key logging later).
    raises 401 if the header is missing or the key is unknown.
    """
    if not x_api_key:
        # missing header — generic message, no hints to attacker
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_api_key not in settings.api_keys_list:
        # unknown key — same generic message, no leak of which keys exist
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return x_api_key
