from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from electri_city_ops.productization import derive_global_productization_readiness
from electri_city_ops.workspace import WorkspaceGuard


EXTERNAL_CUTOVER_CHECKLIST_SCHEMA_VERSION = 1
EXTERNAL_CUTOVER_CHECKLIST_PATH = "config/external-cutover-checklist.json"
ALLOWED_CUTOVER_STATUSES = {
    "operator_input_required",
    "approval_required",
    "ready_for_external_execution",
}
ALLOWED_CUTOVER_ITEM_PHASES = {
    "paypal_env_refs",
    "protected_webhook_runtime",
    "signing_and_delivery",
    "human_ownership",
    "final_go_no_go",
}
ALLOWED_CUTOVER_ITEM_STATES = {
    "local_proof_complete",
    "external_input_required",
    "external_verification_required",
    "approval_required",
    "ready_for_execution",
    "verified_in_target",
}
PENDING_CUTOVER_ITEM_STATES = {
    "external_input_required",
    "external_verification_required",
    "approval_required",
    "ready_for_execution",
}
PHASE_ORDER = (
    "paypal_env_refs",
    "protected_webhook_runtime",
    "signing_and_delivery",
    "human_ownership",
    "final_go_no_go",
)


def external_cutover_checklist_path(workspace_root: Path) -> Path:
    guard = WorkspaceGuard(workspace_root.resolve())
    return guard.resolve_inside(EXTERNAL_CUTOVER_CHECKLIST_PATH)


