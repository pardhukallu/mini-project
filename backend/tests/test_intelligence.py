import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_permissions_score_and_recommendations(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "intelligence@shadowwatch.io", "password": "Intelligence123!", "full_name": "Test"
    })
    headers = {"Authorization": f"Bearer {reg.json()['tokens']['access_token']}"}
    report = await client.post("/api/v1/permissions/report", headers=headers, json={
        "source": "chrome_extension", "extensions": [
            {"name": "Unknown Extension", "permissions": ["cookies", "<all_urls>"], "risk_level": "high", "reason": "Sensitive access"}
        ], "sites": []
    })
    assert report.status_code == 200
    assert report.json()["high_risk"] == 1
    score = await client.get("/api/v1/intelligence/score", headers=headers)
    assert score.status_code == 200
    assert score.json()["privacy_score"] < 100
    advice = await client.get("/api/v1/intelligence/recommendations", headers=headers)
    assert advice.status_code == 200
    assert advice.json()["items"]
    assert advice.json()["provider"] in ["rules", "rules_fallback", "gemini"]

@pytest.mark.asyncio
async def test_report_export_is_user_scoped(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "report@shadowwatch.io", "password": "ReportPassword123!", "full_name": "Test"
    })
    headers = {"Authorization": f"Bearer {reg.json()['tokens']['access_token']}"}
    response = await client.get("/api/v1/reports/export", headers=headers)
    assert response.status_code == 200
    assert response.json()["product"] == "ShadowWatch"
    assert response.json()["scans"] == []


def test_recommendation_schema_rejects_malformed_gemini_output():
    from pydantic import ValidationError
    from app.schemas.intelligence import RecommendationResponse
    with pytest.raises(ValidationError):
        RecommendationResponse.model_validate({"items": [{"priority": "urgent", "title": "Bad", "reason": "No valid priority", "steps": ["Do it"], "unexpected": True}]})
