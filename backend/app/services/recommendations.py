"""Evidence-led remediation. Gemini is optional; deterministic guidance always works."""
import json
import httpx
from app.core.config import settings
from app.schemas.intelligence import RecommendationResponse


def rule_recommendations(score: dict) -> list[dict]:
    items = []
    for finding in score.get("evidence", []):
        category = finding["category"]
        if category == "Email breaches":
            services = finding.get("services", [])
            data_classes = finding.get("data_classes", [])
            service_text = ", ".join(services[:5]) if services else "the affected services"
            title = f"Secure accounts exposed in {service_text}"
            steps = [
                "Change the passwords on affected services and anywhere those credentials were reused.",
                "Enable multi-factor authentication, preferably with an authenticator or passkey.",
                "Review recent sign-ins and revoke sessions you do not recognize.",
            ]
            if any("password" in value.lower() for value in data_classes):
                steps.insert(0, "Prioritize changing credentials because the breach included password data.")
        elif category == "Public profiles":
            platforms = finding.get("platforms", [])
            platform_text = ", ".join(platforms[:5]) if platforms else "the discovered platforms"
            title = f"Review public profiles on {platform_text}"
            steps = [
                "Open each discovered profile and confirm it belongs to you.",
                "Remove personal details you do not intend to publish.",
                "Use separate usernames where cross-site correlation is a concern.",
            ]
        elif category == "Domain email security":
            title = "Strengthen domain email authentication"
            steps = [
                "Publish and validate an SPF record for authorized senders.",
                "Configure DKIM signing with your mail provider.",
                "Deploy DMARC gradually, then move to quarantine or reject after reviewing reports.",
            ]
        else:
            names = finding.get("extensions", [])
            extension_text = ", ".join(names[:5]) if names else "the flagged extensions"
            title = f"Review permissions for {extension_text}"
            steps = [
                "Review the named extension in chrome://extensions.",
                "Remove extensions you do not recognize or no longer use.",
                "Disable optional site access and sensitive permissions where possible.",
            ]
        reason = finding["detail"]
        if category == "Email breaches" and finding.get("data_classes"):
            reason += ". Exposed data classes: " + ", ".join(finding["data_classes"][:8])
        if category == "Domain email security" and finding.get("records"):
            reason += ". Records needing attention: " + ", ".join(finding["records"])
        items.append({"priority": "high" if finding["penalty"] >= 15 else "medium", "title": title, "reason": reason, "steps": steps})
    if not items:
        items.append({"priority": "low", "title": "Maintain your current security posture", "reason": "No recorded high-risk findings were found in the latest verified scans.", "steps": ["Use unique passwords and a password manager.", "Keep multi-factor authentication enabled.", "Repeat your audits periodically."]})
    return items


async def generate_recommendations(score: dict) -> dict:
    fallback = rule_recommendations(score)
    if not settings.GEMINI_API_KEY:
        return {"provider": "rules", "items": fallback, "notice": "Gemini is not configured; recommendations are generated from recorded findings."}

    response_schema = {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
            "title": {"type": "string"}, "reason": {"type": "string"},
            "steps": {"type": "array", "items": {"type": "string"}},
        }, "required": ["priority", "title", "reason", "steps"]}}},
        "required": ["items"],
    }
    prompt = (
        "Generate concise remediation recommendations based ONLY on the evidence below. "
        "Do not invent breaches, platforms, affected accounts, or configurations. "
        "If there is no evidence, return one low-priority maintenance recommendation. Evidence: "
        + json.dumps(score.get("evidence", []), ensure_ascii=False)
    )
    try:
        # Interactions API is Google's current recommended path for new Gemini integrations.
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/interactions",
                headers={"x-goog-api-key": settings.GEMINI_API_KEY, "Content-Type": "application/json"},
                json={"model": "gemini-3.8-flash", "input": prompt,
                      "response_format": {"type": "text", "mime_type": "application/json", "schema": response_schema}},
            )
            response.raise_for_status()
            payload = response.json()
            raw = payload.get("output_text")
            if not raw:
                text_parts = [part.get("text", "") for step in payload.get("steps", [])
                              if step.get("type") == "model_output"
                              for part in step.get("content", []) if part.get("type") == "text"]
                raw = "\n".join(text_parts)
            validated = RecommendationResponse.model_validate_json(raw)
            return {"provider": "gemini", "items": [item.model_dump() for item in validated.items], "notice": "Recommendations generated from your recorded scan evidence and validated against the response schema."}
    except Exception:
        return {"provider": "rules_fallback", "items": fallback, "notice": "Gemini was unavailable or returned invalid structured output; evidence-based rules were used instead."}
