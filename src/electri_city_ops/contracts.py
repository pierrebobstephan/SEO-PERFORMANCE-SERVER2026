from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .product_core import (
    build_domain_runtime_profile,
    channel_allows_active_scoped,
    evaluate_local_plugin_mode,
    validate_domain_name,
    validate_scope_value,
)


@dataclass(slots=True)
class ContractValidationResult:
    valid: bool
    issues: tuple[str, ...]


@dataclass(slots=True)
class HandshakeDecision:
    mode: str
    channel: str
    reasons: tuple[str, ...]
    allowed_scopes: tuple[str, ...]
    rollback_profile_id: str | None
    policy_version: str | None


def validate_license_check_response(
    response: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> ContractValidationResult:
    issues: list[str] = []
    required = ("response_status", "signature_status", "license", "issued_at")
    for key in required:
        if key not in response:
            issues.append(f"license response missing '{key}'")

    if str(response.get("response_status", "")).strip() != "ok":
        issues.append("license response_status must be 'ok'")

    if str(response.get("signature_status", "")).strip() not in {"trusted", "untrusted"}:
        issues.append("signature_status must be 'trusted' or 'untrusted'")

    license_object = response.get("license", {})
    if not isinstance(license_object, dict):
        issues.append("license must be an object")
    else:
        _, license_issues = build_domain_runtime_profile(license_object, channels)
        issues.extend(list(license_issues))

    return ContractValidationResult(not issues, tuple(issues))


def validate_plugin_policy_response(
    response: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> ContractValidationResult:
    issues: list[str] = []
    required = (
        "license_id",
        "bound_domain",
        "release_channel",
        "policy_version",
        "default_mode",
        "allowed_scopes",
        "module_flags",
        "rollback_profile_id",
        "issued_at",
    )
    for key in required:
        if key not in response:
            issues.append(f"policy response missing '{key}'")

    issues.extend(validate_domain_name(str(response.get("bound_domain", ""))))

    release_channel = str(response.get("release_channel", "")).strip()
    if release_channel not in channels:
        issues.append(f"policy release_channel '{release_channel}' is invalid")

    default_mode = str(response.get("default_mode", "")).strip()
    if default_mode not in {"safe_mode", "observe_only", "approval_required", "active_scoped"}:
        issues.append(f"policy default_mode '{default_mode}' is invalid")

    allowed_scopes = response.get("allowed_scopes", [])
    if not isinstance(allowed_scopes, list) or not allowed_scopes:
        issues.append("policy allowed_scopes must be a non-empty list")
    else:
        for scope in allowed_scopes:
            issues.extend(validate_scope_value(str(scope)))

    if not isinstance(response.get("module_flags", {}), dict):
        issues.append("policy module_flags must be an object")

    if not str(response.get("rollback_profile_id", "")).strip():
        issues.append("policy rollback_profile_id must be set")

    return ContractValidationResult(not issues, tuple(issues))


def validate_rollback_profile(
    profile: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> ContractValidationResult:
    issues: list[str] = []
    required = (
        "rollback_profile_id",
        "bound_domain",
        "release_channel",
        "rollback_channel",
        "rollback_steps",
        "verification_checks",
        "abort_triggers",
        "issued_at",
    )
    for key in required:
        if key not in profile:
            issues.append(f"rollback profile missing '{key}'")

    issues.extend(validate_domain_name(str(profile.get("bound_domain", ""))))

    release_channel = str(profile.get("release_channel", "")).strip()
    rollback_channel = str(profile.get("rollback_channel", "")).strip()
    if release_channel not in channels:
        issues.append(f"rollback profile release_channel '{release_channel}' is invalid")
    if rollback_channel not in channels:
        issues.append(f"rollback profile rollback_channel '{rollback_channel}' is invalid")

    for key in ("rollback_steps", "verification_checks", "abort_triggers"):
        if not isinstance(profile.get(key, []), list) or not profile.get(key):
            issues.append(f"rollback profile {key} must be a non-empty list")

    return ContractValidationResult(not issues, tuple(issues))


def validate_customer_domain_onboarding(
    onboarding: dict[str, Any],
    channels: dict[str, dict[str, Any]],
) -> ContractValidationResult:
    issues: list[str] = []
    required = (
        "customer_id",
        "requested_domain",
        "requested_channel",
        "requested_scopes",
        "site_role",
        "cms_platform",
        "operator_contact_status",
    )
    for key in required:
        if key not in onboarding:
            issues.append(f"onboarding object missing '{key}'")

    issues.extend(validate_domain_name(str(onboarding.get("requested_domain", ""))))

    requested_channel = str(onboarding.get("requested_channel", "")).strip()
    if requested_channel not in channels:
        issues.append(f"requested_channel '{requested_channel}' is invalid")

    requested_scopes = onboarding.get("requested_scopes", [])
    if not isinstance(requested_scopes, list) or not requested_scopes:
        issues.append("requested_scopes must be a non-empty list")
    else:
        for scope in requested_scopes:
            issues.extend(validate_scope_value(str(scope)))

    if str(onboarding.get("site_role", "")).strip() not in {"reference_site", "customer_site"}:
        issues.append("site_role must be 'reference_site' or 'customer_site'")

    if str(onboarding.get("cms_platform", "")).strip() != "wordpress":
        issues.append("cms_platform must be 'wordpress'")

    return ContractValidationResult(not issues, tuple(issues))


def determine_plugin_handshake(
    current_domain: str,
    license_response: dict[str, Any] | None,
    policy_response: dict[str, Any] | None,
    rollback_profile: dict[str, Any] | None,
    channels: dict[str, dict[str, Any]],
    *,
    known_conflicts: bool,
    source_mapping_confirmed: bool,
    scope_confirmed: bool,
) -> HandshakeDecision:
    if not isinstance(license_response, dict):
        return HandshakeDecision(
            mode="observe_only",
            channel="pilot",
            reasons=("license response missing; observe_only fallback engaged",),
            allowed_scopes=(),
            rollback_profile_id=None,
            policy_version=None,
        )

    license_result = validate_license_check_response(license_response, channels)
    if not license_result.valid:
        return HandshakeDecision(
            mode="safe_mode",
            channel="pilot",
            reasons=license_result.issues,
            allowed_scopes=(),
            rollback_profile_id=None,
            policy_version=None,
        )

    license_object = license_response["license"]
    profile, _ = build_domain_runtime_profile(license_object, channels)
    assert profile is not None

    if str(license_response.get("signature_status", "")).strip() != "trusted":
        return HandshakeDecision(
            mode="safe_mode",
            channel=profile.release_channel,
            reasons=("license signature_status is not trusted",),
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=None,
        )

    base_decision = evaluate_local_plugin_mode(
        license_object,
        current_domain,
        channels,
        known_conflicts=known_conflicts,
        source_mapping_confirmed=source_mapping_confirmed,
        scope_confirmed=scope_confirmed,
    )

    if base_decision.mode != "active_scoped":
        return HandshakeDecision(
            mode=base_decision.mode,
            channel=profile.release_channel,
            reasons=base_decision.reasons,
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=None,
        )

    if not isinstance(policy_response, dict):
        return HandshakeDecision(
            mode="observe_only",
            channel=profile.release_channel,
            reasons=("policy response missing; observe_only fallback engaged",),
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=None,
        )

    policy_result = validate_plugin_policy_response(policy_response, channels)
    if not policy_result.valid:
        return HandshakeDecision(
            mode="safe_mode",
            channel=profile.release_channel,
            reasons=policy_result.issues,
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=None,
        )

    if str(policy_response["bound_domain"]).strip().lower() != profile.bound_domain:
        return HandshakeDecision(
            mode="observe_only",
            channel=profile.release_channel,
            reasons=("policy bound_domain does not match license bound_domain",),
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    if str(policy_response["release_channel"]).strip() != profile.release_channel:
        return HandshakeDecision(
            mode="approval_required",
            channel=profile.release_channel,
            reasons=("policy release_channel does not match license release_channel",),
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    scoped_policy = tuple(str(scope).strip() for scope in policy_response["allowed_scopes"])
    if not set(scoped_policy).issubset(set(profile.allowed_scopes)):
        return HandshakeDecision(
            mode="approval_required",
            channel=profile.release_channel,
            reasons=("policy allowed_scopes exceed license allowed_scopes",),
            allowed_scopes=profile.allowed_scopes,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    if not isinstance(rollback_profile, dict):
        return HandshakeDecision(
            mode="approval_required",
            channel=profile.release_channel,
            reasons=("rollback profile missing; approval remains required",),
            allowed_scopes=scoped_policy,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    rollback_result = validate_rollback_profile(rollback_profile, channels)
    if not rollback_result.valid:
        return HandshakeDecision(
            mode="safe_mode",
            channel=profile.release_channel,
            reasons=rollback_result.issues,
            allowed_scopes=scoped_policy,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    if str(rollback_profile["rollback_profile_id"]).strip() != profile.rollback_profile_id:
        return HandshakeDecision(
            mode="approval_required",
            channel=profile.release_channel,
            reasons=("rollback profile id does not match license rollback_profile_id",),
            allowed_scopes=scoped_policy,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    if not channel_allows_active_scoped(profile.release_channel, channels):
        return HandshakeDecision(
            mode="observe_only",
            channel=profile.release_channel,
            reasons=(f"release_channel '{profile.release_channel}' does not allow active_scoped",),
            allowed_scopes=scoped_policy,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    policy_mode = str(policy_response["default_mode"]).strip()
    if policy_mode != "active_scoped":
        return HandshakeDecision(
            mode=policy_mode,
            channel=profile.release_channel,
            reasons=(f"policy default_mode '{policy_mode}' prevents active_scoped",),
            allowed_scopes=scoped_policy,
            rollback_profile_id=profile.rollback_profile_id,
            policy_version=str(policy_response["policy_version"]).strip(),
        )

    return HandshakeDecision(
        mode="active_scoped",
        channel=profile.release_channel,
        reasons=("license, policy, rollback, domain, and scope checks passed",),
        allowed_scopes=scoped_policy,
        rollback_profile_id=profile.rollback_profile_id,
        policy_version=str(policy_response["policy_version"]).strip(),
    )
