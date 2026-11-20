# Project State

- Email breach provider switched to XposedOrNot public API; no API key or fixture fallback is used.
- Free XposedOrNot email checks are rate-limited to 25/hour and 100/day per IP.
- Remaining verification: run backend tests and frontend production build on Windows with installed dependencies; perform a live API smoke test.