def load_external_cutover_checklist(workspace_root: Path) -> dict[str, Any]:
    path = external_cutover_checklist_path(workspace_root)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_external_cutover_checklist(payload: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["external cutover checklist must be an object"]

    issues: list[str] = []
    if payload.get("schema_version") != EXTERNAL_CUTOVER_CHECKLIST_SCHEMA_VERSION:
        issues.append(
            f"external cutover checklist schema_version must be {EXTERNAL_CUTOVER_CHECKLIST_SCHEMA_VERSION}"
        )

    for key in (
        "cutover_id",
        "bound_domain",
        "public_base_url",
        "protected_webhook_url",
        "go_live_decision_state",
        "next_smallest_safe_step",
    ):
        if str(payload.get(key, "")).strip() == "":
            issues.append(f"external cutover checklist requires {key}")

    status = str(payload.get("status", "")).strip()
    if status not in ALLOWED_CUTOVER_STATUSES:
        issues.append("external cutover checklist status is invalid")

    for key in ("abort_criteria", "rollback_ready_signals"):
        value = payload.get(key)
        if not isinstance(value, list) or not value or not all(str(item).strip() for item in value):
            issues.append(f"external cutover checklist {key} must be a non-empty string list")

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        issues.append("external cutover checklist items must be a non-empty list")
        return issues

    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append(f"external cutover checklist item {index} must be an object")
            continue

        item_id = str(item.get("item_id", "")).strip()
        label = item_id or f"index {index}"
        for key in (
            "item_id",
            "phase",
            "state",
            "owner",
            "description",
            "source_ref",
            "rollback_reference",
        ):
            if str(item.get(key, "")).strip() == "":
                issues.append(f"external cutover checklist item {label} missing {key}")
        if item_id:
            if item_id in seen_ids:
                issues.append(f"external cutover checklist duplicate item_id '{item_id}'")
            seen_ids.add(item_id)

        phase = str(item.get("phase", "")).strip()
        if phase not in ALLOWED_CUTOVER_ITEM_PHASES:
            issues.append(f"external cutover checklist item {label} phase is invalid")
        state = str(item.get("state", "")).strip()
        if state not in ALLOWED_CUTOVER_ITEM_STATES:
            issues.append(f"external cutover checklist item {label} state is invalid")
        if not isinstance(item.get("blocking"), bool):
            issues.append(f"external cutover checklist item {label} blocking must be boolean")
        required_evidence = item.get("required_evidence")
        if (
            not isinstance(required_evidence, list)
            or not required_evidence
            or not all(str(entry).strip() for entry in required_evidence)
        ):
            issues.append(f"external cutover checklist item {label} required_evidence must be a non-empty string list")

    return issues


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def build_external_cutover_package(workspace_root: Path) -> dict[str, Any]:
    workspace_root = workspace_root.resolve()
    checklist = load_external_cutover_checklist(workspace_root)
    checklist_issues = validate_external_cutover_checklist(checklist)
    readiness = derive_global_productization_readiness(workspace_root)
    webhook_payload = _read_json(
        workspace_root / "manifests" / "previews" / "final-real-staging-paypal-webhook-prep.json"
    ).get("paypal_webhook_prep", {})
    local_runtime_verification = webhook_payload.get("local_runtime_verification", {}) or {}

    items = checklist.get("items", []) if isinstance(checklist, dict) else []
    state_counts: dict[str, int] = {}
    phase_summaries: list[dict[str, Any]] = []
    blocking_pending_item_ids: list[str] = []
    ordered_execution_steps: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        state = str(item.get("state", "")).strip()
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
        if bool(item.get("blocking")) and state in PENDING_CUTOVER_ITEM_STATES:
            blocking_pending_item_ids.append(str(item.get("item_id", "")).strip())

    for phase in PHASE_ORDER:
        phase_items = [
            item for item in items if isinstance(item, dict) and str(item.get("phase", "")).strip() == phase
        ]
        if not phase_items:
            continue
        pending_items = [
            str(item.get("item_id", "")).strip()
            for item in phase_items
            if bool(item.get("blocking")) and str(item.get("state", "")).strip() in PENDING_CUTOVER_ITEM_STATES
        ]
        phase_summaries.append(
            {
                "phase": phase,
                "item_count": len(phase_items),
                "blocking_pending_item_ids": pending_items,
            }
        )
        if pending_items:
            ordered_execution_steps.append(
                {
                    "phase": phase,
                    "objective": (
                        "execute the external cutover items for this phase in the target environment"
                    ),
                    "blocking_pending_item_ids": pending_items,
                }
            )

    commercial_chain = readiness.get("layers", {}).get("commercial_chain", {}) or {}
    local_execution_ready = (
        not checklist_issues
        and not readiness.get("hard_blockers", [])
        and str(commercial_chain.get("local_readiness_state", "")).strip()
        == "locally_verified_waiting_external_inputs"
    )
    package_status = "ready_for_external_execution" if local_execution_ready else "blocked_by_local_preconditions"

    return {
        "schema_version": EXTERNAL_CUTOVER_CHECKLIST_SCHEMA_VERSION,
        "cutover_id": str(checklist.get("cutover_id", "")).strip(),
        "status": package_status,
        "go_live_decision_state": str(checklist.get("go_live_decision_state", "")).strip() or "approval_required",
        "bound_domain": str(checklist.get("bound_domain", "")).strip(),
        "public_base_url": str(checklist.get("public_base_url", "")).strip(),
        "protected_webhook_url": str(checklist.get("protected_webhook_url", "")).strip(),
        "local_preconditions": {
            "global_productization_status": readiness.get("status", ""),
            "commercial_chain_local_readiness_state": commercial_chain.get("local_readiness_state", ""),
            "hard_blockers": readiness.get("hard_blockers", []),
            "local_webhook_runtime_verification_state": local_runtime_verification.get("state", ""),
        },
        "checklist_issues": checklist_issues,
        "required_external_inputs": readiness.get("required_external_inputs", []),
        "blocking_pending_item_ids": blocking_pending_item_ids,
        "state_counts": state_counts,
        "phase_summaries": phase_summaries,
        "ordered_execution_steps": ordered_execution_steps,
        "abort_criteria": checklist.get("abort_criteria", []),
        "rollback_ready_signals": checklist.get("rollback_ready_signals", []),
        "next_smallest_safe_step": str(checklist.get("next_smallest_safe_step", "")).strip()
        or str(readiness.get("next_smallest_safe_step", "")).strip(),
        "evidence_refs": {
            "external_cutover_checklist": EXTERNAL_CUTOVER_CHECKLIST_PATH,
            "global_productization_readiness": "manifests/previews/final-global-productization-readiness.json",
            "paypal_webhook_prep": "manifests/previews/final-real-staging-paypal-webhook-prep.json",
        },
    }
