#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.fulfillment import (
    validate_invoice_automation_prep,
    validate_paypal_business_ops_prep,
    validate_paypal_webhook_prep,
)
from electri_city_ops.config import load_config
from electri_city_ops.paypal_business import (
    assess_webhook_listener_candidate,
    build_secret_reference_state,
    validate_paypal_business_config,
)
from electri_city_ops.paypal_webhook_runtime import (
    build_protected_paypal_webhook_runtime_state,
    run_local_paypal_webhook_runtime_self_test,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local PayPal Business and invoice automation prep artifacts.")
    parser.add_argument("--paypal-config", required=True)
    parser.add_argument("--checkout-record", required=True)
    parser.add_argument("--install-pack", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def load_json(relative_path: str) -> dict:
    return json.loads((WORKSPACE_ROOT / relative_path).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    paypal_config = load_json(args.paypal_config)
    checkout_record = load_json(args.checkout_record)
    install_pack = load_json(args.install_pack)
    output_prefix = (WORKSPACE_ROOT / args.output_prefix).resolve()
    app_config, _ = load_config("config/settings.toml", WORKSPACE_ROOT)

    config_validation = validate_paypal_business_config(paypal_config)
    checkout_payload = checkout_record.get("checkout_record_prep", {}) or {}
    install_pack_payload = install_pack.get("install_pack", {}) or {}
    bound_domain = str(install_pack_payload.get("bound_domain", "")).strip().lower()
    selected_plan = str(checkout_payload.get("selected_plan", "")).strip()
    secret_reference_state = build_secret_reference_state(paypal_config, os.environ)
    webhook_listener_candidate = assess_webhook_listener_candidate(paypal_config)
    protected_runtime_state = build_protected_paypal_webhook_runtime_state(WORKSPACE_ROOT, environ=os.environ)
    local_runtime_verification = run_local_paypal_webhook_runtime_self_test(
        WORKSPACE_ROOT,
        app_config=app_config,
    )

    paypal_ops = {
        "prep_id": "paypal-business-final-real-staging-pilot-001",
        "status": "approval_required",
        "payment_method": "paypal_business",
        "environment": str(paypal_config.get("environment", "production")),
        "oauth_token_url": str(paypal_config.get("oauth_token_url", "")),
        "orders_capture_url_template": str(paypal_config.get("orders_capture_url_template", "")),
        "invoice_create_url": str(paypal_config.get("invoice_create_url", "")),
        "invoice_send_url_template": str(paypal_config.get("invoice_send_url_template", "")),
        "webhook_verify_url": str(paypal_config.get("webhook_verify_url", "")),
        "webhook_listener_candidate": webhook_listener_candidate,
        "client_id_env": str(paypal_config.get("client_id_env", "")),
        "client_secret_env": str(paypal_config.get("client_secret_env", "")),
        "webhook_id_env": str(paypal_config.get("webhook_id_env", "")),
        "cleartext_secrets_present": False,
        "support_email": str(paypal_config.get("support_email", "")),
        "subscription_plans": list(paypal_config.get("subscription_plans", [])),
        "secret_reference_state": secret_reference_state,
        "protected_webhook_runtime": protected_runtime_state,
        "local_runtime_verification": local_runtime_verification,
        "server_validation_owner": str(paypal_config.get("server_validation_owner", "server_managed_bridge")),
        "server_rollback_owner": str(paypal_config.get("server_rollback_owner", "server_managed_bridge")),
        "approval_required_reasons": [
            "real PayPal token exchange, order capture and invoice creation stay protected and not customer-public",
            "client id, client secret and webhook id must be injected as environment references outside the repository",
            "real payment execution remains blocked until operator go-live gates and delivery infrastructure are approved",
        ],
        "built_at": args.built_at,
    }

    invoice_automation = {
        "automation_id": "invoice-auto-final-real-staging-pilot-001",
        "status": "approval_required",
        "payment_method": "paypal_business",
        "selected_plan": selected_plan,
        "bound_domain": bound_domain,
        "support_email": str(paypal_config.get("support_email", "")),
        "create_draft_state": "ready_when_server_credentials_present",
        "send_invoice_state": "ready_when_server_credentials_present",
        "reconcile_payment_state": "webhook_and_operator_confirmation_required",
        "server_validation_state": str(paypal_config.get("server_validation_owner", "server_managed_bridge")),
        "server_rollback_state": str(paypal_config.get("server_rollback_owner", "server_managed_bridge")),
        "invoice_currency": str(paypal_config.get("invoice_currency", "EUR")),
        "invoice_note": str(paypal_config.get("invoice_note", "")),
        "checkout_record_path": args.checkout_record,
        "approval_required_reasons": [
            "invoice draft, send and reconciliation stay protected until credentials and webhook verification are present",
            "server-managed validation and rollback remain mandatory before any buyer-facing release is allowed",
            "no public invoice portal, no public checkout and no customer login are exposed in this path",
        ],
        "built_at": args.built_at,
    }

    webhook_prep = {
        "webhook_prep_id": "paypal-webhook-final-real-staging-pilot-001",
        "status": "approval_required",
        "payment_method": "paypal_business",
        "webhook_verify_url": str(paypal_config.get("webhook_verify_url", "")),
        "webhook_id_env": str(paypal_config.get("webhook_id_env", "")),
        "listener_candidate_url": str(webhook_listener_candidate.get("url", "")),
        "listener_candidate_state": str(webhook_listener_candidate.get("state", "")),
        "listener_candidate_reason": str(webhook_listener_candidate.get("reason", "")),
        "listener_candidate_delivery_scope": str(webhook_listener_candidate.get("delivery_scope", "")),
        "listener_candidate_verification_model": str(webhook_listener_candidate.get("verification_model", "")),
        "listener_candidate_replay_protection_expectation": str(
            webhook_listener_candidate.get("replay_protection_expectation", "")
        ),
        "handler_path": str(protected_runtime_state.get("handler_path", "")),
        "handler_state": str(protected_runtime_state.get("handler_state", "")),
        "receiver_runtime_state": str(protected_runtime_state.get("receiver_runtime_state", "")),
        "verification_runtime_state": str(protected_runtime_state.get("verification_runtime_state", "")),
        "replay_protection_runtime_state": str(protected_runtime_state.get("replay_protection_runtime_state", "")),
        "env_ref_readiness_state": str(protected_runtime_state.get("env_ref_readiness_state", "")),
        "activation_state": str(protected_runtime_state.get("activation_state", "")),
        "evidence_log_path": str(protected_runtime_state.get("evidence_log_path", "")),
        "nonce_registry_path": str(protected_runtime_state.get("nonce_registry_path", "")),
        "local_runtime_verification": local_runtime_verification,
        "verification_state": (
            "blocked_by_invalid_listener_candidate"
            if str(webhook_listener_candidate.get("state", "")).strip() in {"invalid_public_portal_page", "invalid_public_receiver_scope"}
            else "implemented_runtime_ready_when_env_refs_present"
        ),
        "event_routing_state": "protected_operator_console_only",
        "public_route_exposed": False,
        "server_validation_state": str(paypal_config.get("server_validation_owner", "server_managed_bridge")),
        "server_rollback_state": str(paypal_config.get("server_rollback_owner", "server_managed_bridge")),
        "approval_required_reasons": [
            "webhook verification remains protected and must not expose a public customer route",
            "event routing stays local or operator-gated until real billing cutover is approved",
            "server-managed validation and rollback must remain intact before webhook-backed automation can go live",
        ],
        "built_at": args.built_at,
    }

    paypal_validation = validate_paypal_business_ops_prep(paypal_ops)
    invoice_validation = validate_invoice_automation_prep(invoice_automation)
    webhook_validation = validate_paypal_webhook_prep(webhook_prep)

    write_json(
        output_prefix.with_name(output_prefix.name + "-paypal-business-ops-prep.json"),
        {
            "config_valid": config_validation.valid,
            "config_issues": list(config_validation.issues),
            "valid": paypal_validation.valid and config_validation.valid,
            "issues": list(paypal_validation.issues),
            "paypal_business_ops_prep": paypal_ops,
            "input_refs": {
                "paypal_config": args.paypal_config,
                "checkout_record": args.checkout_record,
                "install_pack": args.install_pack,
            },
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-invoice-automation-prep.json"),
        {
            "config_valid": config_validation.valid,
            "config_issues": list(config_validation.issues),
            "valid": invoice_validation.valid and config_validation.valid,
            "issues": list(invoice_validation.issues),
            "invoice_automation_prep": invoice_automation,
            "input_refs": {
                "paypal_config": args.paypal_config,
                "checkout_record": args.checkout_record,
                "install_pack": args.install_pack,
            },
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-paypal-webhook-prep.json"),
        {
            "config_valid": config_validation.valid,
            "config_issues": list(config_validation.issues),
            "valid": webhook_validation.valid and config_validation.valid,
            "issues": list(webhook_validation.issues),
            "paypal_webhook_prep": webhook_prep,
            "input_refs": {
                "paypal_config": args.paypal_config,
            },
        },
    )
    return 0 if (config_validation.valid and paypal_validation.valid and invoice_validation.valid and webhook_validation.valid) else 1


if __name__ == "__main__":
    raise SystemExit(main())
