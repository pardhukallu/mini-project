"""Deterministic, explainable privacy scoring based on the latest evidence per target."""
from typing import Iterable
from app.models.scan import Scan


def calculate_score(scans: Iterable[Scan]) -> dict:
    latest: dict[tuple[str, str], Scan] = {}
    for scan in sorted(scans, key=lambda item: item.created_at):
        latest[(scan.scan_type, scan.target)] = scan

    penalties = {"email_breaches": 0, "footprint": 0, "domain_security": 0, "browser_permissions": 0}
    metrics = {"total_breaches": 0, "footprint_exposures": 0, "high_risk_permissions": 0, "medium_risk_permissions": 0, "verified_scans": 0}
    evidence = []
    verification_warnings = []
    for scan in latest.values():
        data = scan.findings_data or {}
        if scan.scan_type == "email_breach":
            if data.get("source") != "xposedornot_api":
                verification_warnings.append({"target": scan.target, "source": data.get("source", "unknown"), "message": "Email result is not a verified live XposedOrNot lookup."})
                continue
            metrics["verified_scans"] += 1
            count = int(data.get("breach_count", 0))
            metrics["total_breaches"] += count
            penalty = min(30, count * 8)
            penalties["email_breaches"] += penalty
            if count:
                evidence.append({"category": "Email breaches", "target": scan.target, "penalty": penalty,
                                 "detail": f"{count} breach record(s) found",
                                 "services": [item.get("name") for item in data.get("breaches", []) if item.get("name")],
                                 "data_classes": sorted({value for item in data.get("breaches", []) for value in item.get("data_classes", [])})})
        elif scan.scan_type == "username_osint":
            platform_results = data.get("results", [])
            verified_count = sum(1 for item in platform_results if item.get("verified"))
            if verified_count:
                metrics["verified_scans"] += 1
            if verified_count < len(platform_results):
                verification_warnings.append({"target": scan.target, "source": "public_http_probe", "message": f"{len(platform_results) - verified_count} platform result(s) could not be verified reliably."})
            found = int(data.get("platforms_found", 0))
            metrics["footprint_exposures"] += found
            penalty = min(15, found * 2)
            penalties["footprint"] += penalty
            if found:
                evidence.append({"category": "Public profiles", "target": scan.target, "penalty": penalty,
                                 "detail": f"{found} public profile(s) found",
                                 "platforms": [item.get("platform") for item in platform_results if item.get("present")]})
        elif scan.scan_type == "domain_audit":
            metrics["verified_scans"] += 1
            risk = data.get("overall_risk", scan.risk_level)
            penalty = {"none": 0, "low": 3, "medium": 8, "high": 15}.get(risk, 0)
            penalties["domain_security"] += penalty
            if penalty:
                evidence.append({"category": "Domain email security", "target": scan.target, "penalty": penalty,
                                 "detail": f"DNS posture: {risk}",
                                 "records": [item.get("record_type") for item in data.get("checks", []) if item.get("risk_level") in ("medium", "high")]})
        elif scan.scan_type == "permissions":
            metrics["verified_scans"] += 1
            high = len(data.get("high_risk", []))
            medium = len(data.get("medium_risk", []))
            metrics["high_risk_permissions"] += high
            metrics["medium_risk_permissions"] += medium
            penalty = min(20, high * 4 + medium)
            penalties["browser_permissions"] += penalty
            if penalty:
                evidence.append({"category": "Browser permissions", "target": "Installed extensions", "penalty": penalty,
                                 "detail": f"{high} high-risk and {medium} medium-risk permission finding(s)",
                                 "extensions": [item.get("name") for item in data.get("high_risk", []) + data.get("medium_risk", []) if item.get("name")]})

    total = min(100, sum(penalties.values()))
    return {"privacy_score": max(0, 100-total), "deductions": total, "category_penalties": penalties, "metrics": metrics, "evidence": evidence, "verification_warnings": verification_warnings}


def build_score_history(scans: Iterable[Scan]) -> list[dict]:
    ordered = sorted(scans, key=lambda item: item.created_at)
    history = []
    accumulated = []
    for scan in ordered:
        accumulated.append(scan)
        score = calculate_score(accumulated)
        history.append({"scan_id": scan.id, "created_at": scan.created_at.isoformat(), "privacy_score": score["privacy_score"], "scan_type": scan.scan_type})
    return history
