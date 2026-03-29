from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
import re


ALLOWED_LICENSE_STATUSES = {
    "inactive",
    "observe_only",
    "approval_required",
    "pilot_ready",
    "active_scoped",
    "rollback_required",
    "revoked",
}
ALLOWED_PLUGIN_MODES = {
    "safe_mode",
    "observe_only",
    "approval_required",
    "active_scoped",
}
ALLOWED_SCOPE_PREFIXES = ("homepage_only", "template:", "hook:", "feature:", "page_type:")
FORBIDDEN_SCOPE_PATTERNS = ("*", "..", "global", "sitewide", "all-pages", "all-sites")
_DOMAIN_PATTERN = re.compile(r"^[a-z0-9.-]+$")


@dataclass(slots=True)
class ChannelLoadResult:
    channels: dict[str, dict[str, Any]]
    source: str
    path: Path | None
    issues: tuple[str, ...] = ()


@dataclass(slots=True)
class PluginModeDecision:
    mode: str
    reasons: tuple[str, ...]


@dataclass(slots=True)
class DomainRuntimeProfile:
    bound_domain: str
    allowed_subdomains: tuple[str, ...]
    allowed_scopes: tuple[str, ...]
    release_channel: str
    policy_channel: str
    rollback_profile_id: str
    status: str


DEFAULT_RELEASE_CHANNELS: dict[str, dict[str, Any]] = {
    "stable": {
        "requires_explicit_approval": True,
        "allows_active_scoped": True,
        "rollback_target": "rollback",
    },
    "pilot": {
        "requires_explicit_approval": True,
        "allows_active_scoped": True,
        "rollback_target": "rollback",
    },
    "rollback": {
        "requires_explicit_approval": True,
        "allows_active_scoped": False,
        "rollback_target": "rollback",
    },
}


def release_channels_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "release-channels.json"


