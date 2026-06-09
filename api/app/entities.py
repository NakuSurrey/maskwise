"""
entities.py — whitelist of PII entity types MaskWise detects + masks.
single source of truth. add or remove types here; masker.py reads this list.
Presidio supports 50+ types; we expose a curated subset to keep the API predictable.
"""

# ─── default entity set (Phase 1) ──────────────────────────────────
# names from Presidio's built-in recognizers
# https://microsoft.github.io/presidio/supported_entities/
DEFAULT_ENTITIES: tuple[str, ...] = (
    "PERSON",            # full names — John Smith
    "EMAIL_ADDRESS",     # any email — john@example.com
    "PHONE_NUMBER",      # any phone — +44 7700 900123, 555-1234
    "CREDIT_CARD",       # 13-19 digit card numbers, luhn-checked
    "IBAN_CODE",         # bank account numbers (international)
    "IP_ADDRESS",        # IPv4 + IPv6
    "LOCATION",          # cities, countries, addresses
    "DATE_TIME",         # dates, times — birth dates etc.
    "URL",               # full URLs — can leak internal hostnames
    "US_SSN",            # US social security numbers
    "UK_NHS",            # UK NHS numbers — 10 digits
)


# ─── pretty labels (used in responses) ─────────────────────────────
# Presidio returns codes (PERSON); humans want labels (Person Name)
ENTITY_LABELS: dict[str, str] = {
    "PERSON":        "Person Name",
    "EMAIL_ADDRESS": "Email Address",
    "PHONE_NUMBER":  "Phone Number",
    "CREDIT_CARD":   "Credit Card",
    "IBAN_CODE":     "Bank Account",
    "IP_ADDRESS":    "IP Address",
    "LOCATION":      "Location",
    "DATE_TIME":     "Date / Time",
    "URL":           "URL",
    "US_SSN":        "US SSN",
    "UK_NHS":        "UK NHS Number",
}
