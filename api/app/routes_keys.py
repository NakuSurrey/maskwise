"""
routes_keys.py - a logged-in user creates and lists their own API keys.
create returns the full key once. after that only the prefix is shown.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import ApiKey, User
from app.security import generate_api_key, hash_api_key

router = APIRouter(prefix="/keys", tags=["keys"])


# --- request / response shapes ---

class KeyCreateRequest(BaseModel):
    # optional name so a user can tell their keys apart
    label: str | None = None


class KeyCreateResponse(BaseModel):
    id: int
    api_key: str  # the full key - shown this one time only
    key_prefix: str
    label: str | None
    created_at: datetime


class KeyInfo(BaseModel):
    # listing never includes the full key - only what is safe to show
    model_config = ConfigDict(from_attributes=True)
    id: int
    key_prefix: str
    label: str | None
    created_at: datetime
    last_used_at: datetime | None


# --- routes ---

@router.post("", response_model=KeyCreateResponse, status_code=201)
def create_key(
    body: KeyCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KeyCreateResponse:
    # make the key, store only its hash + prefix, hand the full key back once
    raw, prefix = generate_api_key()
    key = ApiKey(
        user_id=user.id,
        key_hash=hash_api_key(raw),
        key_prefix=prefix,
        label=body.label,
    )
    db.add(key)
    db.commit()
    db.refresh(key)  # reload so id + created_at are filled in by the DB

    return KeyCreateResponse(
        id=key.id,
        api_key=raw,
        key_prefix=key.key_prefix,
        label=key.label,
        created_at=key.created_at,
    )


@router.get("", response_model=list[KeyInfo])
def list_keys(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApiKey]:
    # only this user's keys, newest first
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == user.id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )
