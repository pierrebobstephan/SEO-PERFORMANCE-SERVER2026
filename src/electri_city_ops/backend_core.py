from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .registry import load_backend_defaults


CONTROL_PLANE_STATES = {"observe_only", "blueprint_ready", "approval_required", "blocked"}


@dataclass(slots=True)
class BackendStateSummary:
    state: str
    reasons: tuple[str, ...]


def derive_backend_state(
    license_state: str,
    policy_state: str,
    rollback_state: str,
    onboarding_state: str,
) -> BackendStateSummary:
    states = {license_state, policy_state, rollback_state, onboarding_state}
    if "blocked" in states:
        return BackendStateSummary("blocked", ("at least one backend registry object is blocked",))
    if "pending" in states:
        return BackendStateSummary("observe_only", ("at least one backend registry object is still pending",))
    if "approval_required" in states:
        return BackendStateSummary("approval_required", ("operator approval is still required",))
    if states == {"confirmed"}:
        return BackendStateSummary(
            "approval_required",
            ("all registry objects are confirmed, but real backend effects remain approval_required",),
        )
    return BackendStateSummary("blueprint_ready", ("backend state is locally modeled",))


def validate_live_productization_gates(
    gates: dict[str, bool],
    *,
    workspace_root: Path,
) -> tuple[bool, tuple[str, ...]]:
    defaults = load_backend_defaults(workspace_root)
    required = [str(item) for item in defaults.get("required_live_gates", [])]
    missing = [name for name in required if not bool(gates.get(name, False))]
    if missing:
        return False, tuple(f"live productization gate '{name}' is not green" for name in missing)
    return True, ()
