# MaskWise

Production PII masking service for LLMs — detects and redacts personal data before submission to ChatGPT, Claude, and Gemini.

> ⚠️ Under active development. Phase 0 (Foundation Setup) — building the deployment pipeline. Full feature set lands in Phase 1+.

## What This Will Do

- **Text PII masking** — paste text, get masked output, copy to your LLM.
- **Image PII masking** — upload screenshots, faces blurred + text redacted.
- **Chrome extension** — auto-mask PII before sending to ChatGPT, Claude, Gemini.
- **Verifiable erasure** — your session expires from memory after 1 hour. Public stats dashboard proves it.

## Why This Exists

People paste sensitive data into LLMs every day. Real names, real emails, real API keys, real customer information. The LLM provider then has it. MaskWise sits between the user and the LLM, replacing PII with placeholders before submission.

## Project Status

| Phase | Status |
|-------|--------|
| Phase 0 — Foundation Setup | 🟡 In progress |
| Phase 1 — Text PII MVP | ⚪ Not started |
| Phase 2 — Fine-tuned DeBERTa + monitoring | ⚪ Not started |
| Phase 3 — Image PII | ⚪ Not started |
| Phase 4 — Chrome extension | ⚪ Not started |
| Phase 5 — Polish + launch | ⚪ Not started |

Full README (architecture, tech stack, deploy guide, learnings) lands in Phase 5.

## Privacy By Design

- Raw user input lives in exactly one place: Redis, with a 1-hour TTL.
- Forbidden in logs, postgres, error traces, metrics, filesystem.
- Open-source — every line of code is auditable.

## License

MIT — see [LICENSE](./LICENSE).
