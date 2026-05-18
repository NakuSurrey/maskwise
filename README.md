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