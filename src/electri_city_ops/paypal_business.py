from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class PayPalBusinessValidationResult:
    valid: bool
    issues: tuple[str, ...]


def load_paypal_business_config(workspace_root: Path, relative_path: str = "config/paypal-business.json") -> dict[str, Any]:
    return json.loads((workspace_root / relative_path).read_text(encoding="utf-8"))


def validate_paypal_business_config(payload: dict[str, Any]) -> PayPalBusinessValidationResult:
    issues: list[str] = []
    required_root = (
        "payment_method",
        "environment",
        "api_base",
        "oauth_token_url",
        "orders_capture_url_template",
        "invoice_create_url",
        "invoice_send_url_template",
        "webhook_verify_url",
        "webhook_listener_candidate_url",
        "webhook_listener_candidate_state",
        "webhook_delivery_scope",
        "webhook_verification_model",
        "webhook_replay_protection_expectation",
        "webhook_activation_state",
        "env_load_point",
        "env_load_mode",
        "client_id_env",
        "client_secret_env",
        "webhook_id_env",
        "cleartext_secrets_present",
        "support_email",
        "invoice_currency",
        "invoice_note",
        "subscription_plans",
        "server_validation_owner",
        "server_rollback_owner",
        "public_checkout_exposed",
        "public_invoice_portal_exposed",
        "public_webhook_route_exposed",
    )
    for key in required_root:
        if key not in payload:
            issues.append(f"paypal business config missing '{key}'")

    if str(payload.get("payment_method", "")).strip() != "paypal_business":
        issues.append("paypal business config payment_method must stay paypal_business")

    environment = str(payload.get("environment", "")).strip()
    if environment not in {"production", "sandbox"}:
        issues.append("paypal business config environment must be production or sandbox")

    api_base = str(payload.get("api_base", "")).strip()
    expected_base = "https://api-m.paypal.com" if environment == "production" else "https://api-m.sandbox.paypal.com"
    if api_base != expected_base:
        issues.append("paypal business config api_base does not match the configured environment")

    for key in (
        "oauth_token_url",
        "orders_capture_url_template",
        "invoice_create_url",
        "invoice_send_url_template",
        "webhook_verify_url",
    ):
        value = str(payload.get(key, "")).strip()
        if value == "":
            issues.append(f"paypal business config requires {key}")
        elif not value.startswith(expected_base):
            issues.append(f"paypal business config {key} must use {expected_base}")

    for key in ("client_id_env", "client_secret_env", "webhook_id_env"):
        value = str(payload.get(key, "")).strip()
        if value == "":
            issues.append(f"paypal business config requires {key}")
        elif " " in value:
            issues.append(f"paypal business config {key} must be an environment variable name")

    webhook_listener_candidate_url = str(payload.get("webhook_listener_candidate_url", "")).strip()
    if webhook_listener_candidate_url == "":
        issues.append("paypal business config requires webhook_listener_candidate_url")
    elif not webhook_listener_candidate_url.startswith("https://"):
        issues.append("paypal business config webhook_listener_candidate_url must use https")
    elif "/protected/paypal/webhook" not in webhook_listener_candidate_url:
        issues.append("paypal business config webhook_listener_candidate_url must point to the protected PayPal receiver path")

    if str(payload.get("webhook_listener_candidate_state", "")).strip() != "modeled_protected_candidate":
        issues.append("paypal business config webhook_listener_candidate_state must stay modeled_protected_candidate")
    if str(payload.get("webhook_delivery_scope", "")).strip() != "paypal_billing_events_only":
        issues.append("paypal business config webhook_delivery_scope must stay paypal_billing_events_only")
    if str(payload.get("webhook_verification_model", "")).strip() == "":
        issues.append("paypal business config requires webhook_verification_model")
    if str(payload.get("webhook_replay_protection_expectation", "")).strip() == "":
        issues.append("paypal business config requires webhook_replay_protection_expectation")
    if str(payload.get("webhook_activation_state", "")).strip() != "approval_required":
        issues.append("paypal business config webhook_activation_state must stay approval_required")

    env_load_point = str(payload.get("env_load_point", "")).strip()
    if env_load_point == "":
        issues.append("paypal business config requires env_load_point")
    elif not env_load_point.startswith("deploy/"):
        issues.append("paypal business config env_load_point must stay inside deploy/")

    if str(payload.get("env_load_mode", "")).strip() != "systemd_environment_file":
        issues.append("paypal business config env_load_mode must stay systemd_environment_file")

    if payload.get("cleartext_secrets_present") is not False:
        issues.append("paypal business config must keep cleartext_secrets_present false")
    if str(payload.get("support_email", "")).strip() == "":
        issues.append("paypal business config requires support_email")
    if str(payload.get("invoice_currency", "")).strip() != "EUR":
        issues.append("paypal business config invoice_currency must stay EUR")

    subscription_plans = payload.get("subscription_plans")
    if not isinstance(subscription_plans, list) or not subscription_plans:
        issues.append("paypal business config requires subscription_plans")
    else:
        for index, plan in enumerate(subscription_plans):
            if not isinstance(plan, dict):
                issues.append(f"paypal business config subscription_plans[{index}] must be an object")
                continue
            for key in ("plan_id", "plan_name", "product_label", "status"):
                if str(plan.get(key, "")).strip() == "":
                    issues.append(f"paypal business config subscription_plans[{index}] missing '{key}'")
            if not str(plan.get("plan_id", "")).strip().startswith("P-"):
                issues.append(f"paypal business config subscription_plans[{index}] plan_id must start with 'P-'")
            if str(plan.get("status", "")).strip() != "activated":
                issues.append(f"paypal business config subscription_plans[{index}] status must stay activated")

    for key in ("server_validation_owner", "server_rollback_owner"):
        if str(payload.get(key, "")).strip() != "server_managed_bridge":
            issues.append(f"paypal business config {key} must stay server_managed_bridge")
    for key in ("public_checkout_exposed", "public_invoice_portal_exposed", "public_webhook_route_exposed"):
        if payload.get(key) is not False:
            issues.append(f"paypal business config must keep {key} false")

    return PayPalBusinessValidationResult(valid=not issues, issues=tuple(issues))


