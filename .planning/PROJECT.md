# ShadowWatch Project

ShadowWatch is a personal data exposure monitoring platform covering email breach exposure, public username footprint, domain email security, and browser extension permissions. It stores scan evidence and calculates an explainable privacy score.

## Implemented integrations
- Email breach checks: XposedOrNot public community API, no key required.
- Optional AI remediation: Gemini API via `GEMINI_API_KEY`, with rule-based fallback.

## Important constraints
- XposedOrNot's free email endpoint is rate-limited (25/hour, 100/day per IP). Handle HTTP 429 distinctly.
- The email check endpoint returns breach names only. Do not fabricate dates, domains, record counts, or exposed data classes.
- Upstream errors must not be represented as a clean result.
