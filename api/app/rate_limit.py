"""
rate_limit.py — slowapi limiter setup.
caps requests per client IP per period (60/minute by default).
runs BEFORE the auth check so failed key guesses still count against the budget.
in-process for now; swaps to Redis-backed in Phase 2 for multi-instance support.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


# single shared limiter for the whole app
# key_func decides how to identify a caller — get_remote_address uses the IP
# default_limits applies to every endpoint unless overridden per-route
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit],   # e.g. "60/minute" from .env
)
