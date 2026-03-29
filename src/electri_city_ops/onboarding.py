from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import validate_customer_domain_onboarding
from .registry import RegistryValidationResult, validate_registry_state


ONBOARDING_TRANSITIONS = {
    "pending": {"approval_required", "confirmed", "blocked"},
    "approval_required": {"confirmed", "blocked"},
    "confirmed": {"approval_required", "blocked"},
    "blocked": {"approval_required"},
}


@dataclass(slots=True)
class OnboardingTransitionResult:
    valid: bool
    issues: tuple[str, ...]
    entry: dict[str, Any] | None


def validate_domain_onboarding_entry(
    entry: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = ("onboarding_id", "onboarding", "state", "created_at")
    for key in required:
        if key not in entry:
            issues.append(f"domain onboarding entry missing '{key}'")

    onboarding = entry.get("onboarding", {})
    if not isinstance(onboarding, dict):
        issues.append("domain onboarding entry onboarding must be an object")
    else:
        onboarding_result = validate_customer_domain_onboarding(onboarding, channels)
        issues.extend(list(onboarding_result.issues))

    issues.extend(validate_registry_state(str(entry.get("state", "")).strip()))
    return RegistryValidationResult(not issues, tuple(issues))


def transition_onboarding_state(
    entry: dict[str, Any],
    target_state: str,
) -> OnboardingTransitionResult:
    current_state = str(entry.get("state", "")).strip()
    allowed = ONBOARDING_TRANSITIONS.get(current_state, set())
    if target_state not in allowed:
        return OnboardingTransitionResult(
            False,
            (f"transition '{current_state}' -> '{target_state}' is not allowed",),
            None,
        )

    updated = dict(entry)
    updated["state"] = target_state
    return OnboardingTransitionResult(True, (), updated)


def validate_dry_run_onboarding_constraints(entry: dict[str, Any]) -> RegistryValidationResult:
    issues: list[str] = []
    state = str(entry.get("state", "")).strip()
    if state not in {"pending", "approval_required", "confirmed"}:
        issues.append(f"dry-run onboarding state '{state}' is not allowed")

    onboarding = entry.get("onboarding", {})
    if not isinstance(onboarding, dict):
        issues.append("dry-run onboarding requires an onboarding object")
    else:
        if str(onboarding.get("cms_platform", "")).strip() != "wordpress":
            issues.append("dry-run onboarding only supports wordpress")
        if not str(onboarding.get("requested_domain", "")).strip():
            issues.append("dry-run onboarding requires requested_domain")

    return RegistryValidationResult(not issues, tuple(issues))
