from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Any

from .ai_governance import collect_ai_governance_status
from .doctrine import load_doctrine_policy
from .product_core import validate_domain_name


REFERENCE_PILOT_RUNTIME_INPUT_SCHEMA_VERSION = 1
REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS = "captured_from_installed_bridge"
REFERENCE_PILOT_RUNTIME_PENDING_STATUS = "operator_input_required"


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "green",
        "confirmed",
        "complete",
        "captured",
    }


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [normalized for item in value if (normalized := str(item).strip())]


def _first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _normalize_path_base(value: Any) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return "/"
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    if not normalized.endswith("/"):
        normalized += "/"
    return normalized


def validate_reference_pilot_runtime_input(payload: dict[str, Any]) -> list[str]:
    if not isinstance(payload, dict):
        return ["reference pilot runtime input must be an object"]

    issues: list[str] = []
    status = _read_status(payload, "status") or REFERENCE_PILOT_RUNTIME_PENDING_STATUS
    if status not in {
        REFERENCE_PILOT_RUNTIME_PENDING_STATUS,
        REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS,
    }:
        issues.append("reference pilot runtime input status is invalid")

    if status == REFERENCE_PILOT_RUNTIME_PENDING_STATUS:
        return issues

    schema_version = payload.get("schema_version")
    if schema_version != REFERENCE_PILOT_RUNTIME_INPUT_SCHEMA_VERSION:
        issues.append(
            f"reference pilot runtime input schema_version must be {REFERENCE_PILOT_RUNTIME_INPUT_SCHEMA_VERSION}"
        )

    source = _read_status(payload, "source")
    if source != "installed_bridge_runtime_snapshot":
        issues.append("reference pilot runtime input source must be 'installed_bridge_runtime_snapshot'")

    bound_domain = _read_status(payload, "bound_domain")
    if not bound_domain:
        issues.append("reference pilot runtime input bound_domain must be set")
    else:
        for item in validate_domain_name(bound_domain):
            issues.append(f"reference pilot runtime input {item}")

    path_base = _read_status(payload, "path_base")
    if not path_base:
        issues.append("reference pilot runtime input path_base must be set")
    elif not path_base.startswith("/") or not path_base.endswith("/"):
        issues.append("reference pilot runtime input path_base must start and end with '/'")

    blocking_conflicts = _read_status(payload, "blocking_conflicts").lower()
    if blocking_conflicts not in {"green", "blocked", "none", "false"}:
        issues.append("reference pilot runtime input blocking_conflicts must be green or blocked")

    mode = _read_status(payload, "mode")
    if mode not in {"safe_mode", "observe_only", "approval_required", "active_scoped"}:
        issues.append("reference pilot runtime input mode is invalid")

    optimization_gate = _read_status(payload, "optimization_gate")
    if optimization_gate not in {"blocked", "recommend_only", "reversible_change_ready"}:
        issues.append("reference pilot runtime input optimization_gate is invalid")

    for key in (
        "domain_match",
        "url_normalization_clean",
        "baseline_captured",
        "operator_inputs_complete",
        "source_mapping_confirmed",
    ):
        if not isinstance(payload.get(key), bool):
            issues.append(f"reference pilot runtime input {key} must be a boolean")

    if not isinstance(payload.get("open_blockers", []), list):
        issues.append("reference pilot runtime input open_blockers must be a list")
    if "notes" in payload and not isinstance(payload.get("notes"), list):
        issues.append("reference pilot runtime input notes must be a list when present")
    if status == REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS and not _read_status(payload, "next_smallest_safe_step"):
        issues.append("reference pilot runtime input next_smallest_safe_step must be set")

    return issues


