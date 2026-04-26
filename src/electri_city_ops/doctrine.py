from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from electri_city_ops.models import ActionPlan, ValidationCheck


DEFAULT_DOCTRINE_POLICY: dict[str, Any] = {
    "policy_version": "8.0",
    "canonical_docs": [
        "AGENTS.md",
        "docs/system-doctrine.md",
        "Doktrin04.04.2026-Version-8.0.txt",
        "docs/doctrine-alignment-report.md",
    ],
    "defaults": {
        "fallback_gate": "observe_only",
        "approval_gate": "approval_required",
    },
    "workspace": {
        "root_only": True,
        "forbid_outside_workspace": True,
        "forbid_rocket_cloud_changes": True,
    },
    "external_effects": {
        "runtime_connector_activation": False,
        "require_approval": True,
        "blocked_targets": [
            "rocket_cloud",
            "systemd",
            "cron",
            "notification",
        ],
    },
    "gates": {
        "allowed_states": [
            "observe_only",
            "safe_mode",
            "controlled_apply",
            "containment_mode",
            "rollback_mode",
            "self_healing_active",
            "emergency_freeze",
            "adaptive_resonance_mode",
            "centaur_mode",
            "data_insufficient",
            "blueprint_ready",
            "approval_required",
            "pilot_ready",
            "active_pilot",
            "stable_applied",
            "degraded_safe",
            "blocked",
            "rollback_required",
        ],
    },
    "ai_management": {
        "system_register_required": True,
        "impact_assessment_required": True,
        "provenance_required": True,
        "supply_chain_verification_required": True,
        "human_oversight_required_for_external_effects": True,
        "risk_classes": ["R0", "R1", "R2", "R3", "R4"],
    },
    "lifecycle": {
        "required_stages": [
            "govern",
            "register",
            "classify",
            "assess",
            "design",
            "source_verify",
            "build",
            "simulate",
            "validate",
            "approve",
            "deploy",
            "monitor",
            "re_evaluate",
            "learn",
            "decommission",
            "archive_delete",
        ],
    },
    "scopes": {
        "forbidden_patterns": [
            "..",
            "*",
            "global",
            "sitewide",
            "all-paths",
            "rocket cloud",
            "rocket-cloud",
        ],
        "require_explicit_external_scope": True,
    },
    "blast_radius": {
        "allowed_values": [
            "none",
            "minimal",
            "narrow",
            "contained",
            "high",
            "global",
        ],
        "blocked_values": [
            "high",
            "global",
        ],
    },
    "simulation": {
        "required_fields": [
            "pilot_id",
            "connector_type",
            "target_scope",
            "excluded_scope",
            "baseline_window",
            "primary_metrics",
            "neighbor_signals",
            "assumed_cause",
            "expected_gain",
            "abort_conditions",
            "rollback_trigger",
            "adapt_options",
            "final_pre_apply_gate",
            "risk_class",
            "impact_assessment_ref",
            "evidence_plan",
            "aftercare_window",
        ],
    },
}


@dataclass(slots=True)
class PolicyLoadResult:
    policy: dict[str, Any]
    source: str
    path: Path | None
    notes: tuple[str, ...] = ()


@dataclass(slots=True)
class GateCheckResult:
    gate_state: str
    reasons: tuple[str, ...]
    approval_ready: bool
    rollback_ready: bool
    scope_valid: bool
    blast_radius_valid: bool


def _deep_copy_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(policy))


def doctrine_policy_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "doctrine-policy.json"


def load_doctrine_policy(workspace_root: Path) -> PolicyLoadResult:
    path = doctrine_policy_path(workspace_root)
    if not path.exists():
        return PolicyLoadResult(
            policy=_deep_copy_policy(DEFAULT_DOCTRINE_POLICY),
            source="builtin_default",
            path=None,
            notes=("Workspace policy file missing; builtin doctrine default is active.",),
        )

    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return PolicyLoadResult(
            policy=_deep_copy_policy(DEFAULT_DOCTRINE_POLICY),
            source="invalid_workspace_policy_fallback",
            path=path,
            notes=(f"Workspace doctrine policy is invalid JSON: {error}",),
        )

    return PolicyLoadResult(policy=policy, source="workspace_file", path=path)


