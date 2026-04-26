from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PUBLIC_CHECKOUT_PLANS = (
    "Guardian Core Monthly",
    "Sovereign Enterprise Monthly",
    "Sovereign Critical Monthly",
)

LICENSED_DOMAIN_SCOPE_VALUES = {
    1,
    "commercial_review_required",
    "individual_approval_required",
}


@dataclass(frozen=True)
class FulfillmentValidationResult:
    valid: bool
    issues: tuple[str, ...]


def validate_protected_customer_install_pack(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "pack_id",
        "status",
        "delivery_channel",
        "public_delivery",
        "customer_login",
        "license_api_exposed",
        "bound_domain",
        "package",
        "artifacts",
        "customer_visibility",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"protected customer install pack missing '{key}'")

    if payload.get("public_delivery") is not False:
        issues.append("protected customer install pack must keep public_delivery false")
    if payload.get("customer_login") is not False:
        issues.append("protected customer install pack must keep customer_login false")
    if payload.get("license_api_exposed") is not False:
        issues.append("protected customer install pack must keep license_api_exposed false")

    bound_domain = str(payload.get("bound_domain", "")).strip().lower()
    if bound_domain == "":
        issues.append("protected customer install pack requires a bound_domain")

    package = payload.get("package")
    if not isinstance(package, dict):
        issues.append("protected customer install pack package must be an object")
    else:
        for key in ("archive_path", "package_filename", "plugin_version", "package_sha256", "release_channel"):
            if str(package.get(key, "")).strip() == "":
                issues.append(f"protected customer install pack package missing '{key}'")

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append("protected customer install pack artifacts must be an object")
    else:
        for key in (
            "license_object_path",
            "manifest_path",
            "entitlement_path",
            "rollback_profile_path",
            "validation_checklist_path",
            "install_runbook_path",
            "safe_mode_runbook_path",
        ):
            if str(artifacts.get(key, "")).strip() == "":
                issues.append(f"protected customer install pack artifacts missing '{key}'")

    visibility = payload.get("customer_visibility")
    if not isinstance(visibility, dict):
        issues.append("protected customer install pack customer_visibility must be an object")
    else:
        for key in (
            "license_id",
            "subscription_status",
            "bound_domain",
            "domain_scope_summary",
            "documentation_access",
            "licensed_download_access",
            "license_integrity_state",
            "renewal_state",
            "renewal_window_state",
            "failed_payment_recovery_state",
            "support_state",
            "support_email",
            "activation_state",
        ):
            if str(visibility.get(key, "")).strip() == "":
                issues.append(f"protected customer install pack customer_visibility missing '{key}'")
        visibility_bound_domain = str(visibility.get("bound_domain", "")).strip().lower()
        if bound_domain != "" and visibility_bound_domain != bound_domain:
            issues.append("protected customer install pack customer_visibility.bound_domain does not match bound_domain")

    approval_required_reasons = payload.get("approval_required_reasons")
    if not isinstance(approval_required_reasons, list) or not approval_required_reasons:
        issues.append("protected customer install pack requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_license_issuance_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    for key in (
        "issuance_id",
        "status",
        "license_id",
        "bound_domain",
        "license_object_path",
        "signature_state",
        "signing_key_reference",
        "delivery_grant_id",
        "approval_required_reasons",
    ):
        if key not in payload:
            issues.append(f"license issuance prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("license issuance prep status must stay approval_required")
    if str(payload.get("signature_state", "")).strip() == "":
        issues.append("license issuance prep requires signature_state")
    if str(payload.get("signing_key_reference", "")).strip() == "":
        issues.append("license issuance prep requires signing_key_reference")
    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("license issuance prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_signed_delivery_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "prep_id",
        "status",
        "bound_domain",
        "release_channel",
        "signing",
        "replay_protection",
        "delivery_grant",
        "digests",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"signed delivery prep missing '{key}'")

    signing = payload.get("signing")
    if not isinstance(signing, dict):
        issues.append("signed delivery prep signing must be an object")
    else:
        for key in ("signature_mode", "signature_state", "signing_key_reference", "cleartext_secret_present"):
            if key not in signing:
                issues.append(f"signed delivery prep signing missing '{key}'")
        if signing.get("cleartext_secret_present") is not False:
            issues.append("signed delivery prep must keep cleartext_secret_present false")

    replay = payload.get("replay_protection")
    if not isinstance(replay, dict):
        issues.append("signed delivery prep replay_protection must be an object")
    else:
        for key in ("state", "nonce_strategy", "issued_at_binding", "expires_at_required"):
            if key not in replay:
                issues.append(f"signed delivery prep replay_protection missing '{key}'")

    delivery_grant = payload.get("delivery_grant")
    if not isinstance(delivery_grant, dict):
        issues.append("signed delivery prep delivery_grant must be an object")
    else:
        for key in ("grant_id", "state", "public_delivery", "customer_login", "license_api_exposed"):
            if key not in delivery_grant:
                issues.append(f"signed delivery prep delivery_grant missing '{key}'")
        if delivery_grant.get("public_delivery") is not False:
            issues.append("signed delivery prep delivery_grant must keep public_delivery false")
        if delivery_grant.get("customer_login") is not False:
            issues.append("signed delivery prep delivery_grant must keep customer_login false")
        if delivery_grant.get("license_api_exposed") is not False:
            issues.append("signed delivery prep delivery_grant must keep license_api_exposed false")

    digests = payload.get("digests")
    if not isinstance(digests, dict):
        issues.append("signed delivery prep digests must be an object")
    else:
        for key in ("package_sha256", "manifest_sha256", "license_object_sha256", "entitlement_sha256"):
            if str(digests.get(key, "")).strip() == "":
                issues.append(f"signed delivery prep digests missing '{key}'")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("signed delivery prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_checkout_record_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "order_id",
        "status",
        "selected_plan",
        "price_line",
        "scope_line",
        "bound_domain",
        "licensed_domain_count",
        "documentation_access",
        "licensed_download_access",
        "payment_method",
        "payment_processor_label",
        "invoice_state",
        "customer_contact_state",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"checkout record prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("checkout record prep status must stay approval_required")

    selected_plan = str(payload.get("selected_plan", "")).strip()
    if selected_plan not in PUBLIC_CHECKOUT_PLANS:
        issues.append(
            "checkout record prep selected_plan must be Guardian Core Monthly, "
            "Sovereign Enterprise Monthly or Sovereign Critical Monthly"
        )

    licensed_domain_count = payload.get("licensed_domain_count")
    if licensed_domain_count not in LICENSED_DOMAIN_SCOPE_VALUES:
        issues.append(
            "checkout record prep licensed_domain_count must be 1, commercial_review_required or individual_approval_required"
        )

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("checkout record prep requires a bound_domain")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("checkout record prep payment_method must stay paypal_business")

    if str(payload.get("payment_processor_label", "")).strip() != "PayPal Business":
        issues.append("checkout record prep payment_processor_label must stay PayPal Business")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("checkout record prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_checkout_to_issuance_orchestration(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "orchestration_id",
        "status",
        "bound_domain",
        "selected_plan",
        "payment_method",
        "checkout_record_path",
        "payment_confirmation_path",
        "invoice_confirmation_path",
        "license_issuance_prep_path",
        "signed_delivery_prep_path",
        "install_pack_path",
        "customer_release_authorization_path",
        "protected_customer_release_decision_path",
        "steps",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"checkout to issuance orchestration missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("checkout to issuance orchestration status must stay approval_required")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("checkout to issuance orchestration payment_method must stay paypal_business")

    steps = payload.get("steps")
    if not isinstance(steps, list) or not steps:
        issues.append("checkout to issuance orchestration requires steps")
    else:
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                issues.append(f"checkout to issuance orchestration step {index} must be an object")
                continue
            for key in ("name", "status", "blocking"):
                if key not in step:
                    issues.append(f"checkout to issuance orchestration step {index} missing '{key}'")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("checkout to issuance orchestration requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_payment_confirmation_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "payment_confirmation_id",
        "status",
        "order_id",
        "bound_domain",
        "selected_plan",
        "payment_method",
        "payment_processor_label",
        "payment_confirmation_state",
        "invoice_state",
        "invoice_reference",
        "customer_contact_state",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"payment confirmation prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("payment confirmation prep status must stay approval_required")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("payment confirmation prep payment_method must stay paypal_business")

    if str(payload.get("payment_processor_label", "")).strip() != "PayPal Business":
        issues.append("payment confirmation prep payment_processor_label must stay PayPal Business")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("payment confirmation prep requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("payment confirmation prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_customer_release_authorization(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "authorization_id",
        "status",
        "order_id",
        "bound_domain",
        "selected_plan",
        "payment_confirmation_path",
        "license_issuance_prep_path",
        "signed_delivery_prep_path",
        "install_pack_path",
        "support_handover_state",
        "release_state",
        "customer_release_channel",
        "public_delivery",
        "customer_login",
        "license_api_exposed",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"customer release authorization missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("customer release authorization status must stay approval_required")

    if payload.get("public_delivery") is not False:
        issues.append("customer release authorization must keep public_delivery false")
    if payload.get("customer_login") is not False:
        issues.append("customer release authorization must keep customer_login false")
    if payload.get("license_api_exposed") is not False:
        issues.append("customer release authorization must keep license_api_exposed false")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("customer release authorization requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("customer release authorization requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_invoice_confirmation_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "invoice_confirmation_id",
        "status",
        "order_id",
        "bound_domain",
        "selected_plan",
        "payment_confirmation_path",
        "invoice_state",
        "invoice_reference",
        "invoice_confirmation_state",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"invoice confirmation prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("invoice confirmation prep status must stay approval_required")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("invoice confirmation prep requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("invoice confirmation prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_protected_customer_release_decision(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "decision_id",
        "status",
        "order_id",
        "bound_domain",
        "selected_plan",
        "payment_confirmation_path",
        "invoice_confirmation_path",
        "customer_release_authorization_path",
        "release_decision_state",
        "go_no_go_state",
        "decision_channel",
        "public_delivery",
        "customer_login",
        "license_api_exposed",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"protected customer release decision missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("protected customer release decision status must stay approval_required")

    if payload.get("public_delivery") is not False:
        issues.append("protected customer release decision must keep public_delivery false")
    if payload.get("customer_login") is not False:
        issues.append("protected customer release decision must keep customer_login false")
    if payload.get("license_api_exposed") is not False:
        issues.append("protected customer release decision must keep license_api_exposed false")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("protected customer release decision requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("protected customer release decision requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_subscription_lifecycle_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "lifecycle_id",
        "status",
        "bound_domain",
        "selected_plan",
        "subscription_status",
        "payment_method",
        "renewal_state",
        "renewal_window_state",
        "failed_payment_recovery_state",
        "next_operator_gate",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"subscription lifecycle prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("subscription lifecycle prep status must stay approval_required")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("subscription lifecycle prep payment_method must stay paypal_business")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("subscription lifecycle prep requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("subscription lifecycle prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_renewal_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "renewal_id",
        "status",
        "bound_domain",
        "selected_plan",
        "payment_method",
        "current_subscription_status",
        "renewal_state",
        "renewal_window_state",
        "renewal_delivery_state",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"renewal prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("renewal prep status must stay approval_required")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("renewal prep payment_method must stay paypal_business")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("renewal prep requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("renewal prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_failed_payment_recovery_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "recovery_id",
        "status",
        "bound_domain",
        "payment_method",
        "recovery_state",
        "grace_window_state",
        "customer_release_impact",
        "immediate_site_effect",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"failed payment recovery prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("failed payment recovery prep status must stay approval_required")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("failed payment recovery prep payment_method must stay paypal_business")

    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("failed payment recovery prep requires a bound_domain")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("failed payment recovery prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_paypal_business_ops_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "prep_id",
        "status",
        "payment_method",
        "environment",
        "oauth_token_url",
        "orders_capture_url_template",
        "invoice_create_url",
        "invoice_send_url_template",
        "webhook_verify_url",
        "webhook_listener_candidate",
        "protected_webhook_runtime",
        "local_runtime_verification",
        "client_id_env",
        "client_secret_env",
        "webhook_id_env",
        "cleartext_secrets_present",
        "support_email",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"paypal business ops prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("paypal business ops prep status must stay approval_required")
    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("paypal business ops prep payment_method must stay paypal_business")
    if payload.get("cleartext_secrets_present") is not False:
        issues.append("paypal business ops prep must keep cleartext_secrets_present false")
    for key in ("client_id_env", "client_secret_env", "webhook_id_env", "support_email"):
        if str(payload.get(key, "")).strip() == "":
            issues.append(f"paypal business ops prep requires {key}")
    listener_candidate = payload.get("webhook_listener_candidate")
    if not isinstance(listener_candidate, dict):
        issues.append("paypal business ops prep requires webhook_listener_candidate")
    protected_runtime = payload.get("protected_webhook_runtime")
    if not isinstance(protected_runtime, dict):
        issues.append("paypal business ops prep requires protected_webhook_runtime")
    local_runtime_verification = payload.get("local_runtime_verification")
    if not isinstance(local_runtime_verification, dict):
        issues.append("paypal business ops prep requires local_runtime_verification")
    elif str(local_runtime_verification.get("state", "")).strip() == "":
        issues.append("paypal business ops prep local_runtime_verification requires state")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("paypal business ops prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_invoice_automation_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "automation_id",
        "status",
        "payment_method",
        "selected_plan",
        "bound_domain",
        "support_email",
        "create_draft_state",
        "send_invoice_state",
        "reconcile_payment_state",
        "server_validation_state",
        "server_rollback_state",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"invoice automation prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("invoice automation prep status must stay approval_required")
    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("invoice automation prep payment_method must stay paypal_business")
    if str(payload.get("bound_domain", "")).strip().lower() == "":
        issues.append("invoice automation prep requires a bound_domain")
    if str(payload.get("support_email", "")).strip() == "":
        issues.append("invoice automation prep requires support_email")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("invoice automation prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))


def validate_paypal_webhook_prep(payload: dict[str, Any]) -> FulfillmentValidationResult:
    issues: list[str] = []
    required_root = (
        "webhook_prep_id",
        "status",
        "payment_method",
        "webhook_verify_url",
        "webhook_id_env",
        "listener_candidate_url",
        "listener_candidate_state",
        "listener_candidate_reason",
        "handler_path",
        "handler_state",
        "receiver_runtime_state",
        "verification_runtime_state",
        "replay_protection_runtime_state",
        "env_ref_readiness_state",
        "activation_state",
        "local_runtime_verification",
        "verification_state",
        "event_routing_state",
        "public_route_exposed",
        "approval_required_reasons",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"paypal webhook prep missing '{key}'")

    if str(payload.get("status", "")).strip() != "approval_required":
        issues.append("paypal webhook prep status must stay approval_required")
    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("paypal webhook prep payment_method must stay paypal_business")
    if payload.get("public_route_exposed") is not False:
        issues.append("paypal webhook prep must keep public_route_exposed false")
    if str(payload.get("webhook_id_env", "")).strip() == "":
        issues.append("paypal webhook prep requires webhook_id_env")
    if str(payload.get("listener_candidate_url", "")).strip() == "":
        issues.append("paypal webhook prep requires listener_candidate_url")
    if str(payload.get("listener_candidate_state", "")).strip() == "":
        issues.append("paypal webhook prep requires listener_candidate_state")
    local_runtime_verification = payload.get("local_runtime_verification")
    if not isinstance(local_runtime_verification, dict):
        issues.append("paypal webhook prep requires local_runtime_verification")
    elif str(local_runtime_verification.get("state", "")).strip() == "":
        issues.append("paypal webhook prep local_runtime_verification requires state")

    reasons = payload.get("approval_required_reasons")
    if not isinstance(reasons, list) or not reasons:
        issues.append("paypal webhook prep requires approval_required_reasons")

    return FulfillmentValidationResult(valid=not issues, issues=tuple(issues))
