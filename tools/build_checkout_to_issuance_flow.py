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
    PUBLIC_CHECKOUT_PLANS,
    validate_invoice_confirmation_prep,
    validate_protected_customer_release_decision,
    validate_customer_release_authorization,
    validate_checkout_record_prep,
    validate_checkout_to_issuance_orchestration,
    validate_payment_confirmation_prep,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local checkout-to-issuance orchestration preview.")
    parser.add_argument("--public-legal-config", required=True)
    parser.add_argument("--install-pack", required=True)
    parser.add_argument("--license-issuance-prep", required=True)
    parser.add_argument("--signed-delivery-prep", required=True)
    parser.add_argument("--selected-plan", default="Guardian Core Monthly")
    parser.add_argument("--payment-method", default="paypal_business")
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def load_json(relative_path: str) -> dict:
    return json.loads((WORKSPACE_ROOT / relative_path).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def select_plan_terms(public_legal: dict, selected_plan: str) -> dict:
    sections = public_legal.get("pages", {}).get("terms", {}).get("sections", [])
    for section in sections:
        if str(section.get("heading", "")).strip() == selected_plan:
            return section
    raise ValueError(f"selected plan '{selected_plan}' not found in public legal config")


def infer_domain_count(scope_line: str) -> int | str:
    normalized = scope_line.lower()
    if "one exact licensed domain" in normalized and "domain set" not in normalized:
        return 1
    if "commercial review" in normalized or "commercially reviewed" in normalized:
        return "commercial_review_required"
    if "individually approved" in normalized or "high-compliance" in normalized:
        return "individual_approval_required"
    raise ValueError(f"could not infer licensed domain scope value from '{scope_line}'")


def payment_processor_label(payment_method: str) -> str:
    if payment_method == "paypal_business":
        return "PayPal Business"
    return "Operator Confirmed Payment Method"


def main() -> int:
    args = parse_args()
    if args.selected_plan not in PUBLIC_CHECKOUT_PLANS:
        raise ValueError(
            "selected plan must be Guardian Core Monthly, Sovereign Enterprise Monthly or Sovereign Critical Monthly"
        )
    public_legal = load_json(args.public_legal_config)
    install_pack = load_json(args.install_pack)
    issuance_prep = load_json(args.license_issuance_prep)
    signed_delivery_prep = load_json(args.signed_delivery_prep)
    output_prefix = (WORKSPACE_ROOT / args.output_prefix).resolve()

    plan_section = select_plan_terms(public_legal, args.selected_plan)
    paragraphs = list(plan_section.get("paragraphs", []))
    price_line = str(paragraphs[0]) if len(paragraphs) > 0 else ""
    scope_line = str(paragraphs[1]) if len(paragraphs) > 1 else ""
    included_line = str(paragraphs[2]) if len(paragraphs) > 2 else ""
    short_copy = str(paragraphs[3]) if len(paragraphs) > 3 else ""

    install_pack_payload = install_pack.get("install_pack", {})
    issuance_payload = issuance_prep.get("license_issuance_prep", {})
    signed_payload = signed_delivery_prep.get("signed_delivery_prep", {})
    bound_domain = str(install_pack_payload.get("bound_domain", "")).strip().lower()
    invoices_note = str(public_legal.get("identity", {}).get("invoices_note", "")).strip()
    customer_visibility = install_pack_payload.get("customer_visibility", {}) or {}
    support_state = str(customer_visibility.get("support_state", "operator_input_required"))
    support_email = str(customer_visibility.get("support_email", "")).strip()

    checkout_record = {
        "order_id": "order-final-real-staging-pilot-001",
        "status": "approval_required",
        "selected_plan": args.selected_plan,
        "price_line": price_line,
        "scope_line": scope_line,
        "included_line": included_line,
        "short_public_copy": short_copy,
        "bound_domain": bound_domain,
        "licensed_domain_count": infer_domain_count(scope_line),
        "documentation_access": (install_pack_payload.get("customer_visibility", {}) or {}).get("documentation_access", ""),
        "licensed_download_access": (install_pack_payload.get("customer_visibility", {}) or {}).get("licensed_download_access", ""),
        "invoice_state": "approval_required",
        "customer_contact_state": "email_support_active" if support_email else "operator_input_required",
        "support_state": support_state,
        "support_email": support_email,
        "activation_state": (install_pack_payload.get("customer_visibility", {}) or {}).get("activation_state", ""),
        "payment_method": args.payment_method,
        "payment_processor_label": payment_processor_label(args.payment_method),
        "approval_required_reasons": [
            "no real checkout processor is connected in the workspace",
            "real invoice issuance and payment confirmation remain outside the local preview path",
            "customer contact and fulfillment confirmation still require operator review",
        ],
        "built_at": args.built_at,
    }

    payment_confirmation = {
        "payment_confirmation_id": "payment-final-real-staging-pilot-001",
        "status": "approval_required",
        "order_id": checkout_record["order_id"],
        "bound_domain": bound_domain,
        "selected_plan": args.selected_plan,
        "payment_method": args.payment_method,
        "payment_processor_label": payment_processor_label(args.payment_method),
        "payment_confirmation_state": "approval_required",
        "invoice_state": "approval_required",
        "invoice_reference": "operator_input_required",
        "invoice_policy_note": invoices_note,
        "customer_contact_state": checkout_record["customer_contact_state"],
        "support_email": support_email,
        "payer_identity_state": "operator_input_required",
        "release_authorization_precondition": "payment_and_invoice_confirmation_required",
        "approval_required_reasons": [
            "real PayPal Business confirmation is not performed inside the workspace",
            "invoice issuance remains operator-gated and external to the local preview path",
            "payer identity and order confirmation still require operator review",
        ],
        "built_at": args.built_at,
    }

    payment_confirmation_path = output_prefix.with_name(
        output_prefix.name + "-payment-confirmation-prep.json"
    ).relative_to(WORKSPACE_ROOT).as_posix()
    invoice_confirmation_path = output_prefix.with_name(
        output_prefix.name + "-invoice-confirmation-prep.json"
    ).relative_to(WORKSPACE_ROOT).as_posix()
    customer_release_authorization_path = output_prefix.with_name(
        output_prefix.name + "-customer-release-authorization.json"
    ).relative_to(WORKSPACE_ROOT).as_posix()
    release_decision_path = output_prefix.with_name(
        output_prefix.name + "-protected-customer-release-decision.json"
    ).relative_to(WORKSPACE_ROOT).as_posix()

    invoice_confirmation = {
        "invoice_confirmation_id": "invoice-final-real-staging-pilot-001",
        "status": "approval_required",
        "order_id": checkout_record["order_id"],
        "bound_domain": bound_domain,
        "selected_plan": args.selected_plan,
        "payment_confirmation_path": payment_confirmation_path,
        "invoice_state": "approval_required",
        "invoice_reference": "operator_input_required",
        "invoice_confirmation_state": "approval_required",
        "invoice_policy_note": invoices_note,
        "operator_review_owner": "server_managed_bridge",
        "support_email": support_email,
        "approval_required_reasons": [
            "real invoice confirmation remains outside the workspace",
            "invoice reference and completed-order evidence still require operator review",
            "invoice confirmation must precede any protected customer release decision",
        ],
        "built_at": args.built_at,
    }

    customer_release_authorization = {
        "authorization_id": "customer-release-final-real-staging-pilot-001",
        "status": "approval_required",
        "order_id": checkout_record["order_id"],
        "bound_domain": bound_domain,
        "selected_plan": args.selected_plan,
        "payment_confirmation_path": payment_confirmation_path,
        "license_issuance_prep_path": args.license_issuance_prep,
        "signed_delivery_prep_path": args.signed_delivery_prep,
        "install_pack_path": args.install_pack,
        "support_handover_state": "email_support_active" if support_email else "operator_input_required",
        "support_email": support_email,
        "release_state": "approval_required",
        "customer_release_channel": "protected_operator_delivery_only",
        "public_delivery": False,
        "customer_login": False,
        "license_api_exposed": False,
        "approval_required_reasons": [
            "customer release stays protected until payment, invoice and support ownership are confirmed",
            "no public delivery, customer login or open license API is enabled in the workspace",
            "operator release authorization must remain separate from local preview preparation",
        ],
        "built_at": args.built_at,
    }

    protected_customer_release_decision = {
        "decision_id": "release-decision-final-real-staging-pilot-001",
        "status": "approval_required",
        "order_id": checkout_record["order_id"],
        "bound_domain": bound_domain,
        "selected_plan": args.selected_plan,
        "payment_confirmation_path": payment_confirmation_path,
        "invoice_confirmation_path": invoice_confirmation_path,
        "customer_release_authorization_path": customer_release_authorization_path,
        "release_decision_state": "approval_required",
        "go_no_go_state": "operator_review_required",
        "decision_channel": "protected_operator_go_no_go_only",
        "public_delivery": False,
        "customer_login": False,
        "license_api_exposed": False,
        "support_handover_state": "email_support_active" if support_email else "operator_input_required",
        "support_email": support_email,
        "rollback_readiness_state": "server_managed_bridge",
        "validation_readiness_state": "server_managed_bridge",
        "approval_required_reasons": [
            "protected customer release decision stays operator-gated until payment and invoice are confirmed",
            "support handover and rollback ownership still require explicit operator confirmation",
            "no public delivery, customer login or open license API is enabled in the workspace",
        ],
        "built_at": args.built_at,
    }

    orchestration = {
        "orchestration_id": "orchestr-final-real-staging-pilot-001",
        "status": "approval_required",
        "bound_domain": bound_domain,
        "selected_plan": args.selected_plan,
        "payment_method": args.payment_method,
        "checkout_record_path": output_prefix.with_name(output_prefix.name + "-checkout-record-prep.json").relative_to(WORKSPACE_ROOT).as_posix(),
        "payment_confirmation_path": payment_confirmation_path,
        "invoice_confirmation_path": invoice_confirmation_path,
        "license_issuance_prep_path": args.license_issuance_prep,
        "signed_delivery_prep_path": args.signed_delivery_prep,
        "install_pack_path": args.install_pack,
        "customer_release_authorization_path": customer_release_authorization_path,
        "protected_customer_release_decision_path": release_decision_path,
        "steps": [
            {"name": "public_plan_selected", "status": "local_preview_ready", "blocking": False},
            {"name": "checkout_record_prepared", "status": "local_preview_ready", "blocking": False},
            {"name": "payment_confirmation_prepared", "status": "local_preview_ready", "blocking": False},
            {"name": "invoice_confirmation_prepared", "status": "local_preview_ready", "blocking": False},
            {"name": "customer_contact_verified", "status": "operator_input_required", "blocking": True},
            {"name": "invoice_and_payment_confirmed", "status": "approval_required", "blocking": True},
            {"name": "license_issuance_prepared", "status": str(issuance_payload.get("status", "approval_required")), "blocking": True},
            {"name": "signed_delivery_prepared", "status": str(signed_payload.get("status", "approval_required")), "blocking": True},
            {"name": "protected_install_pack_ready", "status": str(install_pack_payload.get("status", "approval_required")), "blocking": True},
            {"name": "customer_release_authorization_prepared", "status": "local_preview_ready", "blocking": False},
            {"name": "protected_customer_release_decision_prepared", "status": "local_preview_ready", "blocking": False},
            {"name": "customer_release_authorized", "status": "approval_required", "blocking": True},
        ],
        "current_gate": "operator_review_before_real_paypal_confirmation_invoice_confirmation_and_customer_release_decision",
        "approval_required_reasons": [
            "checkout, invoice, PayPal Business confirmation and customer verification remain outside the local preview path",
            "signed delivery and protected release remain operator-gated",
            "global customer release requires real support, legal, delivery and rollback operations",
        ],
        "built_at": args.built_at,
    }

    checkout_validation = validate_checkout_record_prep(checkout_record)
    payment_confirmation_validation = validate_payment_confirmation_prep(payment_confirmation)
    invoice_confirmation_validation = validate_invoice_confirmation_prep(invoice_confirmation)
    customer_release_authorization_validation = validate_customer_release_authorization(customer_release_authorization)
    release_decision_validation = validate_protected_customer_release_decision(protected_customer_release_decision)
    orchestration_validation = validate_checkout_to_issuance_orchestration(orchestration)

    write_json(
        output_prefix.with_name(output_prefix.name + "-checkout-record-prep.json"),
        {
            "valid": checkout_validation.valid,
            "issues": list(checkout_validation.issues),
            "checkout_record_prep": checkout_record,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-payment-confirmation-prep.json"),
        {
            "valid": payment_confirmation_validation.valid,
            "issues": list(payment_confirmation_validation.issues),
            "payment_confirmation_prep": payment_confirmation,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-invoice-confirmation-prep.json"),
        {
            "valid": invoice_confirmation_validation.valid,
            "issues": list(invoice_confirmation_validation.issues),
            "invoice_confirmation_prep": invoice_confirmation,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-customer-release-authorization.json"),
        {
            "valid": customer_release_authorization_validation.valid,
            "issues": list(customer_release_authorization_validation.issues),
            "customer_release_authorization": customer_release_authorization,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-protected-customer-release-decision.json"),
        {
            "valid": release_decision_validation.valid,
            "issues": list(release_decision_validation.issues),
            "protected_customer_release_decision": protected_customer_release_decision,
        },
    )
    write_json(
        output_prefix.with_name(output_prefix.name + "-checkout-to-issuance-orchestration.json"),
        {
            "valid": orchestration_validation.valid,
            "issues": list(orchestration_validation.issues),
            "checkout_to_issuance_orchestration": orchestration,
            "input_refs": {
                "public_legal_config": args.public_legal_config,
                "install_pack": args.install_pack,
                "license_issuance_prep": args.license_issuance_prep,
                "signed_delivery_prep": args.signed_delivery_prep,
                "payment_method": args.payment_method,
            },
        },
    )
    return 0 if (
        checkout_validation.valid
        and payment_confirmation_validation.valid
        and invoice_confirmation_validation.valid
        and customer_release_authorization_validation.valid
        and release_decision_validation.valid
        and orchestration_validation.valid
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
