#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.fulfillment import (
    validate_failed_payment_recovery_prep,
    validate_renewal_prep,
    validate_subscription_lifecycle_prep,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local subscription lifecycle prep artifacts.")
    parser.add_argument("--install-pack", required=True)
    parser.add_argument("--checkout-record", required=True)
    parser.add_argument("--payment-confirmation", required=True)
    parser.add_argument("--invoice-confirmation", required=True)
    parser.add_argument("--release-decision", required=True)
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
    install_pack = load_json(args.install_pack)
    checkout_record = load_json(args.checkout_record)
    payment_confirmation = load_json(args.payment_confirmation)
    invoice_confirmation = load_json(args.invoice_confirmation)
    release_decision = load_json(args.release_decision)
    output_prefix = (WORKSPACE_ROOT / args.output_prefix).resolve()

    install_pack_payload = install_pack.get("install_pack", {})
    customer_visibility = install_pack_payload.get("customer_visibility", {}) or {}
    protected_fulfillment = install_pack_payload.get("protected_fulfillment", {}) or {}
    checkout_payload = checkout_record.get("checkout_record_prep", {}) or {}
    payment_payload = payment_confirmation.get("payment_confirmation_prep", {}) or {}
    invoice_payload = invoice_confirmation.get("invoice_confirmation_prep", {}) or {}
    release_decision_payload = release_decision.get("protected_customer_release_decision", {}) or {}
    bound_domain = str(install_pack_payload.get("bound_domain", "")).strip().lower()
    selected_plan = str(checkout_payload.get("selected_plan", "")).strip()
    payment_method = str(payment_payload.get("payment_method", "paypal_business")).strip() or "paypal_business"

    lifecycle = {
        "lifecycle_id": "sub-life-final-real-staging-pilot-001",
        "status": "approval_required",
        "bound_domain": bound_domain,
        "selected_plan": selected_plan,
        "subscription_status": str(customer_visibility.get("subscription_status", "approval_required")),
        "payment_method": payment_method,
        "renewal_state": str(customer_visibility.get("renewal_state", "operator_review_required")),
        "renewal_window_state": str(customer_visibility.get("renewal_window_state", "not_open")),
        "failed_payment_recovery_state": str(
            customer_visibility.get("failed_payment_recovery_state", "not_needed")
        ),
        "next_operator_gate": "real_renewal_billing_and_failed_payment_ops_path",
        "approval_required_reasons": [
            "renewal and failed-payment lifecycle remain operator-gated and outside the workspace",
            "no real billing retry, grace policy or entitlement rotation is executed locally",
            "subscription lifecycle state stays preparatory until real payment and support systems are connected",
        ],
        "built_at": args.built_at,
    }

    renewal = {
        "renewal_id": "renewal-final-real-staging-pilot-001",
        "status": "approval_required",
        "bound_domain": bound_domain,
        "selected_plan": selected_plan,
        "payment_method": payment_method,
        "current_subscription_status": lifecycle["subscription_status"],
        "renewal_state": lifecycle["renewal_state"],
        "renewal_window_state": lifecycle["renewal_window_state"],
        "renewal_delivery_state": str(
            protected_fulfillment.get("renewal_delivery_state", "approval_required")
        ),
        "invoice_confirmation_required": True,
        "release_decision_path": args.release_decision,
        "approval_required_reasons": [
            "real renewal billing and invoice confirmation remain external to the workspace",
            "renewal delivery stays protected and operator-gated",
            "no automatic entitlement extension is enabled in the staging-only path",
        ],
        "built_at": args.built_at,
    }

    recovery = {
        "recovery_id": "recovery-final-real-staging-pilot-001",
        "status": "approval_required",
        "bound_domain": bound_domain,
        "payment_method": payment_method,
        "recovery_state": str(customer_visibility.get("failed_payment_recovery_state", "not_needed")),
        "grace_window_state": "not_started",
        "customer_release_impact": "hold_future_delivery_only",
        "immediate_site_effect": "none",
        "release_decision_state": str(release_decision_payload.get("release_decision_state", "approval_required")),
        "invoice_confirmation_state": str(invoice_payload.get("invoice_confirmation_state", "approval_required")),
        "approval_required_reasons": [
            "failed-payment recovery must not trigger site changes, login changes or public delivery",
            "grace handling, retry logic and release suspension remain external operator processes",
            "no automated cancellation or rollback is executed from the workspace",
        ],
        "built_at": args.built_at,
    }

    lifecycle_validation = validate_subscription_lifecycle_prep(lifecycle)
    renewal_validation = validate_renewal_prep(renewal)
    recovery_validation = validate_failed_payment_recovery_prep(recovery)

    write_json(
        output_prefix.with_name(output_prefix.name + "-subscription-lifecycle-prep.json"),
        {
            "valid": lifecycle_validation.valid,
            "issues": list(lifecycle_validation.issues),
            "subscription_lifecycle_prep": lifecycle,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-renewal-prep.json"),
        {
            "valid": renewal_validation.valid,
            "issues": list(renewal_validation.issues),
            "renewal_prep": renewal,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-failed-payment-recovery-prep.json"),
        {
            "valid": recovery_validation.valid,
            "issues": list(recovery_validation.issues),
            "failed_payment_recovery_prep": recovery,
            "input_refs": {
                "install_pack": args.install_pack,
                "checkout_record": args.checkout_record,
                "payment_confirmation": args.payment_confirmation,
                "invoice_confirmation": args.invoice_confirmation,
                "release_decision": args.release_decision,
            },
        },
    )
    return 0 if (
        lifecycle_validation.valid and renewal_validation.valid and recovery_validation.valid
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
