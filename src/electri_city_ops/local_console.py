from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import json
import os
from pathlib import Path
import subprocess
import threading
from typing import Any

from electri_city_ops.ai_governance import (
    collect_ai_governance_status,
    load_ai_impact_assessments,
    load_ai_system_register,
    load_provenance_evidence,
    load_supply_chain_evidence,
    validate_ai_impact_assessments,
    validate_ai_system_register,
    validate_provenance_evidence,
    validate_supply_chain_evidence,
)
from electri_city_ops.backend_core import derive_backend_state
from electri_city_ops.config import AppConfig, load_config
from electri_city_ops.doctrine import load_doctrine_policy, validate_policy_schema
from electri_city_ops.external_cutover import (
    build_external_cutover_package,
    load_external_cutover_checklist,
    validate_external_cutover_checklist,
)
from electri_city_ops.manifest_builder import (
    build_plugin_package_metadata,
    build_release_artifact,
    build_update_manifest_preview,
    validate_domain_entitlement,
    validate_plugin_package_metadata,
)
from electri_city_ops.onboarding import (
    transition_onboarding_state,
    validate_domain_onboarding_entry,
    validate_dry_run_onboarding_constraints,
)
from electri_city_ops.productization import (
    derive_global_productization_readiness,
    validate_reference_pilot_runtime_input,
)
from electri_city_ops.product_core import (
    load_release_channels,
    validate_domain_binding,
    validate_license_object,
    validate_release_channels,
)
from electri_city_ops.paypal_webhook_runtime import handle_protected_paypal_webhook
from electri_city_ops.registry import (
    load_backend_defaults,
    validate_license_registry_entry,
    validate_policy_registry_entry,
)
from electri_city_ops.rollback_registry import validate_rollback_profile_entry


LOCAL_ONLY_HOSTS = {"127.0.0.1", "localhost"}
ACTION_LABELS = {
    "run_python_tests": "Run Python Tests",
    "run_validate_config": "Validate Config",
    "run_schema_checks": "Run Schema Checks",
    "run_dry_run_onboarding": "Dry Run Onboarding",
    "build_manifest_preview": "Build Manifest Preview",
    "build_package_metadata": "Build Package Metadata",
    "build_release_artifact_preview": "Build Release Artifact Preview",
    "build_protected_customer_install_pack": "Build Protected Customer Install Pack",
    "build_signed_delivery_prep": "Build Signed Delivery Prep",
    "build_checkout_to_issuance_orchestration": "Build Checkout To Issuance Orchestration",
    "build_payment_confirmation_and_customer_release": "Build Payment Confirmation And Customer Release",
    "build_invoice_confirmation_and_release_decision": "Build Invoice Confirmation And Release Decision",
    "build_subscription_lifecycle_prep": "Build Subscription Lifecycle Prep",
    "build_paypal_business_and_invoice_prep": "Build PayPal Business And Invoice Prep",
    "build_global_productization_readiness": "Build Global Productization Readiness",
    "build_external_cutover_package": "Build External Cutover Package",
}


@dataclass(slots=True)
class LocalConsoleConfig:
    host: str
    port: int
    title: str
    local_only_notice: str
    max_text_bytes: int
    max_action_output_bytes: int
    allowed_actions: tuple[str, ...]
    notes: tuple[str, ...] = ()


@dataclass(slots=True)
class ActionExecutionResult:
    action: str
    ok: bool
    output: str
    returncode: int
    timestamp: str


def local_console_config_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "local-console.json"