def build_reference_pilot_runtime_input(bridge_export: dict[str, Any]) -> dict[str, Any]:
    runtime_context = bridge_export.get("runtime_context", {}) if isinstance(bridge_export, dict) else {}
    if not isinstance(runtime_context, dict):
        runtime_context = {}
    if not runtime_context and isinstance(bridge_export, dict):
        runtime_context = bridge_export

    validation_snapshot = bridge_export.get("validation_snapshot", {}) if isinstance(bridge_export, dict) else {}
    if not isinstance(validation_snapshot, dict):
        validation_snapshot = {}

    direct_snapshot = bridge_export.get("reference_pilot_runtime_snapshot", {}) if isinstance(bridge_export, dict) else {}
    if not isinstance(direct_snapshot, dict):
        direct_snapshot = {}
    if not direct_snapshot and isinstance(runtime_context.get("reference_pilot_runtime_snapshot"), dict):
        direct_snapshot = runtime_context["reference_pilot_runtime_snapshot"]

    license_panel = runtime_context.get("license_domain_scope_panel", {})
    if not isinstance(license_panel, dict):
        license_panel = {}
    health_signals = runtime_context.get("installation_health_signals", {})
    if not isinstance(health_signals, dict):
        health_signals = {}
    operator_input_state = runtime_context.get("operator_input_state", {})
    if not isinstance(operator_input_state, dict):
        operator_input_state = {}
    source_mapping_state = runtime_context.get("source_mapping_state", {})
    if not isinstance(source_mapping_state, dict):
        source_mapping_state = {}
    baseline_status = validation_snapshot.get("baseline_status", {})
    if not isinstance(baseline_status, dict):
        baseline_status = {}

    notes = _as_string_list(
        _first_present(
            direct_snapshot.get("notes"),
            runtime_context.get("reference_pilot_notes"),
        )
    )
    next_step = _read_status(runtime_context, "next_smallest_safe_step")
    if next_step and next_step not in notes:
        notes.append(next_step)

    return {
        "schema_version": int(
            direct_snapshot.get("schema_version", REFERENCE_PILOT_RUNTIME_INPUT_SCHEMA_VERSION)
        ),
        "source": _read_status(direct_snapshot, "source") or "installed_bridge_runtime_snapshot",
        "status": _read_status(direct_snapshot, "status") or REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS,
        "captured_at": _read_status(direct_snapshot, "captured_at"),
        "bound_domain": _read_status(direct_snapshot, "bound_domain")
        or _read_status(runtime_context, "bound_domain")
        or _read_status(license_panel, "bound_domain"),
        "current_domain": _read_status(direct_snapshot, "current_domain")
        or _read_status(runtime_context, "current_domain")
        or _read_status(license_panel, "current_domain"),
        "path_base": _normalize_path_base(
            _first_present(
                direct_snapshot.get("path_base"),
                runtime_context.get("path_base"),
                bridge_export.get("path_base") if isinstance(bridge_export, dict) else None,
            )
        ),
        "domain_match": _coerce_bool(
            _first_present(
                direct_snapshot.get("domain_match"),
                runtime_context.get("domain_match"),
                license_panel.get("domain_match"),
                validation_snapshot.get("domain_match"),
            )
        ),
        "url_normalization_clean": _coerce_bool(
            _first_present(
                direct_snapshot.get("url_normalization_clean"),
                runtime_context.get("url_normalization_clean"),
                baseline_status.get("url_normalization_clean"),
            )
        ),
        "baseline_captured": _coerce_bool(
            _first_present(
                direct_snapshot.get("baseline_captured"),
                runtime_context.get("baseline_captured"),
                baseline_status.get("captured"),
                health_signals.get("baseline_captured"),
            )
        ),
        "blocking_conflicts": _read_status(direct_snapshot, "blocking_conflicts")
        or _read_status(health_signals, "blocking_conflicts")
        or "blocked",
        "mode": _read_status(direct_snapshot, "mode")
        or _read_status(runtime_context, "mode")
        or _read_status(validation_snapshot, "mode")
        or "safe_mode",
        "optimization_gate": _read_status(direct_snapshot, "optimization_gate")
        or _read_status(health_signals, "optimization_gate")
        or _read_status(validation_snapshot, "optimization_eligibility")
        or "blocked",
        "operator_inputs_complete": _coerce_bool(
            _first_present(
                direct_snapshot.get("operator_inputs_complete"),
                runtime_context.get("operator_inputs_complete"),
                operator_input_state.get("complete"),
                validation_snapshot.get("operator_inputs", {}).get("complete")
                if isinstance(validation_snapshot.get("operator_inputs"), dict)
                else None,
            )
        ),
        "source_mapping_confirmed": _coerce_bool(
            _first_present(
                direct_snapshot.get("source_mapping_confirmed"),
                runtime_context.get("source_mapping_confirmed"),
                source_mapping_state.get("confirmed"),
                validation_snapshot.get("source_mapping", {}).get("confirmed")
                if isinstance(validation_snapshot.get("source_mapping"), dict)
                else None,
            )
        ),
        "open_blockers": _as_string_list(
            _first_present(
                direct_snapshot.get("open_blockers"),
                runtime_context.get("open_blockers"),
                validation_snapshot.get("open_blockers"),
            )
        ),
        "next_smallest_safe_step": _read_status(direct_snapshot, "next_smallest_safe_step")
        or _read_status(runtime_context, "next_smallest_safe_step")
        or "capture and store the real installed-bridge reference pilot runtime snapshot",
        "notes": notes,
    }


