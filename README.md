# ShadowWatch — Personal Data Exposure Monitor

ShadowWatch is a self-hosted privacy auditing app. It combines account authentication, email breach lookups, public username checks, DNS email-authentication checks, a Chrome extension permission inventory, evidence-based scoring, remediation guidance, and JSON audit exports.

## What is real vs. demo data?

- **Email breaches:** Email lookups use the XposedOrNot free community API. No API key is required. The free endpoint is limited to 25 checks/hour and 100/day per IP; rate limits and upstream failures are reported as errors, never as clean results.
- **Username OSINT:** Performs best-effort public profile HTTP checks. Some platforms block automated checks or use soft-404 pages; results are indicative, not proof of identity or absence.
- **Domain audit:** Resolves public DNS TXT/MX records for SPF, DMARC, DKIM (common selectors), and MX; probes SMTP STARTTLS on up to two MX hosts. An unreachable MX host is reported as unverified, not automatically called insecure. DKIM absence across common selectors is not proof that no DKIM selector exists.
- **Browser extension:** Reads enabled installed extension metadata and declared permissions locally. It does not inspect browsing history, page content, cookies, keystrokes, or live activity. It syncs only after the user supplies an access token.
- **AI advice:** Gemini 3.8 Flash through Google's Interactions API is optional. Structured JSON output is validated against a strict Pydantic schema. Without a key or if generation/validation fails, deterministic recommendations are generated from stored scan evidence.
- **Privacy score:** A transparent heuristic based on the latest scan for each target. It is an educational indicator, not a certified security rating.

## Requirements

- Python 3.11+
- Node.js 20.19+ or 22.12+
- npm
- Optional: PostgreSQL and a Gemini API key (XposedOrNot email breach checks need no key)

## Run locally (Windows PowerShell)

### 1. Backend

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

The API runs at `http://127.0.0.1:8000`; interactive docs: `http://127.0.0.1:8000/docs`.

SQLite is the default and creates `backend/shadowwatch.db`. For PostgreSQL, set `DATABASE_URL` in `.env` to `postgresql+asyncpg://user:password@localhost:5432/shadowwatch`.

### 2. Frontend (new terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to the backend.

### 3. Optional API keys

Edit `backend/.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

Breach lookups cannot tell whether a mailbox actually exists. By default the backend verifies deliverability with a free SMTP probe (no API key, no email sent). If your network blocks outbound port 25, you can use a paid provider instead:

```env
EMAIL_VERIFICATION_PROVIDER=abstract   # abstract, hunter, or zerobounce
EMAIL_VERIFICATION_API_KEY=your_provider_api_key
```

When verification cannot complete (blocked port, catch-all server, timeout), the app still performs the breach lookup and marks email existence as unverified rather than guessing. Restart the backend after changing environment values. Never commit `.env` or share API keys.

## Chrome extension

1. Start the backend and sign into ShadowWatch.
2. Open `chrome://extensions` and enable **Developer mode**.
3. Click **Load unpacked** and select the `extension/` folder.
4. Open the ShadowWatch extension popup, enter the local backend URL and a ShadowWatch access token, then run the audit.
5. Review the Browser Permissions section in the app.

The extension uses `management` permission to enumerate extension metadata. Only install it from source you trust. Its token is stored in extension local storage for convenience; remove it on shared machines.

## Tests

```powershell
cd backend
python -m pytest -q
```

## API overview

- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`
- `POST /api/v1/scans/email-breach`
- `POST /api/v1/footprint/username-scan`
- `POST /api/v1/footprint/domain-audit`
- `POST /api/v1/permissions/report`
- `GET /api/v1/intelligence/score`
- `GET /api/v1/intelligence/recommendations`
- `GET /api/v1/reports/export`
- `GET /api/v1/dashboard/overview`

## Security notes before deployment

Change `SECRET_KEY` to a long random value, use HTTPS, configure exact CORS origins, keep API keys server-side, use PostgreSQL with backups, and review token storage/rotation policy before exposing the service publicly. The local development setup is not a production deployment template.


### Removed module

Password exposure checking has been removed from the user interface, API, scoring model, and scan history. Existing historical `password_check` records, if present in an older database, are ignored by dashboard scoring and hidden from scan history; they are not deleted automatically.