def load_local_console_config(workspace_root: Path) -> LocalConsoleConfig:
    path = local_console_config_path(workspace_root)
    payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    host = str(payload.get("host", "127.0.0.1")).strip() or "127.0.0.1"
    notes: list[str] = []
    if host not in LOCAL_ONLY_HOSTS:
        notes.append(f"Configured host '{host}' is not allowed. Falling back to 127.0.0.1.")
        host = "127.0.0.1"
    if host == "localhost":
        host = "127.0.0.1"

    allowed_actions = tuple(
        name
        for name in payload.get("allowed_actions", [])
        if isinstance(name, str) and name in ACTION_LABELS
    )
    if not allowed_actions:
        allowed_actions = tuple(ACTION_LABELS)

    return LocalConsoleConfig(
        host=host,
        port=max(1024, int(payload.get("port", 8765))),
        title=str(payload.get("title", "Electri City Ops Local Console")).strip() or "Electri City Ops Local Console",
        local_only_notice=str(payload.get("local_only_notice", "Local only / no external effect")).strip()
        or "Local only / no external effect",
        max_text_bytes=max(4096, int(payload.get("max_text_bytes", 65536))),
        max_action_output_bytes=max(2048, int(payload.get("max_action_output_bytes", 20000))),
        allowed_actions=allowed_actions,
        notes=tuple(notes),
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text_preview(path: Path, limit: int) -> str:
    if not path.exists():
        return "(not present)"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n... truncated ..."


def _read_json_preview(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
    }


def _count_python_tests(tests_dir: Path) -> dict[str, int]:
    files = sorted(path for path in tests_dir.glob("test_*.py") if path.is_file())
    test_methods = 0
    for path in files:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lstrip().startswith("def test_"):
                test_methods += 1
    return {"file_count": len(files), "test_method_count": test_methods}


def build_operator_fulfillment_cockpit(workspace_root: Path) -> dict[str, Any]:
    install_pack_path = workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-install-pack.json"
    issuance_prep_path = workspace_root / "manifests" / "previews" / "final-real-staging-license-issuance-prep.json"
    signed_delivery_prep_path = workspace_root / "manifests" / "previews" / "final-real-staging-signed-delivery-prep.json"
    checkout_record_path = workspace_root / "manifests" / "previews" / "final-real-staging-checkout-record-prep.json"
    payment_confirmation_path = workspace_root / "manifests" / "previews" / "final-real-staging-payment-confirmation-prep.json"
    invoice_confirmation_path = workspace_root / "manifests" / "previews" / "final-real-staging-invoice-confirmation-prep.json"
    customer_release_authorization_path = (
        workspace_root / "manifests" / "previews" / "final-real-staging-customer-release-authorization.json"
    )
    protected_customer_release_decision_path = (
        workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-release-decision.json"
    )
    subscription_lifecycle_path = (
        workspace_root / "manifests" / "previews" / "final-real-staging-subscription-lifecycle-prep.json"
    )
    renewal_prep_path = workspace_root / "manifests" / "previews" / "final-real-staging-renewal-prep.json"
    failed_payment_recovery_path = (
        workspace_root / "manifests" / "previews" / "final-real-staging-failed-payment-recovery-prep.json"
    )
    paypal_ops_path = workspace_root / "manifests" / "previews" / "final-real-staging-paypal-business-ops-prep.json"
    invoice_automation_path = (
        workspace_root / "manifests" / "previews" / "final-real-staging-invoice-automation-prep.json"
    )
    paypal_webhook_path = workspace_root / "manifests" / "previews" / "final-real-staging-paypal-webhook-prep.json"
    orchestration_path = workspace_root / "manifests" / "previews" / "final-real-staging-checkout-to-issuance-orchestration.json"
    package_metadata_path = workspace_root / "manifests" / "previews" / "final-real-staging-pilot-package-metadata.json"

    install_pack = _read_json_preview(install_pack_path)
    issuance_prep = _read_json_preview(issuance_prep_path)
    signed_delivery_prep = _read_json_preview(signed_delivery_prep_path)
    checkout_record = _read_json_preview(checkout_record_path)
    payment_confirmation = _read_json_preview(payment_confirmation_path)
    invoice_confirmation = _read_json_preview(invoice_confirmation_path)
    customer_release_authorization = _read_json_preview(customer_release_authorization_path)
    protected_customer_release_decision = _read_json_preview(protected_customer_release_decision_path)
    subscription_lifecycle = _read_json_preview(subscription_lifecycle_path)
    renewal_prep = _read_json_preview(renewal_prep_path)
    failed_payment_recovery = _read_json_preview(failed_payment_recovery_path)
    paypal_ops = _read_json_preview(paypal_ops_path)
    invoice_automation = _read_json_preview(invoice_automation_path)
    paypal_webhook = _read_json_preview(paypal_webhook_path)
    orchestration = _read_json_preview(orchestration_path)
    package_metadata = _read_json_preview(package_metadata_path)

    install_pack_payload = install_pack.get("install_pack", {}) if isinstance(install_pack, dict) else {}
    issuance_payload = issuance_prep.get("license_issuance_prep", {}) if isinstance(issuance_prep, dict) else {}
    signed_payload = signed_delivery_prep.get("signed_delivery_prep", {}) if isinstance(signed_delivery_prep, dict) else {}
    checkout_payload = checkout_record.get("checkout_record_prep", {}) if isinstance(checkout_record, dict) else {}
    payment_payload = payment_confirmation.get("payment_confirmation_prep", {}) if isinstance(payment_confirmation, dict) else {}
    invoice_payload = invoice_confirmation.get("invoice_confirmation_prep", {}) if isinstance(invoice_confirmation, dict) else {}
    release_payload = (
        customer_release_authorization.get("customer_release_authorization", {})
        if isinstance(customer_release_authorization, dict)
        else {}
    )
    release_decision_payload = (
        protected_customer_release_decision.get("protected_customer_release_decision", {})
        if isinstance(protected_customer_release_decision, dict)
        else {}
    )
    lifecycle_payload = (
        subscription_lifecycle.get("subscription_lifecycle_prep", {})
        if isinstance(subscription_lifecycle, dict)
        else {}
    )
    renewal_payload = renewal_prep.get("renewal_prep", {}) if isinstance(renewal_prep, dict) else {}
    recovery_payload = (
        failed_payment_recovery.get("failed_payment_recovery_prep", {})
        if isinstance(failed_payment_recovery, dict)
        else {}
    )
    paypal_ops_payload = (
        paypal_ops.get("paypal_business_ops_prep", {}) if isinstance(paypal_ops, dict) else {}
    )
    invoice_automation_payload = (
        invoice_automation.get("invoice_automation_prep", {}) if isinstance(invoice_automation, dict) else {}
    )
    paypal_webhook_payload = (
        paypal_webhook.get("paypal_webhook_prep", {}) if isinstance(paypal_webhook, dict) else {}
    )
    orchestration_payload = orchestration.get("checkout_to_issuance_orchestration", {}) if isinstance(orchestration, dict) else {}
    customer_visibility_payload = (install_pack_payload.get("customer_visibility", {}) or {})
    paypal_secret_reference_state = paypal_ops_payload.get("secret_reference_state", {}) or {}
    paypal_webhook_local_runtime_verification = paypal_webhook_payload.get("local_runtime_verification", {}) or {}

    return {
        "status": "local_operator_only",
        "public_delivery": False,
        "customer_login": False,
        "license_api_exposed": False,
        "package_metadata": package_metadata,
        "paypal_business_ops_prep": paypal_ops,
        "invoice_automation_prep": invoice_automation,
        "paypal_webhook_prep": paypal_webhook,
        "checkout_record_prep": checkout_record,
        "payment_confirmation_prep": payment_confirmation,
        "invoice_confirmation_prep": invoice_confirmation,
        "customer_release_authorization": customer_release_authorization,
        "protected_customer_release_decision": protected_customer_release_decision,
        "subscription_lifecycle_prep": subscription_lifecycle,
        "renewal_prep": renewal_prep,
        "failed_payment_recovery_prep": failed_payment_recovery,
        "checkout_to_issuance_orchestration": orchestration,
        "protected_customer_install_pack": install_pack,
        "license_issuance_prep": issuance_prep,
        "signed_delivery_prep": signed_delivery_prep,
        "summary": {
            "bound_domain": install_pack_payload.get("bound_domain", ""),
            "package_archive_path": (install_pack_payload.get("package", {}) or {}).get("archive_path", ""),
            "package_sha256": (install_pack_payload.get("package", {}) or {}).get("package_sha256", ""),
            "selected_plan": checkout_payload.get("selected_plan", ""),
            "support_email": customer_visibility_payload.get("support_email", ""),
            "payment_method": payment_payload.get("payment_method", ""),
            "payment_processor_label": payment_payload.get("payment_processor_label", ""),
            "paypal_environment": paypal_ops_payload.get("environment", ""),
            "paypal_client_id_present": paypal_secret_reference_state.get("client_id_present", False),
            "paypal_client_secret_present": paypal_secret_reference_state.get("client_secret_present", False),
            "paypal_webhook_id_present": paypal_secret_reference_state.get("webhook_id_present", False),
            "paypal_webhook_candidate_url": paypal_webhook_payload.get("listener_candidate_url", ""),
            "paypal_webhook_candidate_state": paypal_webhook_payload.get("listener_candidate_state", ""),
            "paypal_webhook_candidate_reason": paypal_webhook_payload.get("listener_candidate_reason", ""),
            "paypal_webhook_candidate_delivery_scope": paypal_webhook_payload.get("listener_candidate_delivery_scope", ""),
            "paypal_webhook_handler_path": paypal_webhook_payload.get("handler_path", ""),
            "paypal_webhook_handler_state": paypal_webhook_payload.get("handler_state", ""),
            "paypal_webhook_receiver_runtime_state": paypal_webhook_payload.get("receiver_runtime_state", ""),
            "paypal_webhook_verification_runtime_state": paypal_webhook_payload.get("verification_runtime_state", ""),
            "paypal_webhook_replay_runtime_state": paypal_webhook_payload.get("replay_protection_runtime_state", ""),
            "paypal_webhook_env_ref_readiness_state": paypal_webhook_payload.get("env_ref_readiness_state", ""),
            "paypal_webhook_activation_state": paypal_webhook_payload.get("activation_state", ""),
            "paypal_webhook_local_runtime_verification_state": paypal_webhook_local_runtime_verification.get("state", ""),
            "paypal_webhook_local_runtime_verification_mode": paypal_webhook_local_runtime_verification.get("proof_mode", ""),
            "checkout_status": checkout_payload.get("status", ""),
            "payment_confirmation_state": payment_payload.get("payment_confirmation_state", ""),
            "invoice_state": payment_payload.get("invoice_state", ""),
            "invoice_confirmation_state": invoice_payload.get("invoice_confirmation_state", ""),
            "invoice_automation_state": invoice_automation_payload.get("status", ""),
            "invoice_server_validation_state": invoice_automation_payload.get("server_validation_state", ""),
            "invoice_server_rollback_state": invoice_automation_payload.get("server_rollback_state", ""),
            "webhook_verification_state": paypal_webhook_payload.get("verification_state", ""),
            "subscription_lifecycle_status": lifecycle_payload.get("status", ""),
            "renewal_state": renewal_payload.get("renewal_state", ""),
            "renewal_window_state": renewal_payload.get("renewal_window_state", ""),
            "failed_payment_recovery_state": recovery_payload.get("recovery_state", ""),
            "subscription_status": (install_pack_payload.get("customer_visibility", {}) or {}).get("subscription_status", ""),
            "license_integrity_state": (install_pack_payload.get("customer_visibility", {}) or {}).get("license_integrity_state", ""),
            "issuance_status": issuance_payload.get("status", ""),
            "signature_state": issuance_payload.get("signature_state", ""),
            "signing_key_reference": issuance_payload.get("signing_key_reference", ""),
            "signed_delivery_status": signed_payload.get("status", ""),
            "replay_protection_state": (signed_payload.get("replay_protection", {}) or {}).get("state", ""),
            "delivery_grant_state": (signed_payload.get("delivery_grant", {}) or {}).get("state", ""),
            "customer_release_state": release_payload.get("release_state", ""),
            "customer_release_channel": release_payload.get("customer_release_channel", ""),
            "release_decision_state": release_decision_payload.get("release_decision_state", ""),
            "release_go_no_go_state": release_decision_payload.get("go_no_go_state", ""),
            "lifecycle_next_gate": lifecycle_payload.get("next_operator_gate", ""),
            "orchestration_gate": orchestration_payload.get("current_gate", ""),
        },
        "global_sales_readiness": {
            "current_phase": "protected_local_prep_with_paypal_invoice_and_lifecycle",
            "next_gate": "real_paypal_business_confirmation_and_signed_delivery_ops_path",
            "still_approval_required": [
                "real PayPal Business payment confirmation and invoice operations",
                "real renewal billing and failed payment recovery operations",
                "real signing keys and signing service",
                "real protected delivery infrastructure",
                "real customer purchase and fulfillment flow",
                "real support and escalation process",
                "global production go-live gates",
            ],
        },
    }


def build_preview_objects(workspace_root: Path, config: AppConfig) -> dict[str, Any]:
    built_at = _now_iso()
    domain = config.domains[0] if config.domains else ""
    source_role = "reference_site" if domain == "electri-c-ity-studios-24-7.com" else "customer_site"

    license_object = {
        "license_id": "preview-license-homepage-meta",
        "customer_id": "operator input required",
        "product_id": "hso-plugin",
        "status": "approval_required",
        "domain_binding": {
            "bound_domain": domain,
            "allowed_subdomains": [],
            "allowed_scopes": ["homepage_only", "feature:meta_description"],
            "release_channel": "pilot",
            "policy_channel": "pilot",
            "rollback_profile_id": "rb-preview-homepage-meta",
        },
        "allowed_features": ["meta_description"],
        "issued_at": built_at,
        "non_expiring": True,
        "integrity": {
            "signature": "source not yet confirmed",
            "signature_state": "operator_signing_required",
            "signing_key_reference": "local_server_signing_key",
        },
    }

    license_registry_entry = {
        "registry_id": "lic-reg-preview-homepage-meta",
        "license": license_object,
        "binding_state": "confirmed",
        "source_role": source_role,
        "created_at": built_at,
    }

    policy_entry = {
        "registry_id": "pol-reg-preview-homepage-meta",
        "license_id": license_object["license_id"],
        "bound_domain": domain,
        "release_channel": "pilot",
        "policy_version": "local-preview-1",
        "default_mode": "approval_required",
        "allowed_scopes": ["homepage_only", "feature:meta_description"],
        "module_flags": {"meta_description": False},
        "rollback_profile_id": "rb-preview-homepage-meta",
        "registry_state": "confirmed",
        "created_at": built_at,
    }

    rollback_entry = {
        "registry_id": "rb-reg-preview-homepage-meta",
        "profile": {
            "rollback_profile_id": "rb-preview-homepage-meta",
            "bound_domain": domain,
            "release_channel": "pilot",
            "rollback_channel": "rollback",
            "rollback_steps": [
                "restore previous homepage meta description source",
                "re-run head validation on homepage preview",
            ],
            "verification_checks": [
                "exactly one homepage meta description remains present",
                "title canonical robots remain stable",
            ],
            "abort_triggers": [
                "duplicate meta description detected",
                "title or canonical regression detected",
            ],
            "issued_at": built_at,
        },
        "registry_state": "confirmed",
        "created_at": built_at,
    }

    onboarding_entry = {
        "onboarding_id": "onb-preview-homepage-meta",
        "onboarding": {
            "customer_id": "operator input required",
            "requested_domain": domain,
            "requested_channel": "pilot",
            "requested_scopes": ["homepage_only", "feature:meta_description"],
            "site_role": source_role,
            "cms_platform": "wordpress",
            "operator_contact_status": "pending",
        },
        "state": "approval_required",
        "created_at": built_at,
    }

    plugin_root = workspace_root / "packages" / "wp-plugin" / "hetzner-seo-ops"
    package_metadata = build_plugin_package_metadata(
        plugin_root,
        plugin_slug="hetzner-seo-ops",
        plugin_version="0.0.1-dev",
        release_channel="pilot",
        built_at=built_at,
    )
    manifest_request = {
        "license_id": license_object["license_id"],
        "policy_registry_id": policy_entry["registry_id"],
        "rollback_registry_id": rollback_entry["registry_id"],
        "requested_channel": "pilot",
        "plugin_version": package_metadata["plugin_version"],
        "package_basename": package_metadata["package_basename"],
        "min_plugin_version": package_metadata["plugin_version"],
        "conflict_blocklist_version": "1",
        "issued_at": built_at,
    }
    manifest_result = build_update_manifest_preview(
        manifest_request,
        license_registry_entry,
        policy_entry,
        rollback_entry,
        load_release_channels(workspace_root).channels,
    )
    manifest_preview = manifest_result.manifest

    entitlement = {
        "entitlement_id": "ent-preview-homepage-meta",
        "license_id": license_object["license_id"],
        "bound_domain": domain,
        "release_channel": "pilot",
        "allowed_package_version": package_metadata["plugin_version"],
        "allowed_scopes": ["homepage_only", "feature:meta_description"],
        "approval_state": "approval_required",
        "issued_at": built_at,
    }

    release_artifact = None
    release_artifact_issues: tuple[str, ...] = ()
    if manifest_preview is not None:
        release_artifact, release_artifact_issues = build_release_artifact(
            package_metadata,
            manifest_preview,
            entitlement,
            load_release_channels(workspace_root).channels,
            artifact_id="artifact-preview-homepage-meta",
            built_at=built_at,
        )

    onboarding_transition = transition_onboarding_state(onboarding_entry, "confirmed")

    return {
        "license_object": license_object,
        "domain_binding": license_object["domain_binding"],
        "license_registry_entry": license_registry_entry,
        "policy_preview": policy_entry,
        "rollback_profile_preview": rollback_entry,
        "onboarding_preview": onboarding_entry,
        "onboarding_transition_preview": {
            "valid": onboarding_transition.valid,
            "issues": list(onboarding_transition.issues),
            "result": onboarding_transition.entry,
        },
        "manifest_build_request": manifest_request,
        "manifest_preview": manifest_preview,
        "manifest_preview_issues": list(manifest_result.issues),
        "plugin_package_metadata_preview": package_metadata,
        "domain_entitlement_preview": entitlement,
        "release_artifact_preview": release_artifact,
        "release_artifact_issues": list(release_artifact_issues),
        "preview_notes": [
            "All objects are local preview-only and are not issued to any external system.",
            "Registry entries are locally marked confirmed only to validate preview build chains; real product state remains approval_required.",
            "Customer identifiers, secrets, signatures, and live transport details remain operator input required or source not yet confirmed.",
        ],
    }


def run_schema_checks(workspace_root: Path, config: AppConfig, console_config: LocalConsoleConfig) -> dict[str, Any]:
    doctrine = load_doctrine_policy(workspace_root)
    channels_result = load_release_channels(workspace_root)
    previews = build_preview_objects(workspace_root, config)
    register_payload = load_ai_system_register(workspace_root)
    impact_payload = load_ai_impact_assessments(workspace_root)
    provenance_payload = load_provenance_evidence(workspace_root)
    supply_chain_payload = load_supply_chain_evidence(workspace_root)
    external_cutover_payload = load_external_cutover_checklist(workspace_root)
    schema_files = sorted((workspace_root / "schemas").glob("*.json"))
    schema_issues: list[str] = []
    parsed_schemas: list[str] = []
    for path in schema_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key in ("$schema", "title", "type"):
            if key not in payload:
                schema_issues.append(f"{path.name} missing '{key}'")
        parsed_schemas.append(path.name)

    validations = {
        "release_channels": validate_release_channels(channels_result.channels),
        "license_object": validate_license_object(previews["license_object"], channels_result.channels),
        "domain_binding": validate_domain_binding(previews["domain_binding"], channels_result.channels),
        "ai_system_register": validate_ai_system_register(register_payload, doctrine.policy),
        "ai_impact_assessments": validate_ai_impact_assessments(impact_payload, register_payload, doctrine.policy),
        "provenance_evidence": validate_provenance_evidence(provenance_payload, register_payload),
        "supply_chain_evidence": validate_supply_chain_evidence(supply_chain_payload, register_payload),
        "external_cutover_checklist": validate_external_cutover_checklist(external_cutover_payload),
        "reference_pilot_runtime_input": validate_reference_pilot_runtime_input(
            _read_json_preview(workspace_root / "config" / "reference-pilot-runtime-input.json") or {}
        ),
        "license_registry_entry": list(
            validate_license_registry_entry(previews["license_registry_entry"], channels_result.channels).issues
        ),
        "policy_registry_entry": list(
            validate_policy_registry_entry(
                previews["policy_preview"],
                channels_result.channels,
                previews["license_object"],
            ).issues
        ),
        "rollback_profile_entry": list(
            validate_rollback_profile_entry(previews["rollback_profile_preview"], channels_result.channels).issues
        ),
        "domain_onboarding_entry": list(
            validate_domain_onboarding_entry(previews["onboarding_preview"], channels_result.channels).issues
        ),
        "dry_run_onboarding": list(validate_dry_run_onboarding_constraints(previews["onboarding_preview"]).issues),
        "plugin_package_metadata": list(
            validate_plugin_package_metadata(previews["plugin_package_metadata_preview"], channels_result.channels).issues
        ),
        "domain_entitlement": list(
            validate_domain_entitlement(previews["domain_entitlement_preview"], channels_result.channels).issues
        ),
        "manifest_preview": list(previews["manifest_preview_issues"]),
        "release_artifact_preview": list(previews["release_artifact_issues"]),
    }
    ok = not schema_issues and not any(validations.values())
    return {
        "ok": ok,
        "parsed_schemas": parsed_schemas,
        "schema_issues": schema_issues,
        "validations": validations,
        "local_console_allowed_actions": list(console_config.allowed_actions),
    }


def _run_subprocess_action(
    workspace_root: Path,
    command: list[str],
    max_output_bytes: int,
) -> ActionExecutionResult:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    completed = subprocess.run(
        command,
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    output = (completed.stdout or "") + ("\n" + completed.stderr if completed.stderr else "")
    if len(output) > max_output_bytes:
        output = output[:max_output_bytes] + "\n\n... truncated ..."
    return ActionExecutionResult(
        action=" ".join(command),
        ok=completed.returncode == 0,
        output=output,
        returncode=completed.returncode,
        timestamp=_now_iso(),
    )


def execute_local_action(
    action: str,
    workspace_root: Path,
    config: AppConfig,
    console_config: LocalConsoleConfig,
) -> ActionExecutionResult:
    if action not in console_config.allowed_actions:
        return ActionExecutionResult(
            action=action,
            ok=False,
            output="Action is not allowed in the local console configuration.",
            returncode=2,
            timestamp=_now_iso(),
        )

    if action == "run_python_tests":
        return _run_subprocess_action(
            workspace_root,
            ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
            console_config.max_action_output_bytes,
        )
    if action == "run_validate_config":
        return _run_subprocess_action(
            workspace_root,
            ["python3", "-m", "electri_city_ops", "validate-config", "--config", "config/settings.toml"],
            console_config.max_action_output_bytes,
        )

    payload: dict[str, Any]
    if action == "run_schema_checks":
        payload = run_schema_checks(workspace_root, config, console_config)
    elif action == "run_dry_run_onboarding":
        previews = build_preview_objects(workspace_root, config)
        payload = {
            "validation": list(
                validate_domain_onboarding_entry(
                    previews["onboarding_preview"],
                    load_release_channels(workspace_root).channels,
                ).issues
            ),
            "dry_run": list(validate_dry_run_onboarding_constraints(previews["onboarding_preview"]).issues),
            "transition_preview": previews["onboarding_transition_preview"],
        }
    elif action == "build_manifest_preview":
        previews = build_preview_objects(workspace_root, config)
        payload = {
            "issues": previews["manifest_preview_issues"],
            "manifest_preview": previews["manifest_preview"],
            "build_request": previews["manifest_build_request"],
        }
    elif action == "build_package_metadata":
        previews = build_preview_objects(workspace_root, config)
        payload = {
            "issues": list(
                validate_plugin_package_metadata(
                    previews["plugin_package_metadata_preview"],
                    load_release_channels(workspace_root).channels,
                ).issues
            ),
            "package_metadata_preview": previews["plugin_package_metadata_preview"],
        }
    elif action == "build_release_artifact_preview":
        previews = build_preview_objects(workspace_root, config)
        payload = {
            "issues": previews["release_artifact_issues"],
            "release_artifact_preview": previews["release_artifact_preview"],
            "domain_entitlement_preview": previews["domain_entitlement_preview"],
        }
    elif action == "build_protected_customer_install_pack":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_protected_customer_install_pack.py",
                "--bridge-config",
                "packages/wp-plugin/hetzner-seo-ops/config/bridge-config.json",
                "--package-metadata",
                "manifests/previews/final-real-staging-pilot-package-metadata.json",
                "--license-object",
                "manifests/previews/final-real-staging-pilot-license-object-preview.json",
                "--manifest",
                "manifests/previews/final-real-staging-pilot-manifest-preview.json",
                "--entitlement",
                "manifests/previews/final-real-staging-pilot-entitlement-preview.json",
                "--rollback-profile",
                "manifests/previews/final-real-staging-pilot-rollback-profile-preview.json",
                "--validation-checklist",
                "manifests/previews/final-real-staging-pilot-validation-checklist-preview.json",
                "--output",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_signed_delivery_prep":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_signed_delivery_prep.py",
                "--bridge-config",
                "packages/wp-plugin/hetzner-seo-ops/config/bridge-config.json",
                "--package-metadata",
                "manifests/previews/final-real-staging-pilot-package-metadata.json",
                "--license-object",
                "manifests/previews/final-real-staging-pilot-license-object-preview.json",
                "--manifest",
                "manifests/previews/final-real-staging-pilot-manifest-preview.json",
                "--entitlement",
                "manifests/previews/final-real-staging-pilot-entitlement-preview.json",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_checkout_to_issuance_orchestration":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_checkout_to_issuance_flow.py",
                "--public-legal-config",
                "config/public-portal-legal.json",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--license-issuance-prep",
                "manifests/previews/final-real-staging-license-issuance-prep.json",
                "--signed-delivery-prep",
                "manifests/previews/final-real-staging-signed-delivery-prep.json",
                "--selected-plan",
                "Guardian Core Monthly",
                "--payment-method",
                "paypal_business",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_payment_confirmation_and_customer_release":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_checkout_to_issuance_flow.py",
                "--public-legal-config",
                "config/public-portal-legal.json",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--license-issuance-prep",
                "manifests/previews/final-real-staging-license-issuance-prep.json",
                "--signed-delivery-prep",
                "manifests/previews/final-real-staging-signed-delivery-prep.json",
                "--selected-plan",
                "Guardian Core Monthly",
                "--payment-method",
                "paypal_business",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_invoice_confirmation_and_release_decision":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_checkout_to_issuance_flow.py",
                "--public-legal-config",
                "config/public-portal-legal.json",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--license-issuance-prep",
                "manifests/previews/final-real-staging-license-issuance-prep.json",
                "--signed-delivery-prep",
                "manifests/previews/final-real-staging-signed-delivery-prep.json",
                "--selected-plan",
                "Guardian Core Monthly",
                "--payment-method",
                "paypal_business",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_subscription_lifecycle_prep":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_subscription_lifecycle_prep.py",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--checkout-record",
                "manifests/previews/final-real-staging-checkout-record-prep.json",
                "--payment-confirmation",
                "manifests/previews/final-real-staging-payment-confirmation-prep.json",
                "--invoice-confirmation",
                "manifests/previews/final-real-staging-invoice-confirmation-prep.json",
                "--release-decision",
                "manifests/previews/final-real-staging-protected-customer-release-decision.json",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-03-31T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_paypal_business_and_invoice_prep":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_paypal_business_invoice_prep.py",
                "--paypal-config",
                "config/paypal-business.json",
                "--checkout-record",
                "manifests/previews/final-real-staging-checkout-record-prep.json",
                "--install-pack",
                "manifests/previews/final-real-staging-protected-customer-install-pack.json",
                "--output-prefix",
                "manifests/previews/final-real-staging",
                "--built-at",
                "2026-04-01T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_global_productization_readiness":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_global_productization_readiness.py",
                "--output",
                "manifests/previews/final-global-productization-readiness.json",
                "--built-at",
                "2026-04-01T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    elif action == "build_external_cutover_package":
        return _run_subprocess_action(
            workspace_root,
            [
                "python3",
                "tools/build_external_cutover_package.py",
                "--output",
                "manifests/previews/final-external-cutover-package.json",
                "--built-at",
                "2026-04-22T00:00:00Z",
            ],
            console_config.max_action_output_bytes,
        )
    else:
        payload = {"ok": False, "issues": [f"unknown action '{action}'"]}

    if action == "run_schema_checks":
        ok = bool(payload.get("ok", False))
    elif action == "run_dry_run_onboarding":
        ok = not payload["validation"] and not payload["dry_run"] and not payload["transition_preview"]["issues"]
    else:
        ok = not payload.get("issues")

    output = json.dumps(payload, indent=2, sort_keys=True)
    if len(output) > console_config.max_action_output_bytes:
        output = output[: console_config.max_action_output_bytes] + "\n\n... truncated ..."
    return ActionExecutionResult(
        action=action,
        ok=ok,
        output=output,
        returncode=0 if ok else 1,
        timestamp=_now_iso(),
    )


def collect_console_snapshot(
    workspace_root: Path,
    config: AppConfig,
    console_config: LocalConsoleConfig,
    *,
    action_results: dict[str, ActionExecutionResult] | None = None,
) -> dict[str, Any]:
    doctrine = load_doctrine_policy(workspace_root)
    release_channels = load_release_channels(workspace_root)
    backend_defaults = load_backend_defaults(workspace_root)
    previews = build_preview_objects(workspace_root, config)
    ai_governance = collect_ai_governance_status(workspace_root, doctrine.policy)
    latest_json = _read_json_preview(config.reports_dir / "latest.json")
    latest_md = _read_text_preview(config.reports_dir / "latest.md", console_config.max_text_bytes)
    plugin_root = workspace_root / "packages" / "wp-plugin" / "hetzner-seo-ops"

    backend_state = derive_backend_state(
        previews["license_registry_entry"]["binding_state"],
        previews["policy_preview"]["registry_state"],
        previews["rollback_profile_preview"]["registry_state"],
        previews["onboarding_preview"]["state"],
    )

    tests_dir = workspace_root / "tests"
    action_results = action_results or {}
    return {
        "runtime": {
            "workspace_root": str(workspace_root),
            "config_path": str(config.config_path),
            "mode": config.mode,
            "timezone": config.timezone,
            "allow_remote_fetch": config.allow_remote_fetch,
            "allow_external_changes": config.allow_external_changes,
            "allow_workspace_self_healing": config.allow_workspace_self_healing,
            "cycle_interval_minutes": config.cycle_interval_minutes,
            "reports_dir": str(config.reports_dir),
            "database_path": str(config.database_path),
            "database_info": _file_info(config.database_path),
            "reports_info": _file_info(config.reports_dir / "latest.json"),
            "logs_info": _file_info(config.logs_dir / "system.log"),
        },
        "doctrine": {
            "policy_source": doctrine.source,
            "policy_notes": list(doctrine.notes),
            "policy_schema_issues": validate_policy_schema(doctrine.policy),
            "canonical_docs": doctrine.policy.get("canonical_docs", []),
            "allowed_gate_states": doctrine.policy.get("gates", {}).get("allowed_states", []),
            "risk_classes": doctrine.policy.get("ai_management", {}).get("risk_classes", []),
            "required_lifecycle_stages": doctrine.policy.get("lifecycle", {}).get("required_stages", []),
            "blocked_targets": doctrine.policy.get("external_effects", {}).get("blocked_targets", []),
            "local_console_notice": console_config.local_only_notice,
            "console_notes": list(console_config.notes),
        },
        "ai_governance": ai_governance,
        "domain_configuration": {
            "configured_domains": list(config.domains),
            "user_agent": config.user_agent,
            "request_timeout_seconds": config.request_timeout_seconds,
            "max_response_bytes": config.max_response_bytes,
        },
        "reports": {
            "latest_json": latest_json,
            "latest_md": latest_md,
            "rollups": {
                window: _read_json_preview(config.reports_dir / "rollups" / f"{window}.json")
                for window in ("1d", "7d", "30d", "365d")
            },
        },
        "product_core_status": {
            "release_channels_source": release_channels.source,
            "release_channel_issues": validate_release_channels(release_channels.channels),
            "release_channels": release_channels.channels,
            "license_validation_issues": validate_license_object(previews["license_object"], release_channels.channels),
            "domain_binding_issues": validate_domain_binding(previews["domain_binding"], release_channels.channels),
        },
        "plugin_mvp_status": {
            "plugin_root": str(plugin_root),
            "plugin_root_info": _file_info(plugin_root / "hetzner-seo-ops.php"),
            "plugin_file_count": len([path for path in plugin_root.rglob("*") if path.is_file()]),
            "plugin_package_metadata_preview": previews["plugin_package_metadata_preview"],
            "plugin_package_metadata_issues": list(
                validate_plugin_package_metadata(previews["plugin_package_metadata_preview"], release_channels.channels).issues
            ),
            "plugin_runtime_mode": "inert_local_preview_only",
            "rank_math_status": "coexistence_only / no replacement active",
        },
        "backend_core_status": {
            "backend_defaults": backend_defaults,
            "backend_state": asdict(backend_state),
            "license_registry_entry": previews["license_registry_entry"],
            "license_registry_issues": list(
                validate_license_registry_entry(previews["license_registry_entry"], release_channels.channels).issues
            ),
            "policy_preview": previews["policy_preview"],
            "policy_registry_issues": list(
                validate_policy_registry_entry(
                    previews["policy_preview"],
                    release_channels.channels,
                    previews["license_object"],
                ).issues
            ),
            "rollback_profile_preview": previews["rollback_profile_preview"],
            "rollback_registry_issues": list(
                validate_rollback_profile_entry(previews["rollback_profile_preview"], release_channels.channels).issues
            ),
        },
        "packaging_release_preview_status": {
            "manifest_build_request": previews["manifest_build_request"],
            "manifest_preview": previews["manifest_preview"],
            "manifest_preview_issues": previews["manifest_preview_issues"],
            "release_artifact_preview": previews["release_artifact_preview"],
            "release_artifact_issues": previews["release_artifact_issues"],
            "domain_entitlement_preview": previews["domain_entitlement_preview"],
            "domain_entitlement_issues": list(
                validate_domain_entitlement(previews["domain_entitlement_preview"], release_channels.channels).issues
            ),
        },
        "operator_fulfillment_cockpit": build_operator_fulfillment_cockpit(workspace_root),
        "global_productization_readiness": derive_global_productization_readiness(workspace_root),
        "external_cutover_package": build_external_cutover_package(workspace_root),
        "dry_run_onboarding_preview": {
            "onboarding_preview": previews["onboarding_preview"],
            "onboarding_issues": list(
                validate_domain_onboarding_entry(previews["onboarding_preview"], release_channels.channels).issues
            ),
            "dry_run_issues": list(validate_dry_run_onboarding_constraints(previews["onboarding_preview"]).issues),
            "transition_preview": previews["onboarding_transition_preview"],
        },
        "preview_objects": {
            "license_object_preview": previews["license_object"],
            "domain_binding_preview": previews["domain_binding"],
            "policy_preview": previews["policy_preview"],
            "rollback_profile_preview": previews["rollback_profile_preview"],
            "manifest_preview": previews["manifest_preview"],
            "plugin_package_metadata_preview": previews["plugin_package_metadata_preview"],
            "release_artifact_preview": previews["release_artifact_preview"],
            "protected_customer_install_pack_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-install-pack.json"
            ),
            "checkout_record_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-checkout-record-prep.json"
            ),
            "payment_confirmation_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-payment-confirmation-prep.json"
            ),
            "invoice_confirmation_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-invoice-confirmation-prep.json"
            ),
            "customer_release_authorization_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-customer-release-authorization.json"
            ),
            "protected_customer_release_decision_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-protected-customer-release-decision.json"
            ),
            "subscription_lifecycle_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-subscription-lifecycle-prep.json"
            ),
            "renewal_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-renewal-prep.json"
            ),
            "failed_payment_recovery_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-failed-payment-recovery-prep.json"
            ),
            "paypal_business_ops_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-paypal-business-ops-prep.json"
            ),
            "invoice_automation_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-invoice-automation-prep.json"
            ),
            "paypal_webhook_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-paypal-webhook-prep.json"
            ),
            "external_cutover_package_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-external-cutover-package.json"
            ),
            "checkout_to_issuance_orchestration_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-checkout-to-issuance-orchestration.json"
            ),
            "license_issuance_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-license-issuance-prep.json"
            ),
            "signed_delivery_prep_preview": _read_json_preview(
                workspace_root / "manifests" / "previews" / "final-real-staging-signed-delivery-prep.json"
            ),
            "preview_notes": previews["preview_notes"],
        },
        "test_status": {
            "tests": _count_python_tests(tests_dir),
            "available_actions": [
                {"id": action, "label": ACTION_LABELS[action]}
                for action in console_config.allowed_actions
            ],
            "recent_action_results": {
                key: asdict(value) for key, value in action_results.items()
            },
        },
        "local_console": {
            "host": console_config.host,
            "port": console_config.port,
            "url": f"http://{console_config.host}:{console_config.port}/",
            "health_url": f"http://{console_config.host}:{console_config.port}/healthz",
            "local_only_notice": console_config.local_only_notice,
        },
    }


