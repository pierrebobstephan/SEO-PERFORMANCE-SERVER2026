from __future__ import annotations

from electri_city_ops.models import Finding


SEVERITY_WEIGHT = {
    "critical": 40,
    "high": 28,
    "warning": 16,
    "info": 8,
}

RISK_WEIGHT = {
    "high": 6,
    "medium": 4,
    "low": 2,
}


def prioritize_findings(findings: list[Finding], recurrence_map: dict[str, int]) -> list[Finding]:
    prioritized: list[Finding] = []
    for finding in findings:
        recurrence_bonus = min(recurrence_map.get(finding.fingerprint, 0), 10) * 2
        score = (
            SEVERITY_WEIGHT.get(finding.severity, 0)
            + RISK_WEIGHT.get(finding.risk, 0)
            + round(finding.confidence * 10)
            + recurrence_bonus
        )
        finding.priority_score = float(score)
        prioritized.append(finding)
    return sorted(prioritized, key=lambda item: item.priority_score, reverse=True)

