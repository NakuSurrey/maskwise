# MaskWise

> **Production PII masking service for LLMs** — detects and redacts personal data before submission to ChatGPT, Claude, and Gemini.

## Live

🔒 **[https://maskwise.nakularora.tech/health](https://maskwise.nakularora.tech/health)** — `{"status":"ok"}` 200 OK

Hosted on Hetzner (Nuremberg). HTTPS via Let's Encrypt. Stub `/health` endpoint live; full PII masking lands in Phase 1.

## What It Does

- **Text PII masking** — replaces names, emails, phone numbers, API keys, NHS numbers, and 10+ other categories of personal data with safe placeholders before you paste into an LLM.
- **Verifiable erasure** — every mask session lives in memory for 1 hour, then auto-deletes. Verifiable via a public stats dashboard and per-session erasure endpoint.
- **Open-source and auditable** — every line of the detection, masking, and storage logic is readable on this repo. Nothing hidden, nothing proprietary about how the privacy promise is kept.

## The Problem

People paste sensitive data into LLMs every day. Real names, real emails, real API keys, real customer information. The LLM provider then has it. Samsung famously banned ChatGPT after engineers leaked production source code through it. A developer pasting customer data into Claude can trigger real GDPR liability for their company.

MaskWise sits between the user and the LLM, replacing real data with placeholders before it ever leaves the user's browser.

## Privacy By Design

- Raw user input lives in exactly one place: an in-memory store, with a 1-hour TTL.
- Forbidden everywhere else: logs, databases, error traces, metrics, filesystem.
- Containers bound to loopback only — no service has direct internet exposure.
- ICO-registered data controller.
- All containers run as non-root, with hard CPU and memory caps and `noexec` `/tmp` mounts.

## Using the API

Every request needs my API key in the `X-API-Key` header. Without it, the API returns `401`.

Rate limit: 60 requests per minute per IP. Over that returns `429`.

### Mask text - `POST /mask`

Send text, get it back with personal data replaced by `<TYPE>` tags.

**Request body**

```json
{
  "text": "Hi, I am John Doe and my email is john@example.com",
  "entities": ["PERSON", "EMAIL_ADDRESS"]
}
```

- `text` (required) - the text to scan. Up to 10,000 characters.
- `entities` (optional) - only look for these types. Leave it out to scan for all supported types.

**Response**

```json
{
  "masked_text": "Hi, I am <PERSON> and my email is <EMAIL_ADDRESS>",
  "entities_found": [
    { "type": "PERSON", "label": "Person", "start": 9, "end": 17, "score": 0.85 },
    { "type": "EMAIL_ADDRESS", "label": "Email Address", "start": 34, "end": 50, "score": 1.0 }
  ],
  "entities_count": 2
}
```

- `masked_text` - the input with each PII span replaced by `<TYPE>`.
- `entities_found` - every span found: type, label, position, and confidence score (0 to 1).
- `entities_count` - how many spans were masked.

**Example**

```bash
curl -X POST https://maskwise.nakularora.tech/mask \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hi, I am John Doe and my email is john@example.com"}'
```

### Detected PII types

| Type | What it is |
|------|------------|
| PERSON | names |
| EMAIL_ADDRESS | email addresses |
| PHONE_NUMBER | phone numbers (US formats) |
| CREDIT_CARD | credit card numbers |
| IBAN_CODE | bank account numbers (IBAN) |
| IP_ADDRESS | IP addresses |
| LOCATION | places, cities, countries |
| DATE_TIME | dates and times |
| URL | web links |
| US_SSN | US social security numbers |
| UK_NHS | UK NHS numbers |

## Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| PII detection | Microsoft Presidio + custom recognizers |
| Session store | Redis (in-memory, TTL-enforced) |
| Reverse proxy | Nginx |
| TLS | Let's Encrypt |
| Containerisation | Docker, Docker Compose |
| Infrastructure | Hetzner Cloud (self-managed) |

## License

MIT — see [LICENSE](./LICENSE).