def build_secret_reference_state(
    payload: dict[str, Any],
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = environ or {}
    client_id_env = str(payload.get("client_id_env", "")).strip()
    client_secret_env = str(payload.get("client_secret_env", "")).strip()
    webhook_id_env = str(payload.get("webhook_id_env", "")).strip()
    return {
        "env_load_point": str(payload.get("env_load_point", "")).strip(),
        "env_load_mode": str(payload.get("env_load_mode", "")).strip(),
        "client_id_env": client_id_env,
        "client_secret_env": client_secret_env,
        "webhook_id_env": webhook_id_env,
        "client_id_present": bool(client_id_env and env.get(client_id_env)),
        "client_secret_present": bool(client_secret_env and env.get(client_secret_env)),
        "webhook_id_present": bool(webhook_id_env and env.get(webhook_id_env)),
        "cleartext_secrets_present": bool(payload.get("cleartext_secrets_present", True)),
    }


def assess_webhook_listener_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("webhook_listener_candidate_url", "")).strip()
    delivery_scope = str(payload.get("webhook_delivery_scope", "")).strip()
    verification_model = str(payload.get("webhook_verification_model", "")).strip()
    replay_protection_expectation = str(payload.get("webhook_replay_protection_expectation", "")).strip()
    candidate_state = str(payload.get("webhook_listener_candidate_state", "")).strip()
    if url == "":
        return {
            "url": "",
            "state": "operator_input_required",
            "reason": "no webhook listener candidate URL is configured",
            "delivery_scope": delivery_scope,
            "verification_model": verification_model,
            "replay_protection_expectation": replay_protection_expectation,
        }
    if url.rstrip("/").endswith("/buy"):
        return {
            "url": url,
            "state": "invalid_public_portal_page",
            "reason": "the configured candidate points to the public buy page and is not a valid webhook receiver",
            "delivery_scope": delivery_scope,
            "verification_model": verification_model,
            "replay_protection_expectation": replay_protection_expectation,
        }
    if "/protected/" not in url:
        return {
            "url": url,
            "state": "invalid_public_receiver_scope",
            "reason": "the configured candidate is not separated into a protected receiver scope",
            "delivery_scope": delivery_scope,
            "verification_model": verification_model,
            "replay_protection_expectation": replay_protection_expectation,
        }
    if candidate_state != "modeled_protected_candidate":
        return {
            "url": url,
            "state": "operator_input_required",
            "reason": "the protected webhook receiver candidate state is not fully modeled yet",
            "delivery_scope": delivery_scope,
            "verification_model": verification_model,
            "replay_protection_expectation": replay_protection_expectation,
        }
    return {
        "url": url,
        "state": "protected_receiver_candidate_modeled",
        "reason": "the candidate URL is separated from public portal pages and modeled as a protected server-side webhook receiver, but it is not yet verified in a real server context",
        "delivery_scope": delivery_scope,
        "verification_model": verification_model,
        "replay_protection_expectation": replay_protection_expectation,
        "public_page_separated": True,
    }
