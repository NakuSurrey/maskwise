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
