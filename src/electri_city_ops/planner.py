from __future__ import annotations

from electri_city_ops.config import AppConfig
from electri_city_ops.models import ActionPlan, Finding


def plan_actions(config: AppConfig, findings: list[Finding]) -> list[ActionPlan]:
    plans: list[ActionPlan] = []

    for finding in findings[:10]:
        scope = "workspace" if finding.source == "audit" and finding.category == "config" else "external_target"
        requires_approval = scope != "workspace" or finding.severity in {"high", "critical"}
        description = finding.recommendation
        status = "planned"
        if config.mode == "observe_only":
            status = "observe_only"
        elif config.mode == "plan_only":
            status = "planned"

        plans.append(
            ActionPlan(
                identifier=f"action-{finding.fingerprint[:12]}",
                phase="plan",
                scope=scope,
                status=status,
                description=description,
                target=finding.target,
                risk=finding.risk,
                reversible=True,
                requires_approval=requires_approval,
                rollback="No change applied. Revert by leaving the external system untouched or undoing a future approved patch.",
                validation="Compare before/after findings and response metrics in the next validated cycle.",
                metadata={
                    "source_finding": finding.fingerprint,
                    "priority_score": finding.priority_score,
                },
            )
        )
    return plans

