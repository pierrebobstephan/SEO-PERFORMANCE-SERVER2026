from __future__ import annotations

from electri_city_ops.config import AppConfig
from electri_city_ops.models import ActionPlan


def apply_actions(config: AppConfig, actions: list[ActionPlan]) -> list[ActionPlan]:
    applied: list[ActionPlan] = []
    for action in actions:
        status = action.status
        if action.scope != "workspace":
            status = "awaiting_approval"
        elif config.mode == "observe_only":
            status = "skipped_observe_only"
        elif config.mode == "plan_only":
            status = "planned_only"
        else:
            status = "ready_internal"

        applied.append(
            ActionPlan(
                identifier=action.identifier,
                phase="apply",
                scope=action.scope,
                status=status,
                description=action.description,
                target=action.target,
                risk=action.risk,
                reversible=action.reversible,
                requires_approval=action.requires_approval,
                rollback=action.rollback,
                validation=action.validation,
                metadata=action.metadata,
            )
        )
    return applied

