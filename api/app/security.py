"""
security.py - password hashing (bcrypt) and login tokens (JWT).
two halves of one job: prove a user is who they claim to be.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


# --- passwords ---

def hash_password(plain: str) -> str:
    # bcrypt needs bytes. it salts internally, so every hash differs.
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    # checkpw re-hashes plain with the salt baked into hashed, then compares.
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# --- login tokens (JWT) ---

def create_access_token(user_id: int) -> str:
    # the token says who (sub) and when it dies (exp). signed with our secret.
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    # verify the signature + expiry. return the user id, or None if bad/expired.
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None


# --- api keys ---

import hashlib
import secrets


def generate_api_key() -> tuple[str, str]:
    # make a random key and the short prefix shown in the dashboard.
    # token_urlsafe gives a long random string, safe in URLs and headers.
    raw = "mk_live_" + secrets.token_urlsafe(32)
    prefix = raw[:12]
    return raw, prefix


def hash_api_key(raw: str) -> str:
    # sha256 hex of the full key. fast and one-way, so we store this not the key.
    # keys are long and random, so sha256 (no salt) is safe here - unlike passwords.
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
