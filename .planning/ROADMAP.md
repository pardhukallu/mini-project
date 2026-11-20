# ShadowWatch Roadmap

1. Authentication and secure session management.
2. Exposure detection: XposedOrNot email breach lookup.
3. Username OSINT and domain DNS/email security.
4. Manifest V3 browser extension permission audit.
5. Evidence-based privacy scoring and scan history.
6. Gemini-assisted remediation with deterministic fallback.
7. Dashboard, exports, and end-to-end verification.

## XposedOrNot integration notes
- Email: `GET https://api.xposedornot.com/v1/check-email/{email}`; no API key. Free quota: 25/hour and 100/day per IP.
- The free email endpoint returns breach names, not full breach metadata.
- Do not present API failures or rate limits as clean results.
