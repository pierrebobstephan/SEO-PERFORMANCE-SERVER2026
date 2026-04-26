from __future__ import annotations

import json
from pathlib import Path
from typing import Any


AI_SYSTEM_REGISTER_SCHEMA_VERSION = 1
AI_IMPACT_ASSESSMENT_SCHEMA_VERSION = 1
PROVENANCE_EVIDENCE_SCHEMA_VERSION = 1
SUPPLY_CHAIN_EVIDENCE_SCHEMA_VERSION = 1
REQUIRED_SECRET_IGNORE_PATTERNS = (
    "deploy/systemd/*.env",
    "deploy/systemd/*.env.save",
    "!deploy/systemd/*.env.example",
)
SENSITIVE_ENV_KEY_MARKERS = (
    "SECRET",
    "PASSWORD",
    "API_KEY",
    "TOKEN",
    "CLIENT_ID",
    "WEBHOOK_ID",
    "PRIVATE_KEY",
)
PLACEHOLDER_SECRET_VALUES = {
    "",
    "replace_me",
    "changeme",
    "operator_input_required",
    "approval_required",
}

EXPECTED_AI_SYSTEM_IDS = (
    "suite_runtime_core",
    "wordpress_bridge_plugin",
    "public_portal_surface",
    "protected_paypal_webhook_receiver",
    "protected_fulfillment_chain",
)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalized for item in value if (normalized := str(item).strip())]


def _is_sensitive_env_key(key: str) -> bool:
    normalized = key.strip().upper()
    return any(marker in normalized for marker in SENSITIVE_ENV_KEY_MARKERS)


def _is_placeholder_secret_value(value: str) -> bool:
    normalized = value.strip()
    lower = normalized.lower()
    return (
        lower in PLACEHOLDER_SECRET_VALUES
        or lower.startswith("replace-with-")
        or lower.startswith("set-via-")
        or lower.startswith("env-ref:")
    )


def _read_gitignore_lines(workspace_root: Path) -> set[str]:
    path = workspace_root.resolve() / ".gitignore"
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def validate_secret_hygiene(workspace_root: Path) -> list[str]:
    workspace_root = workspace_root.resolve()
    issues: list[str] = []

    gitignore_lines = _read_gitignore_lines(workspace_root)
    for pattern in REQUIRED_SECRET_IGNORE_PATTERNS:
        if pattern not in gitignore_lines:
            issues.append(f"secret hygiene missing .gitignore pattern '{pattern}'")

    deploy_systemd = workspace_root / "deploy" / "systemd"
    if not deploy_systemd.exists():
        return issues

    candidate_paths = sorted(deploy_systemd.glob("*.env")) + sorted(deploy_systemd.glob("*.env.save"))
    for path in candidate_paths:
        if path.name.endswith(".env.example"):
            continue
        relative = path.relative_to(workspace_root)
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if _is_sensitive_env_key(key) and not _is_placeholder_secret_value(value):
                issues.append(f"secret hygiene {relative}:{line_number} contains a non-placeholder value for {key.strip()}")

    return issues


def ai_system_register_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "ai-system-register.json"


def ai_impact_assessments_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "ai-impact-assessments.json"


def provenance_evidence_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "provenance-evidence.json"


def supply_chain_evidence_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "supply-chain-evidence.json"


def load_ai_system_register(workspace_root: Path) -> dict[str, Any]:
    return _read_json(ai_system_register_path(workspace_root))


def load_ai_impact_assessments(workspace_root: Path) -> dict[str, Any]:
    return _read_json(ai_impact_assessments_path(workspace_root))


def load_provenance_evidence(workspace_root: Path) -> dict[str, Any]:
    return _read_json(provenance_evidence_path(workspace_root))


def load_supply_chain_evidence(workspace_root: Path) -> dict[str, Any]:
    return _read_json(supply_chain_evidence_path(workspace_root))