def build_reference_pilot_closeout_readiness(bridge_export: dict[str, Any]) -> dict[str, Any]:
    runtime_input = build_reference_pilot_runtime_input(bridge_export)
    runtime_input_issues = validate_reference_pilot_runtime_input(runtime_input)
    if runtime_input_issues:
        return {
            "status": "operator_input_required",
            "decision": "capture_runtime_again",
            "open_blockers": [f"invalid runtime input: {item}" for item in runtime_input_issues],
            "next_smallest_safe_step": "capture and store the real installed-bridge reference pilot runtime snapshot",
        }

    runtime_context = bridge_export.get("runtime_context", {}) if isinstance(bridge_export, dict) else {}
    if not isinstance(runtime_context, dict):
        runtime_context = {}
    source_mapping_state = runtime_context.get("source_mapping_state", {})
    if not isinstance(source_mapping_state, dict):
        source_mapping_state = {}
    operator_input_state = runtime_context.get("operator_input_state", {})
    if not isinstance(operator_input_state, dict):
        operator_input_state = {}
    operator_fields = operator_input_state.get("fields", {})
    if not isinstance(operator_fields, dict):
        operator_fields = {}
    missing_fields = {
        str(item).strip()
        for item in _as_string_list(operator_input_state.get("missing_fields", []))
    }

    backup_confirmation_complete = bool(_read_status(operator_fields, "backup_confirmation")) and "backup_confirmation" not in missing_fields
    restore_confirmation_complete = bool(_read_status(operator_fields, "restore_confirmation")) and "restore_confirmation" not in missing_fields
    source_mapping_confirmed = bool(source_mapping_state.get("confirmed", runtime_input["source_mapping_confirmed"]))

    closeout_items = [
        {
            "key": "backup_confirmation",
            "status": "green" if backup_confirmation_complete else "blocked",
            "detail": (
                "backup confirmation is recorded in the installed bridge operator inputs"
                if backup_confirmation_complete
                else "backup confirmation is not yet recorded in the installed bridge operator inputs"
            ),
        },
        {
            "key": "restore_confirmation",
            "status": "green" if restore_confirmation_complete else "blocked",
            "detail": (
                "restore confirmation is recorded in the installed bridge operator inputs"
                if restore_confirmation_complete
                else "restore confirmation is not yet recorded in the installed bridge operator inputs"
            ),
        },
        {
            "key": "source_mapping_confirmed",
            "status": "green" if source_mapping_confirmed else "blocked",
            "detail": (
                "source mapping is confirmed from the installed bridge runtime"
                if source_mapping_confirmed
                else "source mapping still needs explicit runtime confirmation"
            ),
        },
    ]

    open_blockers = _as_string_list(runtime_input.get("open_blockers", []))
    if not backup_confirmation_complete and "backup and restore confirmation are not yet recorded" not in open_blockers:
        open_blockers.append("backup confirmation is not yet recorded")
    if not restore_confirmation_complete and "backup and restore confirmation are not yet recorded" not in open_blockers:
        open_blockers.append("restore confirmation is not yet recorded")
    if not source_mapping_confirmed and "source mapping confirmation is not yet complete" not in open_blockers:
        open_blockers.append("source mapping confirmation is not yet complete")

    status = "ready_for_closeout_review"
    decision = "prepare_reference_pilot_closeout_review"
    if runtime_input["optimization_gate"] == "blocked" or any(item["status"] == "blocked" for item in closeout_items):
        status = "blocked"
        decision = "stay_in_staging"

    return {
        "status": status,
        "decision": decision,
        "bound_domain": runtime_input["bound_domain"],
        "current_domain": runtime_input["current_domain"],
        "path_base": runtime_input["path_base"],
        "captured_at": runtime_input.get("captured_at", ""),
        "mode": runtime_input["mode"],
        "optimization_gate": runtime_input["optimization_gate"],
        "operator_inputs_complete": runtime_input["operator_inputs_complete"],
        "source_mapping_confirmed": runtime_input["source_mapping_confirmed"],
        "closeout_items": closeout_items,
        "open_blockers": open_blockers,
        "next_smallest_safe_step": runtime_input["next_smallest_safe_step"],
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_status(payload: dict[str, Any], key: str) -> str:
    return str(payload.get(key, "")).strip()


def _is_green(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"green", "true", "confirmed"}


def _derive_reference_pilot_layer(
    runtime_input: dict[str, Any],
    preinstall_gate: dict[str, Any],
) -> dict[str, Any]:
    status = _read_status(runtime_input, "status") or "operator_input_required"
    blockers: list[str] = []
    required_inputs: list[str] = []
    proof_points: list[str] = []

    if status == "operator_input_required":
        required_inputs.extend(
            [
                "reference pilot runtime snapshot from the installed bridge",
                "current safe_mode / baseline / conflict / source-mapping runtime export",
            ]
        )
        for issue in _as_string_list(runtime_input.get("invalid_runtime_input_issues", [])):
            blockers.append(f"stored reference pilot runtime input is invalid: {issue}")
    else:
        domain_match = bool(runtime_input.get("domain_match", False))
        url_normalization_clean = bool(runtime_input.get("url_normalization_clean", False))
        baseline_captured = bool(runtime_input.get("baseline_captured", False))
        blocking_conflicts = str(runtime_input.get("blocking_conflicts", "")).strip().lower()
        mode = _read_status(runtime_input, "mode")
        optimization_gate = _read_status(runtime_input, "optimization_gate")
        open_blockers = runtime_input.get("open_blockers", [])

        if not domain_match:
            blockers.append("reference pilot runtime still reports a domain-binding mismatch")
        if not url_normalization_clean:
            blockers.append("reference pilot runtime still reports URL normalization as not clean")
        if not baseline_captured:
            blockers.append("reference pilot runtime has not captured a baseline yet")
        if blocking_conflicts not in {"green", "none", "false"}:
            blockers.append("reference pilot runtime still reports a blocking conflict picture")
        if mode not in {"safe_mode", "observe_only"}:
            blockers.append("reference pilot runtime is not in a doctrine-safe start mode")
        if optimization_gate == "blocked":
            blockers.append("reference pilot runtime still reports the optimization gate as blocked")
        if isinstance(open_blockers, list):
            blockers.extend(str(item).strip() for item in open_blockers if str(item).strip())

        if domain_match:
            proof_points.append("runtime domain binding is green")
        if url_normalization_clean:
            proof_points.append("runtime URL normalization is green")
        if baseline_captured:
            proof_points.append("runtime baseline is captured")
        if blocking_conflicts in {"green", "none", "false"}:
            proof_points.append("runtime conflict picture is green")
        if mode in {"safe_mode", "observe_only"}:
            proof_points.append(f"runtime starts in {mode}")

    if not proof_points and preinstall_gate:
        if bool(preinstall_gate.get("safe_boot_sequence_ready", False)):
            proof_points.append("pre-install safe boot sequence is ready")
        if bool(preinstall_gate.get("baseline_guardrail_sequence_ready", False)):
            proof_points.append("pre-install baseline and guardrail sequence is ready")

    layer_status = "blocked" if blockers else ("ready_for_reference_pilot" if status != "operator_input_required" else "operator_input_required")
    return {
        "status": layer_status,
        "proof_points": proof_points,
        "blockers": blockers,
        "required_inputs": required_inputs,
        "authoritative_source": (
            "runtime_input"
            if status != "operator_input_required"
            else "reference_pilot_runtime_input_missing"
        ),
    }


def _derive_commercial_chain_layer(
    paypal_ops: dict[str, Any],
    invoice_automation: dict[str, Any],
    webhook_prep: dict[str, Any],
    issuance_prep: dict[str, Any],
    signed_delivery_prep: dict[str, Any],
    orchestration: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    external_inputs: list[str] = []
    proof_points: list[str] = []

    paypal_payload = paypal_ops.get("paypal_business_ops_prep", {}) if isinstance(paypal_ops, dict) else {}
    invoice_payload = invoice_automation.get("invoice_automation_prep", {}) if isinstance(invoice_automation, dict) else {}
    webhook_payload = webhook_prep.get("paypal_webhook_prep", {}) if isinstance(webhook_prep, dict) else {}
    issuance_payload = issuance_prep.get("license_issuance_prep", {}) if isinstance(issuance_prep, dict) else {}
    signed_payload = signed_delivery_prep.get("signed_delivery_prep", {}) if isinstance(signed_delivery_prep, dict) else {}
    orchestration_payload = orchestration.get("checkout_to_issuance_orchestration", {}) if isinstance(orchestration, dict) else {}
    local_runtime_verification = webhook_payload.get("local_runtime_verification", {}) or {}
    local_runtime_verification_state = str(local_runtime_verification.get("state", "")).strip()

    secret_state = paypal_payload.get("secret_reference_state", {}) or {}
    webhook_listener = paypal_payload.get("webhook_listener_candidate", {}) or {}
    webhook_listener_state = str(webhook_listener.get("state", "")).strip()
    webhook_verification_state = _read_status(webhook_payload, "verification_state")
    webhook_handler_state = _read_status(webhook_payload, "handler_state")
    webhook_receiver_runtime_state = _read_status(webhook_payload, "receiver_runtime_state")
    webhook_verification_runtime_state = _read_status(webhook_payload, "verification_runtime_state")
    webhook_replay_runtime_state = _read_status(webhook_payload, "replay_protection_runtime_state")
    missing_paypal_env_refs: list[str] = []
    if not bool(secret_state.get("client_id_present", False)):
        missing_paypal_env_refs.append("PAYPAL_BUSINESS_CLIENT_ID")
    if not bool(secret_state.get("client_secret_present", False)):
        missing_paypal_env_refs.append("PAYPAL_BUSINESS_CLIENT_SECRET")
    if not bool(secret_state.get("webhook_id_present", False)):
        missing_paypal_env_refs.append("PAYPAL_BUSINESS_WEBHOOK_ID")
    for item in missing_paypal_env_refs:
        external_inputs.append(item)

    if str(issuance_payload.get("signing_key_reference", "")).strip() in {"", "operator_input_required"}:
        external_inputs.append("signing key reference or signing service target")
    if str((signed_payload.get("replay_protection", {}) or {}).get("state", "")).strip() in {"", "operator_input_required"}:
        external_inputs.append("replay protection policy and nonce strategy")
    delivery_grant = signed_payload.get("delivery_grant", {}) or {}
    delivery_target = str(delivery_grant.get("delivery_target", "")).strip()
    delivery_grant_rule = str(delivery_grant.get("delivery_grant_rule", "")).strip()
    if delivery_target in {"", "operator_input_required"} or delivery_grant_rule in {"", "operator_input_required"}:
        external_inputs.append("protected delivery infrastructure target and delivery grant release rule")
    if webhook_listener_state in {"invalid_public_portal_page", "invalid_public_receiver_scope"}:
        blockers.append("the configured webhook listener candidate is not a valid protected webhook receiver")
        external_inputs.append("real protected PayPal webhook receiver URL")

    if paypal_payload:
        proof_points.append("PayPal Business config is modeled with env-ref-only secrets")
        if paypal_payload.get("subscription_plans"):
            proof_points.append("PayPal subscription plan catalog is modeled with the real monthly plan IDs")
    if invoice_payload:
        proof_points.append("invoice automation prep exists and stays server-governed")
    if webhook_payload:
        proof_points.append("webhook verification prep exists without opening a public route")
    if webhook_handler_state == "implemented_local_protected_only":
        proof_points.append("protected webhook handler exists in the local protected runtime")
    if webhook_verification_runtime_state == "implemented":
        proof_points.append("PayPal webhook signature verification runtime is implemented")
    if webhook_replay_runtime_state == "implemented":
        proof_points.append("PayPal webhook replay protection runtime is implemented")
    if webhook_listener_state == "protected_receiver_candidate_modeled":
        proof_points.append("protected webhook receiver candidate is separated from public portal pages")
    if local_runtime_verification_state == "passed":
        proof_points.append("protected webhook runtime is locally self-verified through signature and replay checks")
    else:
        blockers.append("protected PayPal webhook runtime does not yet have a passing local end-to-end self-test")
    if webhook_receiver_runtime_state == "modeled_only":
        blockers.append("the protected PayPal webhook receiver is still only modeled and not yet implemented")
        external_inputs.append("protected PayPal webhook receiver implementation")
    elif webhook_receiver_runtime_state == "implemented_but_unverified" or webhook_verification_state == "implemented_runtime_ready_when_env_refs_present":
        external_inputs.append("protected PayPal webhook receiver verification and activation")
    if issuance_payload:
        proof_points.append("license issuance prep is bound to the real staging domain")
    if signed_payload:
        proof_points.append("signed delivery prep keeps public delivery, login and license API disabled")
        if delivery_target not in {"", "operator_input_required"}:
            proof_points.append(f"signed delivery target is pinned to {delivery_target}")
    if orchestration_payload:
        proof_points.append("checkout to issuance orchestration exists end-to-end in protected local form")

    return {
        "status": "operator_input_required" if external_inputs or blockers else "blueprint_ready",
        "local_readiness_state": (
            "locally_verified_waiting_external_inputs"
            if not blockers and external_inputs
            else ("local_blockers_present" if blockers else "blueprint_ready")
        ),
        "proof_points": proof_points,
        "blockers": blockers,
        "required_inputs": external_inputs,
        "current_gate": _read_status(orchestration_payload, "current_gate") or "not_built",
    }


def _derive_operations_layer(
    release_decision: dict[str, Any],
    invoice_automation: dict[str, Any],
    subscription_lifecycle: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    proof_points: list[str] = []

    release_payload = (
        release_decision.get("protected_customer_release_decision", {})
        if isinstance(release_decision, dict)
        else {}
    )
    invoice_payload = invoice_automation.get("invoice_automation_prep", {}) if isinstance(invoice_automation, dict) else {}
    lifecycle_payload = (
        subscription_lifecycle.get("subscription_lifecycle_prep", {})
        if isinstance(subscription_lifecycle, dict)
        else {}
    )

    if _read_status(release_payload, "rollback_readiness_state") != "server_managed_bridge":
        blockers.append("rollback ownership is not yet server-managed through the bridge")
    else:
        proof_points.append("rollback ownership is server-managed through the bridge")

    if _read_status(release_payload, "validation_readiness_state") != "server_managed_bridge":
        blockers.append("validation ownership is not yet server-managed through the bridge")
    else:
        proof_points.append("validation ownership is server-managed through the bridge")

    if _read_status(invoice_payload, "server_validation_state") == "server_managed_bridge":
        proof_points.append("invoice validation path is modeled as server-managed")
    if _read_status(invoice_payload, "server_rollback_state") == "server_managed_bridge":
        proof_points.append("invoice rollback path is modeled as server-managed")
    if lifecycle_payload:
        proof_points.append("renewal and failed-payment recovery remain non-destructive and operator-gated")

    return {
        "status": "blueprint_ready" if not blockers else "blocked",
        "proof_points": proof_points,
        "blockers": blockers,
        "required_inputs": [],
    }


def _derive_product_layer(
    workspace_root: Path,
    install_pack: dict[str, Any],
    release_decision: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    proof_points: list[str] = []
    required_inputs: list[str] = []

    install_pack_payload = install_pack.get("install_pack", {}) if isinstance(install_pack, dict) else {}
    visibility = (install_pack_payload.get("customer_visibility", {}) or {})
    release_payload = (
        release_decision.get("protected_customer_release_decision", {})
        if isinstance(release_decision, dict)
        else {}
    )

    support_email = _read_status(visibility, "support_email")
    if support_email:
        proof_points.append(f"buyer-visible support email is set to {support_email}")
    else:
        blockers.append("buyer-visible support email is missing")

    if _read_status(visibility, "domain_scope_summary"):
        proof_points.append("buyer-visible license / domain / scope panel is populated")
    else:
        blockers.append("buyer-visible license / domain / scope panel is incomplete")

    if _read_status(visibility, "customer_visibility_note"):
        proof_points.append("installed plugin exposes buyer-readable health, delivery and cutover state")
    else:
        blockers.append("buyer-readable installed insight surface is incomplete")

    if _read_status(release_payload, "support_handover_state") == "email_support_active":
        proof_points.append("support handover is modeled as active email support")
    else:
        required_inputs.append("final support handover and escalation process")

    if (workspace_root / "LICENSE.md").exists():
        proof_points.append("repository-level license position is documented")
    else:
        blockers.append("repository-level license position is missing")

    if (workspace_root / "docs" / "global-usage-rights-and-valuation-model.md").exists():
        proof_points.append("global usage rights and valuation model is documented")
    else:
        blockers.append("global usage rights and valuation model is missing")

    status = "blueprint_ready" if not blockers and not required_inputs else ("operator_input_required" if required_inputs else "blocked")
    return {
        "status": status,
        "proof_points": proof_points,
        "blockers": blockers,
        "required_inputs": required_inputs,
    }


def _derive_ai_governance_layer(governance_status: dict[str, Any]) -> dict[str, Any]:
    blockers = _as_string_list(governance_status.get("issues", []))
    proof_points: list[str] = []
    if int(governance_status.get("system_register_entry_count", 0)) > 0:
        proof_points.append("AI system register entries are present for suite, plugin, portal, webhook and fulfillment")
    if int(governance_status.get("impact_assessment_count", 0)) > 0:
        proof_points.append("impact assessments are present for all required systems")
    if int(governance_status.get("provenance_entry_count", 0)) > 0:
        proof_points.append("provenance evidence is recorded for all required systems")
    if int(governance_status.get("supply_chain_entry_count", 0)) > 0:
        proof_points.append("supply chain evidence is recorded for all required systems")
    if not _as_string_list(governance_status.get("secret_hygiene_issues", [])):
        proof_points.append("secret hygiene gate is green for workspace env files and ignore rules")

    return {
        "status": "blueprint_ready" if not blockers else "blocked",
        "proof_points": proof_points,
        "blockers": blockers,
        "required_inputs": [],
        "risk_distribution": governance_status.get("risk_distribution", {}),
    }


def _derive_neutral_rating(
    *,
    required_inputs: list[str],
    hard_blockers: list[str],
    workspace_root: Path,
) -> dict[str, Any]:
    open_10_10_gates: list[str] = []
    open_10_10_gates.extend(required_inputs)
    open_10_10_gates.extend(hard_blockers)

    if shutil.which("php") is None:
        open_10_10_gates.append("PHP CLI syntax validation for the WordPress bridge is not available in this environment")

    open_10_10_gates.extend(
        [
            "rotate any credentials that were previously present in workspace env files",
            "complete a real protected PayPal webhook activation test",
            "complete a signed protected delivery test",
            "complete and approve the reference pilot closeout",
            "execute and document a production rollback drill",
            "sign a global usage rights agreement before granting global commercial rights",
        ]
    )

    normalized_gates: list[str] = []
    for item in open_10_10_gates:
        normalized = str(item).strip()
        if normalized and normalized not in normalized_gates:
            normalized_gates.append(normalized)

    local_artifacts_green = (
        (workspace_root / "LICENSE.md").exists()
        and (workspace_root / "docs" / "global-usage-rights-and-valuation-model.md").exists()
        and not any("secret hygiene" in item for item in hard_blockers)
    )
    current_score = "8/10_local_blueprint"
    if hard_blockers:
        current_score = "7/10_local_blueprint_with_blockers"
    if not local_artifacts_green:
        current_score = "6/10_local_blueprint_incomplete"

    return {
        "target_score": "10/10",
        "current_score": current_score,
        "production_claim_allowed": False,
        "reason": "10/10 requires external, runtime, legal and operational evidence that cannot be created by local repository edits alone",
        "open_10_10_gates": normalized_gates,
    }


def derive_global_productization_readiness(workspace_root: Path) -> dict[str, Any]:
    workspace_root = workspace_root.resolve()
    doctrine = load_doctrine_policy(workspace_root)
    ai_governance_status = collect_ai_governance_status(workspace_root, doctrine.policy)
    runtime_input = _load_json(workspace_root / "config" / "reference-pilot-runtime-input.json")
    runtime_input_issues = validate_reference_pilot_runtime_input(runtime_input)
    if runtime_input_issues:
        runtime_input = {
            "status": REFERENCE_PILOT_RUNTIME_PENDING_STATUS,
            "invalid_runtime_input_issues": runtime_input_issues,
        }
    preinstall_gate = _load_json(workspace_root / "config" / "real-staging-ready-gate.json")
    install_pack = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-install-pack.json")
    paypal_ops = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-paypal-business-ops-prep.json")
    invoice_automation = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-invoice-automation-prep.json")
    webhook_prep = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-paypal-webhook-prep.json")
    orchestration = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-checkout-to-issuance-orchestration.json")
    release_decision = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-release-decision.json")
    subscription_lifecycle = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-subscription-lifecycle-prep.json")
    issuance_prep = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-license-issuance-prep.json")
    signed_delivery_prep = _load_json(workspace_root / "manifests" / "previews" / "final-real-staging-signed-delivery-prep.json")

    reference_pilot = _derive_reference_pilot_layer(runtime_input, preinstall_gate)
    commercial_chain = _derive_commercial_chain_layer(
        paypal_ops,
        invoice_automation,
        webhook_prep,
        issuance_prep,
        signed_delivery_prep,
        orchestration,
    )
    operations = _derive_operations_layer(release_decision, invoice_automation, subscription_lifecycle)
    product = _derive_product_layer(workspace_root, install_pack, release_decision)
    ai_governance = _derive_ai_governance_layer(ai_governance_status)

    all_required_inputs: list[str] = []
    for layer in (ai_governance, reference_pilot, commercial_chain, operations, product):
        for item in layer.get("required_inputs", []):
            normalized = str(item).strip()
            if normalized and normalized not in all_required_inputs:
                all_required_inputs.append(normalized)

    hard_blockers: list[str] = []
    for layer_name, layer in (
        ("ai_governance", ai_governance),
        ("reference_pilot", reference_pilot),
        ("commercial_chain", commercial_chain),
        ("operations", operations),
        ("product", product),
    ):
        for item in layer.get("blockers", []):
            normalized = str(item).strip()
            if normalized:
                hard_blockers.append(f"{layer_name}: {normalized}")

    if ai_governance["status"] == "blocked":
        overall_status = "ai_governance_not_closed"
        next_smallest_safe_step = (
            "repair the doctrine 8.0 AI system register, impact assessments, provenance and supply-chain evidence"
        )
    elif reference_pilot["status"] in {"blocked", "operator_input_required"}:
        overall_status = "reference_pilot_not_closed"
        next_smallest_safe_step = _read_status(runtime_input, "next_smallest_safe_step") or (
            "capture and store the real installed-bridge reference pilot runtime snapshot"
        )
    elif commercial_chain["status"] == "operator_input_required":
        overall_status = "commercial_chain_not_closed"
        next_smallest_safe_step = "inject PayPal env refs and verify the protected webhook receiver in the real server context"
    elif operations["status"] == "blocked":
        overall_status = "operations_not_closed"
        next_smallest_safe_step = "restore server-managed rollback and validation ownership before any cutover"
    elif product["status"] == "operator_input_required":
        overall_status = "product_surface_not_closed"
        next_smallest_safe_step = "close the final support handover and buyer-facing delivery process"
    else:
        overall_status = "ready_for_controlled_reference_pilot_and_external_cutover_work"
        next_smallest_safe_step = "run the controlled reference pilot and begin external cutover execution"

    return {
        "status": overall_status,
        "doctrine_state": "approval_required",
        "bound_domain": "wp.electri-c-ity-studios-24-7.com",
        "path_base": "/wordpress/",
        "layers": {
            "ai_governance": ai_governance,
            "reference_pilot": reference_pilot,
            "commercial_chain": commercial_chain,
            "operations": operations,
            "product": product,
        },
        "hard_blockers": hard_blockers,
        "required_external_inputs": all_required_inputs,
        "neutral_rating": _derive_neutral_rating(
            required_inputs=all_required_inputs,
            hard_blockers=hard_blockers,
            workspace_root=workspace_root,
        ),
        "next_smallest_safe_step": next_smallest_safe_step,
        "ready_for_global_go_live": False,
    }