def build_health_payload(workspace_root: Path, config: AppConfig, console_config: LocalConsoleConfig) -> dict[str, Any]:
    return {
        "status": "ok",
        "workspace_root": str(workspace_root),
        "mode": config.mode,
        "host": console_config.host,
        "port": console_config.port,
        "local_only": True,
        "allow_external_changes": config.allow_external_changes,
    }


def render_index_html(snapshot: dict[str, Any], console_config: LocalConsoleConfig) -> str:
    sections = [
        ("Runtime / System Status", "runtime"),
        ("Doctrine / Guardrails / Current Mode", "doctrine"),
        ("Domain Configuration", "domain_configuration"),
        ("Last Reports / latest.md / latest.json", "reports"),
        ("Product Core Status", "product_core_status"),
        ("Plugin MVP Status", "plugin_mvp_status"),
        ("Backend Core Status", "backend_core_status"),
        ("Packaging / Release Preview Status", "packaging_release_preview_status"),
        ("Operator Fulfillment Cockpit", "operator_fulfillment_cockpit"),
        ("Dry Run / Onboarding Preview", "dry_run_onboarding_preview"),
        ("Preview Objects", "preview_objects"),
        ("Test Status", "test_status"),
    ]
    actions_html = "".join(
        f'<button data-action="{html.escape(action["id"])}">{html.escape(action["label"])}</button>'
        for action in snapshot["test_status"]["available_actions"]
    )
    sections_html = "".join(
        f"""
        <section class="panel" data-section="{html.escape(key)}">
          <h2>{html.escape(label)}</h2>
          <pre id="section-{html.escape(key)}">Loading...</pre>
        </section>
        """
        for label, key in sections
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(console_config.title)}</title>
  <style>
    :root {{
      --bg: #f4efe4;
      --panel: #fff9ee;
      --ink: #1f1a17;
      --muted: #6d625b;
      --accent: #9b4d1f;
      --line: #d7c5ad;
      --code: #2f241d;
      --ok: #215732;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Georgia", "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(155, 77, 31, 0.12), transparent 35%),
        linear-gradient(180deg, #f8f2e8 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    header {{
      padding: 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 249, 238, 0.92);
      position: sticky;
      top: 0;
      backdrop-filter: blur(8px);
    }}
    header h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0.02em;
    }}
    .notice {{
      display: inline-block;
      padding: 8px 12px;
      border: 1px solid var(--accent);
      color: var(--accent);
      background: rgba(155, 77, 31, 0.08);
      font-weight: 700;
    }}
    main {{
      padding: 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 18px;
      box-shadow: 0 14px 30px rgba(66, 41, 18, 0.08);
    }}
    .actions {{
      grid-column: 1 / -1;
    }}
    .action-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 14px;
    }}
    button {{
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 700;
    }}
    button:hover {{
      opacity: 0.92;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Courier New", monospace;
      font-size: 13px;
      color: var(--code);
      max-height: 440px;
      overflow: auto;
    }}
    .meta {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(console_config.title)}</h1>
    <div class="notice">{html.escape(console_config.local_only_notice)}</div>
    <div class="meta">Bound to {html.escape(snapshot["local_console"]["url"])}. No external effect, no public bind, no live customer API.</div>
  </header>
  <main>
    <section class="panel actions">
      <h2>Local Test Actions</h2>
      <div class="action-row">{actions_html}</div>
      <pre id="action-output">No action run yet.</pre>
    </section>
    {sections_html}
  </main>
  <script>
    async function loadSnapshot() {{
      const response = await fetch('/api/snapshot');
      const payload = await response.json();
      for (const [key, value] of Object.entries(payload)) {{
        const target = document.getElementById(`section-${{key}}`);
        if (target) {{
          target.textContent = JSON.stringify(value, null, 2);
        }}
      }}
    }}

    async function runAction(action) {{
      const output = document.getElementById('action-output');
      output.textContent = `Running ${{action}}...`;
      const response = await fetch('/api/action', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ action }})
      }});
      const payload = await response.json();
      output.textContent = JSON.stringify(payload, null, 2);
      await loadSnapshot();
    }}

    document.querySelectorAll('button[data-action]').forEach((button) => {{
      button.addEventListener('click', () => runAction(button.dataset.action));
    }});

    loadSnapshot();
  </script>
