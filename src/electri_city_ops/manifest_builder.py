from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .product_core import validate_scope_value, validate_update_manifest
from .registry import (
    RegistryValidationResult,
    validate_license_registry_entry,
    validate_policy_registry_entry,
)
from .rollback_registry import validate_rollback_profile_entry


@dataclass(slots=True)
class ManifestBuildResult:
    valid: bool
    issues: tuple[str, ...]
    manifest: dict[str, Any] | None


def validate_manifest_build_request(
    request: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = (
        "license_id",
        "policy_registry_id",
        "rollback_registry_id",
        "requested_channel",
        "plugin_version",
        "package_basename",
        "min_plugin_version",
        "conflict_blocklist_version",
        "issued_at",
    )
    for key in required:
        if key not in request:
            issues.append(f"manifest build request missing '{key}'")

    channel = str(request.get("requested_channel", "")).strip()
    if channel not in channels:
        issues.append(f"requested_channel '{channel}' is invalid")

    return RegistryValidationResult(not issues, tuple(issues))


def build_update_manifest_preview(
    request: dict[str, Any],
    license_entry: dict[str, Any],
    policy_entry: dict[str, Any],
    rollback_entry: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> ManifestBuildResult:
    issues: list[str] = []

    request_result = validate_manifest_build_request(request, channels)
    issues.extend(list(request_result.issues))

    license_result = validate_license_registry_entry(license_entry, channels)
    issues.extend(list(license_result.issues))

    license_object = license_entry.get("license", {})
    if isinstance(license_object, dict):
        policy_result = validate_policy_registry_entry(policy_entry, channels, license_object)
    else:
        policy_result = RegistryValidationResult(False, ("license registry entry is malformed",))
    issues.extend(list(policy_result.issues))

    rollback_result = validate_rollback_profile_entry(rollback_entry, channels)
    issues.extend(list(rollback_result.issues))

    if str(license_entry.get("binding_state", "")).strip() != "confirmed":
        issues.append("license registry entry must be confirmed before manifest build")
    if str(policy_entry.get("registry_state", "")).strip() != "confirmed":
        issues.append("policy registry entry must be confirmed before manifest build")
    if str(rollback_entry.get("registry_state", "")).strip() != "confirmed":
        issues.append("rollback registry entry must be confirmed before manifest build")

    if issues:
        return ManifestBuildResult(False, tuple(issues), None)

    domain_binding = license_object["domain_binding"]
    requested_channel = str(request["requested_channel"]).strip()
    if requested_channel != str(domain_binding["release_channel"]).strip():
        return ManifestBuildResult(
            False,
            ("requested_channel does not match license release_channel",),
            None,
        )

    if requested_channel != str(policy_entry["release_channel"]).strip():
        return ManifestBuildResult(
            False,
            ("requested_channel does not match policy release_channel",),
            None,
        )

    rollback_profile = rollback_entry["profile"]
    if str(rollback_profile["rollback_profile_id"]).strip() != str(domain_binding["rollback_profile_id"]).strip():
        return ManifestBuildResult(
            False,
            ("rollback profile id does not match license rollback_profile_id",),
            None,
        )

    manifest = {
        "product_id": str(license_object["product_id"]).strip(),
        "plugin_version": str(request["plugin_version"]).strip(),
        "release_channel": requested_channel,
        "license_id": str(license_object["license_id"]).strip(),
        "bound_domain": str(domain_binding["bound_domain"]).strip(),
        "package_url": f"local://{request['package_basename']}",
        "package_checksum": "source not yet confirmed",
        "policy_version": str(policy_entry["policy_version"]).strip(),
        "rollback_version": str(rollback_profile["rollback_profile_id"]).strip(),
        "allowed_scopes": [str(item).strip() for item in policy_entry["allowed_scopes"]],
        "required_features": [str(item).strip() for item in license_object["allowed_features"]],
        "conflict_blocklist_version": str(request["conflict_blocklist_version"]).strip(),
        "min_plugin_version": str(request["min_plugin_version"]).strip(),
        "issued_at": str(request["issued_at"]).strip(),
    }

    manifest_issues = validate_update_manifest(manifest, channels)
    if manifest_issues:
        return ManifestBuildResult(False, tuple(manifest_issues), None)

    return ManifestBuildResult(True, (), manifest)


def build_plugin_package_metadata(
    plugin_root: Path,
    *,
    plugin_slug: str,
    plugin_version: str,
    release_channel: str,
    built_at: str,
) -> dict[str, Any]:
    files = sorted(path for path in plugin_root.rglob("*") if path.is_file())
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(plugin_root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())

    return {
        "plugin_slug": plugin_slug,
        "plugin_version": plugin_version,
        "release_channel": release_channel,
        "package_basename": f"{plugin_slug}-{plugin_version}",
        "package_filename": f"{plugin_slug}-{plugin_version}.zip",
        "package_sha256": digest.hexdigest(),
        "file_count": len(files),
        "build_mode": "local_preview_only",
        "built_at": built_at,
    }


def validate_plugin_package_metadata(
    metadata: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = (
        "plugin_slug",
        "plugin_version",
        "release_channel",
        "package_basename",
        "package_filename",
        "package_sha256",
        "file_count",
        "build_mode",
        "built_at",
    )
    for key in required:
        if key not in metadata:
            issues.append(f"plugin package metadata missing '{key}'")

    if str(metadata.get("release_channel", "")).strip() not in channels:
        issues.append(f"package release_channel '{metadata.get('release_channel', '')}' is invalid")
    if int(metadata.get("file_count", 0)) <= 0:
        issues.append("file_count must be greater than zero")
    if str(metadata.get("build_mode", "")).strip() != "local_preview_only":
        issues.append("build_mode must remain 'local_preview_only'")
    return RegistryValidationResult(not issues, tuple(issues))


def validate_domain_entitlement(
    entitlement: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> RegistryValidationResult:
    issues: list[str] = []
    required = (
        "entitlement_id",
        "license_id",
        "bound_domain",
        "release_channel",
        "allowed_package_version",
        "allowed_scopes",
        "approval_state",
        "issued_at",
    )
    for key in required:
        if key not in entitlement:
            issues.append(f"domain entitlement missing '{key}'")

    if str(entitlement.get("release_channel", "")).strip() not in channels:
        issues.append(f"entitlement release_channel '{entitlement.get('release_channel', '')}' is invalid")
    for scope in entitlement.get("allowed_scopes", []):
        issues.extend(validate_scope_value(str(scope)))
    if str(entitlement.get("approval_state", "")).strip() not in {"approval_required", "confirmed", "blocked"}:
        issues.append("approval_state must be 'approval_required', 'confirmed', or 'blocked'")
    return RegistryValidationResult(not issues, tuple(issues))


def build_release_artifact(
    package_metadata: dict[str, Any],
    manifest: dict[str, Any],
    entitlement: dict[str, Any],
    channels: dict[str, dict[str, Any]],
    *,
    artifact_id: str,
    built_at: str,
) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    issues: list[str] = []
    issues.extend(list(validate_plugin_package_metadata(package_metadata, channels).issues))
    issues.extend(validate_update_manifest(manifest, channels))
    issues.extend(list(validate_domain_entitlement(entitlement, channels).issues))

    if str(package_metadata.get("plugin_version", "")).strip() != str(manifest.get("plugin_version", "")).strip():
        issues.append("package metadata plugin_version does not match manifest plugin_version")
    if str(package_metadata.get("release_channel", "")).strip() != str(manifest.get("release_channel", "")).strip():
        issues.append("package metadata release_channel does not match manifest release_channel")
    if str(entitlement.get("release_channel", "")).strip() != str(manifest.get("release_channel", "")).strip():
        issues.append("entitlement release_channel does not match manifest release_channel")
    if str(entitlement.get("license_id", "")).strip() != str(manifest.get("license_id", "")).strip():
        issues.append("entitlement license_id does not match manifest license_id")
    if str(entitlement.get("bound_domain", "")).strip().lower() != str(manifest.get("bound_domain", "")).strip().lower():
        issues.append("entitlement bound_domain does not match manifest bound_domain")

    if issues:
        return None, tuple(issues)

    artifact = {
        "artifact_id": artifact_id,
        "plugin_slug": str(package_metadata["plugin_slug"]).strip(),
        "plugin_version": str(package_metadata["plugin_version"]).strip(),
        "release_channel": str(package_metadata["release_channel"]).strip(),
        "package_metadata": package_metadata,
        "manifest": manifest,
        "entitlement": entitlement,
        "build_mode": "local_preview_only",
        "built_at": built_at,
    }
    return artifact, ()
