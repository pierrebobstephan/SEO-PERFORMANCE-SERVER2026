from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from electri_city_ops.workspace import WorkspaceGuard


AUTOMATION_CONTRACTS_PATH = "config/automation-contracts.json"
REQUIRED_CONTRACT_FIELDS = {
    "contract_id",
    "action_type",
    "version",
    "enabled",
    "risk_class",
    "scope",
    "allowed_execution_lane",
    "allowed_runtime_gates",
    "allowed_target_fields",
    "allowed_seo_owners",
    "requires_admin_confirmation",
    "requires_before_state_capture",
    "requires_rollback",
    "preconditions",
    "validation_checks",
    "rollback_plan",
    "abort_criteria",
    "protected_holds",
}


def load_automation_contracts(workspace_root: str | Path) -> dict[str, Any]:
    guard = WorkspaceGuard(Path(workspace_root).resolve())
    path = guard.resolve_inside(AUTOMATION_CONTRACTS_PATH)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_automation_contracts(payload: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["automation contracts payload must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != 1:
        issues.append("automation contracts schema_version must be 1")
    if payload.get("default_policy") != "deny_by_default":
        issues.append("automation contracts default_policy must be deny_by_default")

    contracts = payload.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        issues.append("automation contracts must include a non-empty contracts list")
        return issues

    seen_ids: set[str] = set()
    seen_actions: set[str] = set()
    for index, contract in enumerate(contracts):
        if not isinstance(contract, dict):
            issues.append(f"automation contract at index {index} must be an object")
            continue

        missing = sorted(REQUIRED_CONTRACT_FIELDS - set(contract))
        for key in missing:
            issues.append(f"automation contract at index {index} missing '{key}'")

        contract_id = str(contract.get("contract_id", "")).strip()
        action_type = str(contract.get("action_type", "")).strip()
        if not contract_id:
            issues.append(f"automation contract at index {index} contract_id must be set")
        elif contract_id in seen_ids:
            issues.append(f"automation contract_id '{contract_id}' is duplicated")
        else:
            seen_ids.add(contract_id)
        if not action_type:
            issues.append(f"automation contract at index {index} action_type must be set")
        elif action_type in seen_actions:
            issues.append(f"automation action_type '{action_type}' is duplicated")
        else:
            seen_actions.add(action_type)

        if str(contract.get("risk_class", "")).strip() not in {"R0", "R1", "R2", "R3"}:
            issues.append(f"automation contract '{contract_id}' risk_class is invalid")
        if not str(contract.get("scope", "")).strip():
            issues.append(f"automation contract '{contract_id}' scope must be set")
        if not str(contract.get("allowed_execution_lane", "")).strip():
            issues.append(f"automation contract '{contract_id}' allowed_execution_lane must be set")

        for key in (
            "allowed_runtime_gates",
            "allowed_target_fields",
            "allowed_seo_owners",
            "preconditions",
            "validation_checks",
            "rollback_plan",
            "abort_criteria",
            "protected_holds",
        ):
            value = contract.get(key)
            if not isinstance(value, list) or not all(str(item).strip() for item in value):
                issues.append(f"automation contract '{contract_id}' {key} must be a non-empty string list")

        for key in ("requires_admin_confirmation", "requires_before_state_capture", "requires_rollback"):
            if contract.get(key) is not True:
                issues.append(f"automation contract '{contract_id}' {key} must be true")

    return issues


def build_automation_contract_state(payload: dict[str, Any], issues: list[str]) -> dict[str, Any]:
    contracts = payload.get("contracts", []) if isinstance(payload, dict) else []
    valid_contracts = [
        contract
        for contract in contracts
        if isinstance(contract, dict) and str(contract.get("action_type", "")).strip()
    ]
    return {
        "schema_version": payload.get("schema_version") if isinstance(payload, dict) else None,
        "default_policy": payload.get("default_policy") if isinstance(payload, dict) else "deny_by_default",
        "status": "valid" if not issues else "invalid",
        "issues": issues,
        "allowed_action_types": sorted(str(contract["action_type"]).strip() for contract in valid_contracts),
    }


def get_automation_contract(payload: dict[str, Any], action_type: str) -> dict[str, Any] | None:
    contracts = payload.get("contracts", []) if isinstance(payload, dict) else []
    for contract in contracts:
        if isinstance(contract, dict) and str(contract.get("action_type", "")).strip() == action_type:
            return contract
    return None


def candidate_contract_issues(candidate: dict[str, Any], contract: dict[str, Any] | None) -> list[str]:
    if contract is None:
        return ["automation candidate has no matching contract"]
    issues: list[str] = []
    if not contract.get("enabled"):
        issues.append("automation contract is disabled")
    if str(candidate.get("action_type", "")).strip() != str(contract.get("action_type", "")).strip():
        issues.append("automation candidate action_type does not match contract")
    if str(candidate.get("execution_lane", "")).strip() != str(contract.get("allowed_execution_lane", "")).strip():
        issues.append("automation candidate execution_lane does not match contract")
    if str(candidate.get("target_field", "")).strip() not in {
        str(item).strip() for item in contract.get("allowed_target_fields", [])
    }:
        issues.append("automation candidate target_field is not allowed by contract")
    if str(candidate.get("runtime_gate", "")).strip() not in {
        str(item).strip() for item in contract.get("allowed_runtime_gates", [])
    }:
        issues.append("automation candidate runtime_gate is not allowed by contract")
    if str(candidate.get("active_seo_owner", "")).strip() not in {
        str(item).strip() for item in contract.get("allowed_seo_owners", [])
    }:
        issues.append("automation candidate active_seo_owner is not allowed by contract")
    if str(candidate.get("target_domain", "")).strip() != str(candidate.get("bound_domain", "")).strip():
        issues.append("automation candidate target_domain must match bound_domain")
    if candidate.get("approval_state") != "admin_confirmation_required":
        issues.append("automation candidate approval_state must require admin confirmation")
    if candidate.get("rollback_state") != "ready_if_before_state_captured":
        issues.append("automation candidate rollback_state must require before-state capture")
    return issues


def attach_contract(candidate: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(candidate)
    enriched["automation_contract_id"] = str(contract["contract_id"]).strip()
    enriched["automation_contract_version"] = str(contract["version"]).strip()
    enriched["automation_contract_state"] = "contract_verified"
    enriched["risk_class"] = str(contract["risk_class"]).strip()
    enriched["scope"] = str(contract["scope"]).strip()
    enriched["requires_admin_confirmation"] = bool(contract["requires_admin_confirmation"])
    enriched["requires_before_state_capture"] = bool(contract["requires_before_state_capture"])
    enriched["requires_rollback"] = bool(contract["requires_rollback"])
    enriched["preconditions"] = [str(item).strip() for item in contract["preconditions"]]
    enriched["validation_checks"] = [str(item).strip() for item in contract["validation_checks"]]
    enriched["rollback_plan"] = [str(item).strip() for item in contract["rollback_plan"]]
    enriched["abort_criteria"] = [str(item).strip() for item in contract["abort_criteria"]]
    enriched["protected_holds"] = [str(item).strip() for item in contract["protected_holds"]]
    return enriched
