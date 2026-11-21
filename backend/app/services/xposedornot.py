"""XposedOrNot public email-breach lookup integration."""
from typing import Any
from urllib.parse import quote

import httpx

BASE_URL = "https://api.xposedornot.com"


def _extract_breach_names(payload: Any) -> list[dict[str, str]]:
    """Return only breach names explicitly present in the API response."""
    if not isinstance(payload, dict):
        raise ValueError("Unexpected XposedOrNot response format")

    if payload.get("Error") == "Not found" and payload.get("email") is None:
        return []

    groups = payload.get("breaches")
    if groups is None:
        raise ValueError("XposedOrNot response did not include breach records")

    if not isinstance(groups, list):
        raise ValueError("Unexpected XposedOrNot breach response format")

    names: list[str] = []
    for group in groups:
        candidates = group if isinstance(group, list) else [group]
        for item in candidates:
            if isinstance(item, str) and item.strip():
                names.append(item.strip())

    # Deduplicate without adding any metadata not returned by XposedOrNot.
    return [{"name": name} for name in dict.fromkeys(names)]


async def check_email_breaches(email: str) -> tuple[list[dict[str, str]], str]:
    clean_email = email.strip().lower()
    url = f"{BASE_URL}/v1/check-email/{quote(clean_email, safe='@.+-_')}"

    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        response = await client.get(
            url,
            headers={"Accept": "application/json", "User-Agent": "ShadowWatch/1.0"},
        )

    if response.status_code == 404:
        return [], "xposedornot_api"
    if response.status_code == 429:
        raise httpx.HTTPStatusError(
            "XposedOrNot rate limit reached", request=response.request, response=response
        )
    response.raise_for_status()

    try:
        payload = response.json()
    except ValueError as exc:
        raise ValueError("Invalid JSON returned by XposedOrNot") from exc

    return _extract_breach_names(payload), "xposedornot_api"
