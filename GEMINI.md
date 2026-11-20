# ShadowWatch — Project Context

ShadowWatch is a security-first personal data exposure monitor. It includes account authentication, email breach checks, username OSINT, DNS/domain security auditing, a browser extension permission audit, evidence-based privacy scoring, and optional Gemini-powered recommendations.

## External data sources
- Email breach lookups use the XposedOrNot public `GET /v1/check-email/{email}` endpoint. No API key is required. The free community quota is 25 checks/hour and 100/day per IP.
- XposedOrNot's free email endpoint returns breach names only; do not invent dates, domains, record counts, or exposed data classes.
- A 404/no-match response is a clean result; 429 and upstream/network failures must be surfaced as unavailable, never converted to a clean result.
- Gemini is optional and requires `GEMINI_API_KEY`; rule-based recommendations remain available without it.

## Development
Backend: `backend/`; frontend: `frontend/`; Chrome extension: `extension/`. No XposedOrNot key is required for email breach checks.