def validate_policy_schema(policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required_top_level = (
        "policy_version",
        "canonical_docs",
        "defaults",
        "workspace",
        "external_effects",
        "gates",
        "ai_management",
        "lifecycle",
        "scopes",
        "blast_radius",
        "simulation",
    )
    for key in required_top_level:
        if key not in policy:
            issues.append(f"policy missing required key '{key}'")

    if not isinstance(policy.get("canonical_docs"), list) or not policy.get("canonical_docs"):
        issues.append("policy canonical_docs must be a non-empty list")

    defaults = policy.get("defaults", {})
    if not isinstance(defaults, dict):
        issues.append("policy defaults must be an object")
    else:
        for key in ("fallback_gate", "approval_gate"):
            if not str(defaults.get(key, "")).strip():
                issues.append(f"policy defaults.{key} must be set")

    workspace = policy.get("workspace", {})
    if not isinstance(workspace, dict):
        issues.append("policy workspace must be an object")
    else:
        for key in ("root_only", "forbid_outside_workspace", "forbid_rocket_cloud_changes"):
            if key not in workspace:
                issues.append(f"policy workspace.{key} must be set")

    external_effects = policy.get("external_effects", {})
    if not isinstance(external_effects, dict):
        issues.append("policy external_effects must be an object")
    else:
        blocked_targets = external_effects.get("blocked_targets")
        if not isinstance(blocked_targets, list):
            issues.append("policy external_effects.blocked_targets must be a list")

    gates = policy.get("gates", {})
    if not isinstance(gates, dict):
        issues.append("policy gates must be an object")
    else:
        allowed_states = gates.get("allowed_states")
        if not isinstance(allowed_states, list) or not allowed_states:
            issues.append("policy gates.allowed_states must be a non-empty list")

    ai_management = policy.get("ai_management", {})
    if not isinstance(ai_management, dict):
        issues.append("policy ai_management must be an object")
    else:
        for key in (
            "system_register_required",
            "impact_assessment_required",
            "provenance_required",
            "supply_chain_verification_required",
            "human_oversight_required_for_external_effects",
            "risk_classes",
        ):
            if key not in ai_management:
                issues.append(f"policy ai_management.{key} must be set")
        if not isinstance(ai_management.get("risk_classes"), list) or not ai_management.get("risk_classes"):
            issues.append("policy ai_management.risk_classes must be a non-empty list")

    lifecycle = policy.get("lifecycle", {})
    if not isinstance(lifecycle, dict):
        issues.append("policy lifecycle must be an object")
    else:
        required_stages = lifecycle.get("required_stages")
        if not isinstance(required_stages, list) or not required_stages:
            issues.append("policy lifecycle.required_stages must be a non-empty list")

    scopes = policy.get("scopes", {})
    if not isinstance(scopes, dict):
        issues.append("policy scopes must be an object")
    else:
        patterns = scopes.get("forbidden_patterns")
        if not isinstance(patterns, list) or not patterns:
            issues.append("policy scopes.forbidden_patterns must be a non-empty list")

    blast_radius = policy.get("blast_radius", {})
    if not isinstance(blast_radius, dict):
        issues.append("policy blast_radius must be an object")
    else:
        allowed_values = blast_radius.get("allowed_values")
        blocked_values = blast_radius.get("blocked_values")
        if not isinstance(allowed_values, list) or not allowed_values:
            issues.append("policy blast_radius.allowed_values must be a non-empty list")
        if not isinstance(blocked_values, list):
            issues.append("policy blast_radius.blocked_values must be a list")

    simulation = policy.get("simulation", {})
    if not isinstance(simulation, dict):
        issues.append("policy simulation must be an object")
    else:
        required_fields = simulation.get("required_fields")
        if not isinstance(required_fields, list) or not required_fields:
            issues.append("policy simulation.required_fields must be a non-empty list")

    return issues


def validate_scope(
    target_scope: str,
    policy: dict[str, Any],
    workspace_root: Path,
    external_effect: bool,
) -> list[str]:
    issues: list[str] = []
    normalized = target_scope.strip()
    if not normalized:
        return ["target scope must not be empty"]

    lower_scope = normalized.lower()
    forbidden_patterns = tuple(str(item).lower() for item in policy["scopes"]["forbidden_patterns"])
    for pattern in forbidden_patterns:
        if pattern in lower_scope:
            issues.append(f"target scope contains forbidden pattern '{pattern}'")

    if external_effect and policy["scopes"].get("require_explicit_external_scope", True):
        if normalized in {"external_target", "target", "default"}:
            issues.append("external target scope is not explicit enough")

    if not external_effect and normalized not in {"workspace", "workspace_internal"}:
        candidate = Path(normalized)
        resolved = candidate.resolve() if candidate.is_absolute() else (workspace_root / candidate).resolve()
        if resolved != workspace_root and workspace_root not in resolved.parents:
            issues.append("local target scope escapes workspace")

    return issues


def validate_blast_radius(blast_radius: str, policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    normalized = blast_radius.strip().lower()
    allowed_values = {str(item).lower() for item in policy["blast_radius"]["allowed_values"]}
    blocked_values = {str(item).lower() for item in policy["blast_radius"]["blocked_values"]}
    if normalized not in allowed_values:
        issues.append(f"blast radius '{blast_radius}' is not recognized")
    elif normalized in blocked_values:
        issues.append(f"blast radius '{blast_radius}' is blocked by policy")
    return issues


def validate_simulation_object(simulation: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required_fields = tuple(policy["simulation"]["required_fields"])
    for field_name in required_fields:
        value = simulation.get(field_name)
        if value in (None, "", [], {}):
            issues.append(f"simulation object missing '{field_name}'")
    return issues


def validate_ai_governance_spec(spec: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    ai_management = policy.get("ai_management", {})
    risk_class = str(spec.get("risk_class", "")).strip()
    allowed_risk_classes = {str(item).strip() for item in ai_management.get("risk_classes", [])}

    if risk_class not in allowed_risk_classes:
        issues.append("risk_class is missing or invalid")
    if ai_management.get("system_register_required", True) and not spec.get("system_registered", False):
        issues.append("AI system register entry is missing")
    if ai_management.get("impact_assessment_required", True) and not spec.get("impact_assessment_complete", False):
        issues.append("AI impact assessment is incomplete")
    if ai_management.get("provenance_required", True) and not spec.get("provenance_ready", False):
        issues.append("provenance readiness is incomplete")
    if ai_management.get("supply_chain_verification_required", True) and not spec.get("supply_chain_verified", False):
        issues.append("supply chain verification is incomplete")
    if (
        spec.get("external_effect", False)
        and ai_management.get("human_oversight_required_for_external_effects", True)
        and not spec.get("human_oversight_defined", False)
    ):
        issues.append("human oversight is not defined for external effect")

    return issues


def validate_approval_readiness(spec: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not spec.get("requires_approval", False):
        return issues
    if not spec.get("approval_granted", False):
        issues.append("required approval is not granted")
    if spec.get("external_effect", False) and not spec.get("secrets_available", False):
        issues.append("required secrets are not available")
    return issues


def validate_rollback_readiness(spec: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not spec.get("reversible", False):
        issues.append("step is not marked reversible")
    if not str(spec.get("rollback_path", "")).strip():
        issues.append("rollback path is missing")
    if not str(spec.get("rollback_trigger", "")).strip():
        issues.append("rollback trigger is missing")
    return issues


def evaluate_pilot_gate(spec: dict[str, Any], policy: dict[str, Any], workspace_root: Path) -> GateCheckResult:
    reasons: list[str] = []
    doctrine_conformant = bool(spec.get("doctrine_conformant", True))
    external_effect = bool(spec.get("external_effect", False))
    prefer_observe_only = bool(spec.get("prefer_observe_only", False))
    validation_ready = bool(spec.get("validation_ready", False))
    simulation_required = bool(spec.get("simulation_required", external_effect))
    simulation_object = spec.get("simulation_object", {})
    scope_issues = validate_scope(
        target_scope=str(spec.get("target_scope", "")),
        policy=policy,
        workspace_root=workspace_root,
        external_effect=external_effect,
    )
    blast_radius_issues = validate_blast_radius(str(spec.get("blast_radius", "")), policy)
    rollback_issues = validate_rollback_readiness(spec)
    approval_issues = validate_approval_readiness(spec)
    simulation_issues = validate_simulation_object(simulation_object, policy) if simulation_required else []
    ai_governance_issues = validate_ai_governance_spec(spec, policy)

    if not doctrine_conformant:
        reasons.append("step is not doctrine-conformant")
    reasons.extend(scope_issues)
    reasons.extend(blast_radius_issues)
    reasons.extend(rollback_issues)
    reasons.extend(ai_governance_issues)

    if not doctrine_conformant or scope_issues or blast_radius_issues or rollback_issues or ai_governance_issues:
        if approval_issues:
            reasons.extend(approval_issues)
        if simulation_issues:
            reasons.extend(simulation_issues)
        if not validation_ready:
            reasons.append("validation readiness is incomplete")
        gate_state = "blocked"
    elif approval_issues:
        reasons.extend(approval_issues)
        gate_state = "approval_required"
    elif simulation_issues or not validation_ready:
        if simulation_issues:
            reasons.extend(simulation_issues)
        if not validation_ready:
            reasons.append("validation readiness is incomplete")
        gate_state = "approval_required" if external_effect else ("observe_only" if prefer_observe_only else "blueprint_ready")
    elif external_effect:
        gate_state = "pilot_ready"
    else:
        gate_state = "observe_only" if prefer_observe_only else "blueprint_ready"

    return GateCheckResult(
        gate_state=gate_state,
        reasons=tuple(reasons),
        approval_ready=not approval_issues,
        rollback_ready=not rollback_issues,
        scope_valid=not scope_issues,
        blast_radius_valid=not blast_radius_issues,
    )


def _runtime_action_spec(action: ActionPlan, mode: str) -> dict[str, Any]:
    external_effect = action.scope != "workspace"
    simulation_object = {}
    if not external_effect:
        simulation_object = {
            "pilot_id": action.identifier,
            "connector_type": "workspace_internal",
            "target_scope": action.scope,
            "excluded_scope": "outside_workspace",
            "baseline_window": "current_cycle",
            "primary_metrics": ["workspace_integrity"],
            "neighbor_signals": ["validation_checks"],
            "assumed_cause": action.description,
            "expected_gain": "local safety or internal consistency",
            "abort_conditions": ["validation_failure"],
            "rollback_trigger": action.rollback,
            "adapt_options": ["observe_only", "blueprint_ready"],
            "final_pre_apply_gate": "observe_only" if mode == "observe_only" else "blueprint_ready",
            "risk_class": "R0",
            "impact_assessment_ref": "workspace_internal_low_risk_assessment",
            "evidence_plan": "local validation checks plus cycle smoke and rollback evidence",
            "aftercare_window": "current_cycle",
        }

    return {
        "connector_type": "workspace_internal" if not external_effect else "external_target",
        "target_scope": action.scope if not external_effect else action.target,
        "external_effect": external_effect,
        "requires_approval": action.requires_approval or external_effect,
        "approval_granted": False,
        "secrets_available": False,
        "reversible": action.reversible,
        "rollback_path": action.rollback,
        "rollback_trigger": action.rollback,
        "validation_ready": bool(action.validation),
        "simulation_required": external_effect,
        "simulation_object": simulation_object,
        "blast_radius": "minimal" if not external_effect else "contained",
        "doctrine_conformant": "rocket cloud" not in action.description.lower(),
        "prefer_observe_only": mode == "observe_only",
        "risk_class": "R0" if not external_effect else "R2",
        "system_registered": True,
        "impact_assessment_complete": True,
        "provenance_ready": True,
        "supply_chain_verified": True,
        "human_oversight_defined": True,
    }


def enforce_runtime_guardrails(
    workspace_root: Path,
    mode: str,
    allow_external_changes: bool,
    email_enabled: bool,
    actions: list[ActionPlan],
) -> tuple[PolicyLoadResult, list[ActionPlan], list[ValidationCheck]]:
    load_result = load_doctrine_policy(workspace_root)
    schema_issues = validate_policy_schema(load_result.policy)
    validations = [
        ValidationCheck(
            name="doctrine_policy_schema_valid",
            success=not schema_issues,
            detail="; ".join(schema_issues) if schema_issues else f"policy source: {load_result.source}",
        ),
        ValidationCheck(
            name="doctrine_external_changes_locked",
            success=not allow_external_changes,
            detail=f"allow_external_changes={allow_external_changes}",
        ),
        ValidationCheck(
            name="doctrine_notifications_locked",
            success=not email_enabled,
            detail=f"email_enabled={email_enabled}",
        ),
        ValidationCheck(
            name="doctrine_workspace_root_valid",
            success=workspace_root.exists(),
            detail=f"workspace_root={workspace_root}",
        ),
    ]
    for note in load_result.notes:
        validations.append(
            ValidationCheck(
                name="doctrine_policy_note",
                success=True,
                detail=note,
            )
        )

    guarded_actions: list[ActionPlan] = []
    for action in actions:
        gate = evaluate_pilot_gate(_runtime_action_spec(action, mode), load_result.policy, workspace_root)
        status = action.status
        if gate.gate_state == "blocked":
            status = "blocked"
        elif gate.gate_state == "approval_required" and action.scope != "workspace":
            status = "awaiting_approval"
        elif gate.gate_state == "observe_only" and action.scope == "workspace" and mode == "observe_only":
            status = "skipped_observe_only"

        metadata = dict(action.metadata)
        metadata.update(
            {
                "doctrine_gate": gate.gate_state,
                "doctrine_reasons": list(gate.reasons),
                "doctrine_scope_valid": gate.scope_valid,
                "doctrine_blast_radius_valid": gate.blast_radius_valid,
                "doctrine_approval_ready": gate.approval_ready,
                "doctrine_rollback_ready": gate.rollback_ready,
            }
        )

        guarded_actions.append(
            ActionPlan(
                identifier=action.identifier,
                phase=action.phase,
                scope=action.scope,
                status=status,
                description=action.description,
                target=action.target,
                risk=action.risk,
                reversible=action.reversible,
                requires_approval=action.requires_approval,
                rollback=action.rollback,
                validation=action.validation,
                metadata=metadata,
            )
        )

    return load_result, guarded_actions, validations
