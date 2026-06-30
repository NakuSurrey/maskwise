"""
auth.py — API key authentication dependency.
checks the X-API-Key header against the list of valid keys in settings.
runs AFTER the rate limiter — invalid keys cost the attacker rate-limit budget.
"""
from fastapi import Depends, Header, HTTPException, status

from app.config import settings
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ApiKey, User, _now
from app.security import decode_access_token, hash_api_key


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
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

    # look the key up by its sha256 hash - one indexed DB hit, no scan
    key_hash = hash_api_key(x_api_key)
    key_row = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
    if key_row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # stamp last_used_at so the dashboard can show when a key last ran
    key_row.last_used_at = _now()
    db.commit()

    return x_api_key


# --- logged-in user (JWT) ---




async def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    # the dashboard sends "Authorization: Bearer <jwt>". pull the token out.
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # token is valid - load the matching user so routes know who is calling.
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
