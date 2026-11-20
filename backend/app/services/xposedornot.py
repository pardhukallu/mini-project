"""XposedOrNot free community API integration (no API key required).

Email checks return breach names from the public check-email endpoint.
"""
from typing import Any
from urllib.parse import quote
import httpx

BASE_URL = "https://api.xposedornot.com"


def _breach_record(name: str) -> dict[str, Any]:
    # The free check-email endpoint returns breach names, not full breach metadata.
    # Keep unavailable fields explicitly empty rather than inventing details.
    return {
        "name": name,
        "title": name,
        "domain": "",
        "breach_date": "",
        "added_date": None,
        "pwn_count": 0,
        "description": "Breach name reported by XposedOrNot. Detailed metadata was not included in the free email-check response.",
        "logo_path": None,
        "data_classes": [],
        "is_verified": True,
        "is_sensitive": False,
    }


async def check_email_breaches(email: str) -> tuple[list[dict[str, Any]], str]:
    clean_email = email.strip().lower()
    url = f"{BASE_URL}/v1/check-email/{quote(clean_email, safe='@.+-_')}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers={"Accept": "application/json", "User-Agent": "ShadowWatch/1.0"})
    if response.status_code == 404:
        return [], "xposedornot_api"
    if response.status_code == 429:
        raise httpx.HTTPStatusError("XposedOrNot rate limit reached. Try again later.", request=response.request, response=response)
    response.raise_for_status()
    payload = response.json()
    if payload.get("Error") == "Not found":
        return [], "xposedornot_api"
    names: list[str] = []
    for group in payload.get("breaches", []) or []:
        if isinstance(group, list):
            names.extend(str(item) for item in group if item)
        elif isinstance(group, str) and group:
            names.append(group)
    # Preserve order while removing duplicates.
    unique_names = list(dict.fromkeys(names))
    return [_breach_record(name) for name in unique_names], "xposedornot_api"

