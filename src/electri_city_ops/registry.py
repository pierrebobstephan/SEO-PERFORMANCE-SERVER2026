from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .contracts import validate_plugin_policy_response
from .product_core import validate_license_object


REGISTRY_STATES = {"pending", "confirmed", "blocked", "approval_required"}
SITE_ROLES = {"reference_site", "customer_site"}
DEFAULT_BACKEND_DEFAULTS: dict[str, Any] = {
    "registry_states": sorted(REGISTRY_STATES),
    "site_roles": sorted(SITE_ROLES),
    "default_release_channel": "pilot",
    "default_policy_mode": "observe_only",
    "required_live_gates": [
        "license_registry_confirmed",
        "policy_registry_confirmed",
        "rollback_registry_confirmed",
        "onboarding_confirmed",
        "operator_approval_confirmed",
        "validation_defined",
        "rollback_defined",
        "source_mapping_confirmed",
    ],
}


@dataclass(slots=True)
class RegistryValidationResult:
    valid: bool
    issues: tuple[str, ...]


def backend_defaults_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "backend-defaults.json"


def load_backend_defaults(workspace_root: Path) -> dict[str, Any]:
    path = backend_defaults_path(workspace_root)
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_BACKEND_DEFAULTS))
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry_state(state: str) -> list[str]:
    if state not in REGISTRY_STATES:
        return [f"registry_state '{state}' is invalid"]
    return []


def validate_license_registry_entry(
    entry: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = ("registry_id", "license", "binding_state", "source_role", "created_at")
    for key in required:
        if key not in entry:
            issues.append(f"license registry entry missing '{key}'")

    license_object = entry.get("license", {})
    if not isinstance(license_object, dict):
        issues.append("license registry entry license must be an object")
    else:
        issues.extend(validate_license_object(license_object, channels))

    issues.extend(validate_registry_state(str(entry.get("binding_state", "")).strip()))

    source_role = str(entry.get("source_role", "")).strip()
    if source_role not in SITE_ROLES:
        issues.append(f"source_role '{source_role}' is invalid")

    return RegistryValidationResult(not issues, tuple(issues))


def extract_license_identity(entry: dict[str, Any]) -> tuple[str, str]:
    license_object = entry.get("license", {})
    domain_binding = license_object.get("domain_binding", {}) if isinstance(license_object, dict) else {}
    return (
        str(license_object.get("license_id", "")).strip(),
        str(domain_binding.get("bound_domain", "")).strip().lower(),
    )


def prevent_duplicate_license_or_domain(
    existing_entries: list[dict[str, Any]],
    new_entry: dict[str, Any],
) -> RegistryValidationResult:
    issues: list[str] = []
    new_registry_id = str(new_entry.get("registry_id", "")).strip()
    new_license_id, new_bound_domain = extract_license_identity(new_entry)

    for entry in existing_entries:
        registry_id = str(entry.get("registry_id", "")).strip()
        if registry_id == new_registry_id:
            continue

        license_id, bound_domain = extract_license_identity(entry)
        if new_license_id and license_id == new_license_id:
            issues.append(f"duplicate license_id '{new_license_id}' is not allowed")
        if new_bound_domain and bound_domain == new_bound_domain:
            issues.append(f"duplicate bound_domain '{new_bound_domain}' is not allowed")

    return RegistryValidationResult(not issues, tuple(issues))


def policy_scopes_are_narrowed(
    policy_entry: dict[str, Any],
    license_object: dict[str, Any],
) -> RegistryValidationResult:
    allowed_scopes = set(str(item).strip() for item in license_object["domain_binding"]["allowed_scopes"])
    policy_scopes = set(str(item).strip() for item in policy_entry.get("allowed_scopes", []))
    if policy_scopes.issubset(allowed_scopes):
        return RegistryValidationResult(True, ())
    return RegistryValidationResult(
        False,
        ("policy allowed_scopes exceed license allowed_scopes",),
    )


def validate_policy_registry_entry(
    entry: dict[str, Any],
    channels: dict[str, dict[str, Any]],
    license_object: dict[str, Any] | None = None,
) -> RegistryValidationResult:
    issues: list[str] = []
    required = (
        "registry_id",
        "license_id",
        "bound_domain",
        "release_channel",
        "policy_version",
        "default_mode",
        "allowed_scopes",
        "module_flags",
        "registry_state",
        "created_at",
    )
    for key in required:
        if key not in entry:
            issues.append(f"policy registry entry missing '{key}'")

    policy_result = validate_plugin_policy_response(
        {
            "license_id": entry.get("license_id", ""),
            "bound_domain": entry.get("bound_domain", ""),
            "release_channel": entry.get("release_channel", ""),
            "policy_version": entry.get("policy_version", ""),
            "default_mode": entry.get("default_mode", ""),
            "allowed_scopes": entry.get("allowed_scopes", []),
            "module_flags": entry.get("module_flags", {}),
            "rollback_profile_id": entry.get("rollback_profile_id", "TBD"),
            "issued_at": entry.get("created_at", ""),
        },
        channels,
    )
    issues.extend(list(policy_result.issues))
    issues.extend(validate_registry_state(str(entry.get("registry_state", "")).strip()))

    if license_object is not None:
        license_id = str(license_object.get("license_id", "")).strip()
        bound_domain = str(license_object.get("domain_binding", {}).get("bound_domain", "")).strip().lower()
        if str(entry.get("license_id", "")).strip() != license_id:
            issues.append("policy license_id does not match linked license")
        if str(entry.get("bound_domain", "")).strip().lower() != bound_domain:
            issues.append("policy bound_domain does not match linked license")
        scope_result = policy_scopes_are_narrowed(entry, license_object)
        issues.extend(list(scope_result.issues))

    return RegistryValidationResult(not issues, tuple(issues))
