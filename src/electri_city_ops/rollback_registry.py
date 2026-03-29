from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import validate_rollback_profile
from .registry import RegistryValidationResult, validate_registry_state


@dataclass(slots=True)
class RollbackLookupResult:
    found: bool
    entry: dict[str, Any] | None
    issues: tuple[str, ...]


def validate_rollback_profile_entry(
    entry: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = ("registry_id", "profile", "registry_state", "created_at")
    for key in required:
        if key not in entry:
            issues.append(f"rollback registry entry missing '{key}'")

    profile = entry.get("profile", {})
    if not isinstance(profile, dict):
        issues.append("rollback profile entry profile must be an object")
    else:
        profile_result = validate_rollback_profile(profile, channels)
        issues.extend(list(profile_result.issues))

    issues.extend(validate_registry_state(str(entry.get("registry_state", "")).strip()))
    return RegistryValidationResult(not issues, tuple(issues))


def find_rollback_profile(
    entries: list[dict[str, Any]],
    bound_domain: str,
    rollback_profile_id: str,
) -> RollbackLookupResult:
    normalized_domain = bound_domain.strip().lower()
    for entry in entries:
        profile = entry.get("profile", {})
        if not isinstance(profile, dict):
            continue
        if str(profile.get("bound_domain", "")).strip().lower() != normalized_domain:
            continue
        if str(profile.get("rollback_profile_id", "")).strip() != rollback_profile_id:
            continue
        return RollbackLookupResult(True, entry, ())
    return RollbackLookupResult(
        False,
        None,
        (f"rollback profile '{rollback_profile_id}' for '{normalized_domain}' was not found",),
    )