def load_release_channels(workspace_root: Path) -> ChannelLoadResult:
    path = release_channels_path(workspace_root)
    if not path.exists():
        return ChannelLoadResult(
            channels=json.loads(json.dumps(DEFAULT_RELEASE_CHANNELS)),
            source="builtin_default",
            path=None,
            issues=("Workspace release-channels config missing; builtin default is active.",),
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return ChannelLoadResult(
            channels=json.loads(json.dumps(DEFAULT_RELEASE_CHANNELS)),
            source="invalid_workspace_channels_fallback",
            path=path,
            issues=(f"Workspace release-channels config is invalid JSON: {error}",),
        )

    channels = payload.get("channels", {})
    if not isinstance(channels, dict):
        return ChannelLoadResult(
            channels=json.loads(json.dumps(DEFAULT_RELEASE_CHANNELS)),
            source="invalid_workspace_channels_fallback",
            path=path,
            issues=("Workspace release-channels config must contain an object 'channels'.",),
        )
    return ChannelLoadResult(channels=channels, source="workspace_file", path=path)


def validate_release_channels(channels: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    required = {"stable", "pilot", "rollback"}
    missing = required - set(channels)
    if missing:
        issues.append(f"missing required release channels: {sorted(missing)}")

    for name, payload in channels.items():
        if not isinstance(payload, dict):
            issues.append(f"channel '{name}' must be an object")
            continue
        for key in ("requires_explicit_approval", "allows_active_scoped", "rollback_target"):
            if key not in payload:
                issues.append(f"channel '{name}' missing '{key}'")
        rollback_target = str(payload.get("rollback_target", "")).strip()
        if rollback_target and rollback_target not in channels and rollback_target != name:
            issues.append(f"channel '{name}' rollback_target '{rollback_target}' is unknown")
    return issues


def channel_allows_active_scoped(channel_name: str, channels: dict[str, dict[str, Any]]) -> bool:
    payload = channels.get(channel_name, {})
    return bool(payload.get("allows_active_scoped", False))


def normalize_domain(domain: str) -> str:
    normalized = domain.strip().lower()
    if normalized.startswith("http://") or normalized.startswith("https://"):
        normalized = normalized.split("://", 1)[1]
    normalized = normalized.strip("/")
    return normalized


def validate_domain_name(domain: str) -> list[str]:
    issues: list[str] = []
    normalized = normalize_domain(domain)
    if not normalized:
        return ["domain must not be empty"]
    if "/" in normalized:
        issues.append("domain must not include a path")
    if not _DOMAIN_PATTERN.match(normalized):
        issues.append(f"domain '{domain}' contains unsupported characters")
    if "." not in normalized:
        issues.append(f"domain '{domain}' must contain at least one dot")
    return issues


def validate_scope_value(scope: str) -> list[str]:
    issues: list[str] = []
    normalized = scope.strip()
    if not normalized:
        return ["scope must not be empty"]
    lower_scope = normalized.lower()
    for pattern in FORBIDDEN_SCOPE_PATTERNS:
        if pattern in lower_scope:
            issues.append(f"scope contains forbidden pattern '{pattern}'")
    if normalized == "homepage_only":
        return issues
    if not any(normalized.startswith(prefix) for prefix in ALLOWED_SCOPE_PREFIXES[1:]):
        issues.append(f"scope '{scope}' is not recognized")
    return issues


def validate_domain_binding(binding: dict[str, Any], channels: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    required = (
        "bound_domain",
        "allowed_subdomains",
        "allowed_scopes",
        "release_channel",
        "policy_channel",
        "rollback_profile_id",
    )
    for key in required:
        if key not in binding:
            issues.append(f"domain binding missing '{key}'")

    bound_domain = str(binding.get("bound_domain", "")).strip()
    issues.extend(validate_domain_name(bound_domain))

    allowed_subdomains = binding.get("allowed_subdomains", [])
    if not isinstance(allowed_subdomains, list):
        issues.append("allowed_subdomains must be a list")
    else:
        for item in allowed_subdomains:
            if validate_domain_name(str(item)):
                issues.append(f"allowed_subdomain '{item}' is invalid")

    allowed_scopes = binding.get("allowed_scopes", [])
    if not isinstance(allowed_scopes, list) or not allowed_scopes:
        issues.append("allowed_scopes must be a non-empty list")
    else:
        for item in allowed_scopes:
            issues.extend(validate_scope_value(str(item)))

    release_channel = str(binding.get("release_channel", "")).strip()
    if release_channel not in channels:
        issues.append(f"release_channel '{release_channel}' is invalid")

    policy_channel = str(binding.get("policy_channel", "")).strip()
    if policy_channel not in channels:
        issues.append(f"policy_channel '{policy_channel}' is invalid")

    if not str(binding.get("rollback_profile_id", "")).strip():
        issues.append("rollback_profile_id must be set")

    return issues


def validate_license_object(license_object: dict[str, Any], channels: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    required = (
        "license_id",
        "customer_id",
        "product_id",
        "status",
        "domain_binding",
        "allowed_features",
        "issued_at",
        "non_expiring",
    )
    for key in required:
        if key not in license_object:
            issues.append(f"license object missing '{key}'")

    if str(license_object.get("status", "")).strip() not in ALLOWED_LICENSE_STATUSES:
        issues.append(f"license status '{license_object.get('status', '')}' is invalid")

    domain_binding = license_object.get("domain_binding", {})
    if not isinstance(domain_binding, dict):
        issues.append("domain_binding must be an object")
    else:
        issues.extend(validate_domain_binding(domain_binding, channels))

    allowed_features = license_object.get("allowed_features", [])
    if not isinstance(allowed_features, list):
        issues.append("allowed_features must be a list")

    if not bool(license_object.get("non_expiring", False)) and not str(license_object.get("expires_at", "")).strip():
        issues.append("expires_at must be set when non_expiring is false")

    return issues


def build_domain_runtime_profile(
    license_object: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> tuple[DomainRuntimeProfile | None, tuple[str, ...]]:
    issues = validate_license_object(license_object, channels)
    if issues:
        return None, tuple(issues)

    binding = license_object["domain_binding"]
    profile = DomainRuntimeProfile(
        bound_domain=normalize_domain(str(binding["bound_domain"])),
        allowed_subdomains=tuple(normalize_domain(str(item)) for item in binding["allowed_subdomains"]),
        allowed_scopes=tuple(str(item).strip() for item in binding["allowed_scopes"]),
        release_channel=str(binding["release_channel"]).strip(),
        policy_channel=str(binding["policy_channel"]).strip(),
        rollback_profile_id=str(binding["rollback_profile_id"]).strip(),
        status=str(license_object["status"]).strip(),
    )
    return profile, ()


def validate_update_manifest(manifest: dict[str, Any], channels: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    required = (
        "product_id",
        "plugin_version",
        "release_channel",
        "license_id",
        "bound_domain",
        "package_url",
        "package_checksum",
        "policy_version",
        "rollback_version",
        "allowed_scopes",
        "required_features",
        "conflict_blocklist_version",
        "min_plugin_version",
        "issued_at",
    )
    for key in required:
        if key not in manifest:
            issues.append(f"update manifest missing '{key}'")

    issues.extend(validate_domain_name(str(manifest.get("bound_domain", ""))))
    if str(manifest.get("release_channel", "")).strip() not in channels:
        issues.append(f"manifest release_channel '{manifest.get('release_channel', '')}' is invalid")

    allowed_scopes = manifest.get("allowed_scopes", [])
    if not isinstance(allowed_scopes, list) or not allowed_scopes:
        issues.append("manifest allowed_scopes must be a non-empty list")
    else:
        for item in allowed_scopes:
            issues.extend(validate_scope_value(str(item)))
    return issues


def domain_matches(current_domain: str, bound_domain: str, allowed_subdomains: list[str]) -> bool:
    current = normalize_domain(current_domain)
    bound = normalize_domain(bound_domain)
    if current == bound:
        return True
    normalized_subdomains = {normalize_domain(item) for item in allowed_subdomains}
    return current in normalized_subdomains


def evaluate_local_plugin_mode(
    license_object: dict[str, Any],
    current_domain: str,
    channels: dict[str, dict[str, Any]],
    *,
    known_conflicts: bool,
    source_mapping_confirmed: bool,
    scope_confirmed: bool,
) -> PluginModeDecision:
    profile, issues = build_domain_runtime_profile(license_object, channels)
    if issues:
        return PluginModeDecision("safe_mode", issues)

    assert profile is not None
    if not domain_matches(current_domain, profile.bound_domain, list(profile.allowed_subdomains)):
        return PluginModeDecision("observe_only", ("current domain does not match bound_domain",))
    if known_conflicts:
        return PluginModeDecision("safe_mode", ("known theme/builder/SEO conflict detected",))
    if not source_mapping_confirmed or not scope_confirmed:
        return PluginModeDecision("approval_required", ("source mapping or scope is not fully confirmed",))
    if profile.status in {"inactive", "revoked"}:
        return PluginModeDecision(
            "observe_only",
            (f"license status '{profile.status}' does not allow active mode",),
        )
    if not channel_allows_active_scoped(profile.release_channel, channels):
        return PluginModeDecision(
            "observe_only",
            (f"release_channel '{profile.release_channel}' does not allow active_scoped",),
        )
    if profile.status in {"observe_only", "approval_required", "pilot_ready", "rollback_required"}:
        return PluginModeDecision(
            "approval_required",
            (f"license status '{profile.status}' does not yet allow active_scoped",),
        )
    return PluginModeDecision("active_scoped", ("license, domain, scope, and conflict gates are satisfied",))
