"""
schemas.py — Pydantic models for /mask request + response.
defines the API contract. FastAPI uses these to:
  - validate incoming JSON (bad shape → 422 Unprocessable Entity)
  - serialize responses (Python dict → JSON)
  - generate the OpenAPI schema at /openapi.json
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from app.entities import DEFAULT_ENTITIES


# ─── request ────────────────────────────────────────────────────
class MaskRequest(BaseModel):
    """body of POST /mask"""

    text: str = Field(
        ...,                              # required
        min_length=1,
        max_length=10_000,                # Phase 1 cap — prevents abuse
        description="Text to scan for PII. Max 10,000 characters.",
        examples=["Hi, I am John Doe and my email is john@example.com"],
    )

    entities: Optional[List[str]] = Field(
        default=None,
        description=(
            "Optional list of PII types to detect. "
            f"Defaults to all {len(DEFAULT_ENTITIES)} supported types."
        ),
        examples=[["PERSON", "EMAIL_ADDRESS"]],
    )


# ─── response ───────────────────────────────────────────────────
class EntityHit(BaseModel):
    """one PII span found in the input"""

    type:  str = Field(..., description="Presidio entity code, e.g. PERSON")
    label: str = Field(..., description="Human-readable label, e.g. 'Person Name'")
    start: int = Field(..., description="Start character index in original text")
    end:   int = Field(..., description="End character index in original text")
    score: float = Field(..., description="Detector confidence, 0.0 to 1.0")


class MaskResponse(BaseModel):
    """body of the /mask response"""

    masked_text:    str             = Field(..., description="Input text with PII replaced by <TYPE> tokens")
    entities_found: List[EntityHit] = Field(..., description="Every PII span detected")
    entities_count: int             = Field(..., description="Total number of spans masked")
