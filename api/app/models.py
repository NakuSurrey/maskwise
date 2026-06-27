"""
models.py - User and ApiKey tables.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


def _now():
    # timezone-aware UTC timestamp for created_at / last_used_at
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)

    # one user owns many api keys. delete the user -> their keys go too
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    # sha256 of the full key - lets /mask find the row fast. keys are random, so sha256 is safe
    key_hash = Column(String(64), unique=True, nullable=False, index=True)
    # first chars shown in the dashboard so a user recognises a key without seeing it whole
    key_prefix = Column(String(16), nullable=False)
    label = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="api_keys")
