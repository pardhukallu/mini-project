"""
OSINT username presence scanner — Phase 3
Performs HTTP HEAD requests to public profile URLs across major platforms.
No authentication required; presence is inferred from HTTP status codes.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any

import httpx

from app.schemas.footprint import PlatformPresence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Platform definitions
# Each entry: (display_name, url_template)
# Profile presence: 200 → found, 404 → not found, anything else → unknown
# ---------------------------------------------------------------------------
PLATFORMS: list[tuple[str, str]] = [
    ("GitHub",          "https://github.com/{username}"),
    ("Reddit",          "https://www.reddit.com/user/{username}"),
    ("Twitter / X",     "https://x.com/{username}"),
    ("Instagram",       "https://www.instagram.com/{username}/"),
    ("LinkedIn",        "https://www.linkedin.com/in/{username}/"),
    ("HackerNews",      "https://news.ycombinator.com/user?id={username}"),
    ("Dev.to",          "https://dev.to/{username}"),
    ("Medium",          "https://medium.com/@{username}"),
    ("Keybase",         "https://keybase.io/{username}"),
    ("GitLab",          "https://gitlab.com/{username}"),
]

# Platforms known to always return 200 regardless of existence (soft-404)
_SOFT_404_PLATFORMS: set[str] = {"LinkedIn", "Instagram", "Twitter / X"}

# Request timeout per platform
_TIMEOUT_S = 6.0

# Headers to mimic a real browser (avoid bot blocks on some platforms)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


async def _check_platform(
    client: httpx.AsyncClient,
    platform: str,
    url: str,
) -> PlatformPresence:
    """Check one platform and return a PlatformPresence result."""
    try:
        resp = await client.head(url, follow_redirects=True, timeout=_TIMEOUT_S)
        status = resp.status_code

        if platform in _SOFT_404_PLATFORMS:
            return PlatformPresence(platform=platform, url=url, present=False, verified=False,
                status_code=status, note="Cannot verify reliably — platform uses bot protection or soft-404 responses")
        if status == 200:
            return PlatformPresence(platform=platform, url=url, present=True, verified=True,
                status_code=status, note="Public profile page returned HTTP 200; confirm it belongs to you")
        if status == 404:
            return PlatformPresence(platform=platform, url=url, present=False, verified=True,
                status_code=status, note="No public profile page returned (HTTP 404)")
        return PlatformPresence(platform=platform, url=url, present=False, verified=False,
            status_code=status, note=f"Unverified response (HTTP {status}); platform may block automated checks")

    except httpx.TimeoutException:
        return PlatformPresence(
            platform=platform, url=url, present=False, verified=False,
            note="Request timed out — unable to verify",
        )
    except httpx.RequestError as exc:
        logger.warning("OSINT request error for %s: %s", platform, exc)
        return PlatformPresence(
            platform=platform, url=url, present=False, verified=False,
            note="Network error — unable to verify",
        )


async def scan_username(username: str) -> list[PlatformPresence]:
    """
    Concurrently check username across all defined platforms.
    Returns a list of PlatformPresence results.
    """
    targets = [
        (name, tmpl.format(username=username))
        for name, tmpl in PLATFORMS
    ]

    async with httpx.AsyncClient(headers=_HEADERS) as client:
        tasks = [
            _check_platform(client, name, url)
            for name, url in targets
        ]
        results: list[PlatformPresence] = await asyncio.gather(*tasks)

    return results