</body>
</html>"""


class LocalConsoleServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: type[BaseHTTPRequestHandler],
        *,
        workspace_root: Path,
        app_config: AppConfig,
        console_config: LocalConsoleConfig,
    ) -> None:
        super().__init__(server_address, handler_class)
        self.workspace_root = workspace_root
        self.app_config = app_config
        self.console_config = console_config
        self.action_results: dict[str, ActionExecutionResult] = {}
        self.action_lock = threading.Lock()


class LocalConsoleHandler(BaseHTTPRequestHandler):
    server: LocalConsoleServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _client_allowed(self) -> bool:
        client = self.client_address[0]
        return client in {"127.0.0.1", "::1"}

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, body: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _snapshot(self) -> dict[str, Any]:
        with self.server.action_lock:
            action_results = dict(self.server.action_results)
        return collect_console_snapshot(
            self.server.workspace_root,
            self.server.app_config,
            self.server.console_config,
            action_results=action_results,
        )

    def do_GET(self) -> None:
        if not self._client_allowed():
            self._send_json({"error": "local access only"}, status=HTTPStatus.FORBIDDEN)
            return

        if self.path == "/protected/paypal/webhook":
            self._send_json({"error": "method not allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED)
            return

        if self.path == "/healthz":
            self._send_json(
                build_health_payload(
                    self.server.workspace_root,
                    self.server.app_config,
                    self.server.console_config,
                )
            )
            return

        if self.path == "/api/snapshot":
            self._send_json(self._snapshot())
            return

        if self.path == "/":
            self._send_html(render_index_html(self._snapshot(), self.server.console_config))
            return

        self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if not self._client_allowed():
            self._send_json({"error": "local access only"}, status=HTTPStatus.FORBIDDEN)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length)

        if self.path == "/protected/paypal/webhook":
            status, payload = handle_protected_paypal_webhook(
                self.server.workspace_root,
                self.server.app_config,
                method="POST",
                path=self.path,
                headers={key: value for key, value in self.headers.items()},
                body=raw,
                environ=os.environ,
            )
            self._send_json(payload, status=status)
            return

        if self.path != "/api/action":
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=HTTPStatus.BAD_REQUEST)
            return

        action = str(payload.get("action", "")).strip()
        result = execute_local_action(
            action,
            self.server.workspace_root,
            self.server.app_config,
            self.server.console_config,
        )
        with self.server.action_lock:
            self.server.action_results[action] = result
        self._send_json(asdict(result), status=200 if result.ok else 400)


def run_local_console(
    config_path: str | Path = "config/settings.toml",
    *,
    workspace_root: str | Path | None = None,
    host: str | None = None,
    port: int | None = None,
) -> int:
    app_config, _ = load_config(config_path, workspace_root)
    console_config = load_local_console_config(app_config.workspace_root)
    effective_host = console_config.host if host is None else host
    if effective_host not in LOCAL_ONLY_HOSTS:
        raise ValueError("Local console may only bind to 127.0.0.1 or localhost.")
    effective_host = "127.0.0.1"
    effective_port = console_config.port if port is None else int(port)
    server = LocalConsoleServer(
        (effective_host, effective_port),
        LocalConsoleHandler,
        workspace_root=app_config.workspace_root,
        app_config=app_config,
        console_config=LocalConsoleConfig(
            host=effective_host,
            port=effective_port,
            title=console_config.title,
            local_only_notice=console_config.local_only_notice,
            max_text_bytes=console_config.max_text_bytes,
            max_action_output_bytes=console_config.max_action_output_bytes,
            allowed_actions=console_config.allowed_actions,
            notes=console_config.notes,
        ),
    )
    print(f"Local console running at http://{effective_host}:{effective_port}/")
    print("Local only / no external effect")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