def _system_map(register_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    systems = register_payload.get("systems", [])
    if not isinstance(systems, list):
        return {}
    mapping: dict[str, dict[str, Any]] = {}
    for item in systems:
        if not isinstance(item, dict):
            continue
        system_id = str(item.get("system_id", "")).strip()
        if system_id:
            mapping[system_id] = item
    return mapping


def validate_ai_system_register(payload: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["AI system register must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != AI_SYSTEM_REGISTER_SCHEMA_VERSION:
        issues.append(f"AI system register schema_version must be {AI_SYSTEM_REGISTER_SCHEMA_VERSION}")

    if str(payload.get("doctrine_version", "")).strip() != str(policy.get("policy_version", "")).strip():
        issues.append("AI system register doctrine_version must match doctrine policy_version")

    systems = payload.get("systems")
    if not isinstance(systems, list) or not systems:
        return issues + ["AI system register systems must be a non-empty list"]

    allowed_risk_classes = {
        str(item).strip() for item in policy.get("ai_management", {}).get("risk_classes", []) if str(item).strip()
    }
    allowed_gate_states = {
        str(item).strip() for item in policy.get("gates", {}).get("allowed_states", []) if str(item).strip()
    }
    seen_ids: set[str] = set()
    for index, item in enumerate(systems):
        if not isinstance(item, dict):
            issues.append(f"AI system register entry {index} must be an object")
            continue
        system_id = str(item.get("system_id", "")).strip()
        label = system_id or f"index {index}"
        for field in (
            "system_id",
            "system_name",
            "version",
            "owner",
            "validator",
            "operator",
            "auditor",
            "purpose",
            "scope",
            "jurisdiction",
            "risk_class",
            "impact_assessment_ref",
            "fallback_state",
            "kill_switch",
            "rollback_path",
        ):
            if not str(item.get(field, "")).strip():
                issues.append(f"AI system register {label} missing {field}")
        if system_id in seen_ids:
            issues.append(f"AI system register duplicate system_id '{system_id}'")
        seen_ids.add(system_id)
        risk_class = str(item.get("risk_class", "")).strip()
        if risk_class not in allowed_risk_classes:
            issues.append(f"AI system register {label} risk_class is invalid")
        fallback_state = str(item.get("fallback_state", "")).strip()
        if fallback_state not in allowed_gate_states:
            issues.append(f"AI system register {label} fallback_state is invalid")
        if not isinstance(item.get("customer_near"), bool):
            issues.append(f"AI system register {label} customer_near must be boolean")
        if not isinstance(item.get("external_effects_possible"), bool):
            issues.append(f"AI system register {label} external_effects_possible must be boolean")
        if not _as_string_list(item.get("data_classes")):
            issues.append(f"AI system register {label} data_classes must be a non-empty list")
        if not _as_string_list(item.get("monitor_signals")):
            issues.append(f"AI system register {label} monitor_signals must be a non-empty list")
        if not isinstance(item.get("external_write_paths", []), list):
            issues.append(f"AI system register {label} external_write_paths must be a list")
        layer_governance = item.get("layer_governance")
        if not isinstance(layer_governance, dict):
            issues.append(f"AI system register {label} layer_governance must be an object")
        else:
            for field in ("model", "policy", "prompt", "memory", "tool", "agent"):
                if not str(layer_governance.get(field, "")).strip():
                    issues.append(f"AI system register {label} layer_governance.{field} must be set")

    missing_system_ids = [system_id for system_id in EXPECTED_AI_SYSTEM_IDS if system_id not in seen_ids]
    for system_id in missing_system_ids:
        issues.append(f"AI system register missing required system '{system_id}'")
    return issues


def validate_ai_impact_assessments(
    payload: dict[str, Any], register_payload: dict[str, Any], policy: dict[str, Any]
) -> list[str]:
    if not isinstance(payload, dict):
        return ["AI impact assessments must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != AI_IMPACT_ASSESSMENT_SCHEMA_VERSION:
        issues.append(f"AI impact assessments schema_version must be {AI_IMPACT_ASSESSMENT_SCHEMA_VERSION}")

    if str(payload.get("doctrine_version", "")).strip() != str(policy.get("policy_version", "")).strip():
        issues.append("AI impact assessments doctrine_version must match doctrine policy_version")

    assessments = payload.get("assessments")
    if not isinstance(assessments, list) or not assessments:
        return issues + ["AI impact assessments assessments must be a non-empty list"]

    registered_systems = _system_map(register_payload)
    seen_system_ids: set[str] = set()
    for index, item in enumerate(assessments):
        if not isinstance(item, dict):
            issues.append(f"AI impact assessment entry {index} must be an object")
            continue
        assessment_id = str(item.get("assessment_id", "")).strip()
        system_id = str(item.get("system_id", "")).strip()
        label = assessment_id or system_id or f"index {index}"
        for field in (
            "assessment_id",
            "system_id",
            "risk_class",
            "status",
            "summary",
            "human_oversight_state",
            "rollback_reference",
            "monitoring_reference",
            "review_cycle",
        ):
            if not str(item.get(field, "")).strip():
                issues.append(f"AI impact assessment {label} missing {field}")
        if str(item.get("status", "")).strip() not in {"completed", "completed_local_blueprint"}:
            issues.append(f"AI impact assessment {label} status is invalid")
        if not _as_string_list(item.get("primary_harms")):
            issues.append(f"AI impact assessment {label} primary_harms must be a non-empty list")
        if not _as_string_list(item.get("mitigation_controls")):
            issues.append(f"AI impact assessment {label} mitigation_controls must be a non-empty list")
        if system_id not in registered_systems:
            issues.append(f"AI impact assessment {label} references unknown system_id '{system_id}'")
        elif str(item.get("risk_class", "")).strip() != str(registered_systems[system_id].get("risk_class", "")).strip():
            issues.append(f"AI impact assessment {label} risk_class does not match AI system register")
        seen_system_ids.add(system_id)

    for system_id in EXPECTED_AI_SYSTEM_IDS:
        if system_id not in seen_system_ids:
            issues.append(f"AI impact assessments missing required assessment for '{system_id}'")
    return issues


def validate_provenance_evidence(payload: dict[str, Any], register_payload: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["provenance evidence must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != PROVENANCE_EVIDENCE_SCHEMA_VERSION:
        issues.append(f"provenance evidence schema_version must be {PROVENANCE_EVIDENCE_SCHEMA_VERSION}")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return issues + ["provenance evidence entries must be a non-empty list"]

    registered_systems = _system_map(register_payload)
    seen_system_ids: set[str] = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            issues.append(f"provenance evidence entry {index} must be an object")
            continue
        system_id = str(item.get("system_id", "")).strip()
        label = system_id or f"index {index}"
        for field in (
            "system_id",
            "source_provenance_class",
            "evidence_confidence",
            "freshness_status",
            "human_review_status",
            "synthetic_data_ratio",
            "rights_status",
            "operational_trust_class",
        ):
            if not str(item.get(field, "")).strip():
                issues.append(f"provenance evidence {label} missing {field}")
        if system_id not in registered_systems:
            issues.append(f"provenance evidence {label} references unknown system_id '{system_id}'")
        seen_system_ids.add(system_id)

    for system_id in EXPECTED_AI_SYSTEM_IDS:
        if system_id not in seen_system_ids:
            issues.append(f"provenance evidence missing required entry for '{system_id}'")
    return issues


def validate_supply_chain_evidence(payload: dict[str, Any], register_payload: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["supply chain evidence must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != SUPPLY_CHAIN_EVIDENCE_SCHEMA_VERSION:
        issues.append(f"supply chain evidence schema_version must be {SUPPLY_CHAIN_EVIDENCE_SCHEMA_VERSION}")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        return issues + ["supply chain evidence entries must be a non-empty list"]

    registered_systems = _system_map(register_payload)
    seen_system_ids: set[str] = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            issues.append(f"supply chain evidence entry {index} must be an object")
            continue
        system_id = str(item.get("system_id", "")).strip()
        label = system_id or f"index {index}"
        for field in (
            "system_id",
            "dependency_verification_state",
            "build_provenance_state",
            "signing_state",
            "secret_handling_state",
            "delivery_state",
            "review_state",
        ):
            if not str(item.get(field, "")).strip():
                issues.append(f"supply chain evidence {label} missing {field}")
        if system_id not in registered_systems:
            issues.append(f"supply chain evidence {label} references unknown system_id '{system_id}'")
        seen_system_ids.add(system_id)

    for system_id in EXPECTED_AI_SYSTEM_IDS:
        if system_id not in seen_system_ids:
            issues.append(f"supply chain evidence missing required entry for '{system_id}'")
    return issues


def collect_ai_governance_status(workspace_root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    workspace_root = workspace_root.resolve()
    register_payload = load_ai_system_register(workspace_root)
    impact_payload = load_ai_impact_assessments(workspace_root)
    provenance_payload = load_provenance_evidence(workspace_root)
    supply_chain_payload = load_supply_chain_evidence(workspace_root)

    issues: list[str] = []
    register_issues = validate_ai_system_register(register_payload, policy)
    impact_issues = validate_ai_impact_assessments(impact_payload, register_payload, policy)
    provenance_issues = validate_provenance_evidence(provenance_payload, register_payload)
    supply_chain_issues = validate_supply_chain_evidence(supply_chain_payload, register_payload)
    secret_hygiene_issues = validate_secret_hygiene(workspace_root)
    for group in (register_issues, impact_issues, provenance_issues, supply_chain_issues, secret_hygiene_issues):
        for item in group:
            normalized = str(item).strip()
            if normalized:
                issues.append(normalized)

    systems = register_payload.get("systems", []) if isinstance(register_payload.get("systems"), list) else []
    risk_distribution: dict[str, int] = {}
    for item in systems:
        if not isinstance(item, dict):
            continue
        risk_class = str(item.get("risk_class", "")).strip()
        if risk_class:
            risk_distribution[risk_class] = risk_distribution.get(risk_class, 0) + 1

    status = "blueprint_ready" if not issues else "blocked"
    return {
        "status": status,
        "paths": {
            "system_register": str(ai_system_register_path(workspace_root).relative_to(workspace_root)),
            "impact_assessments": str(ai_impact_assessments_path(workspace_root).relative_to(workspace_root)),
            "provenance_evidence": str(provenance_evidence_path(workspace_root).relative_to(workspace_root)),
            "supply_chain_evidence": str(supply_chain_evidence_path(workspace_root).relative_to(workspace_root)),
            "secret_hygiene": str((workspace_root / ".gitignore").relative_to(workspace_root)),
        },
        "system_register_entry_count": len(systems),
        "impact_assessment_count": len(
            impact_payload.get("assessments", []) if isinstance(impact_payload.get("assessments"), list) else []
        ),
        "provenance_entry_count": len(
            provenance_payload.get("entries", []) if isinstance(provenance_payload.get("entries"), list) else []
        ),
        "supply_chain_entry_count": len(
            supply_chain_payload.get("entries", []) if isinstance(supply_chain_payload.get("entries"), list) else []
        ),
        "risk_distribution": risk_distribution,
        "required_system_ids": list(EXPECTED_AI_SYSTEM_IDS),
        "issues": issues,
        "register_issues": register_issues,
        "impact_assessment_issues": impact_issues,
        "provenance_issues": provenance_issues,
        "supply_chain_issues": supply_chain_issues,
        "secret_hygiene_issues": secret_hygiene_issues,
    }
