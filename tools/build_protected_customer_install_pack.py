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

from electri_city_ops.fulfillment import validate_protected_customer_install_pack


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a protected local customer install pack for the bridge plugin.")
    parser.add_argument("--bridge-config", required=True)
    parser.add_argument("--package-metadata", required=True)
    parser.add_argument("--license-object", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--entitlement", required=True)
    parser.add_argument("--rollback-profile", required=True)
    parser.add_argument("--validation-checklist", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def load_json(relative_path: str) -> dict:
    return json.loads((WORKSPACE_ROOT / relative_path).read_text(encoding="utf-8"))


def write_json(relative_path: str, payload: dict) -> None:
    path = WORKSPACE_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    bridge_config = load_json(args.bridge_config)
    package_payload = load_json(args.package_metadata)
    license_object = load_json(args.license_object)
    manifest = load_json(args.manifest)
    entitlement = load_json(args.entitlement)
    rollback_profile = load_json(args.rollback_profile)
    validation_checklist = load_json(args.validation_checklist)

    package_metadata = package_payload.get("metadata", {})
    customer_visibility = dict(bridge_config.get("customer_visibility", {}))
    protected_fulfillment = dict(bridge_config.get("protected_fulfillment", {}))
    bound_domain = str(manifest.get("bound_domain", "")).strip().lower()

    payload = {
        "pack_id": "cust-install-pack-final-real-staging-pilot-001",
        "status": "approval_required",
        "delivery_channel": str(protected_fulfillment.get("delivery_channel", "protected_local_only")),
        "public_delivery": bool(protected_fulfillment.get("public_delivery", False)),
        "customer_login": bool(protected_fulfillment.get("customer_login", False)),
        "license_api_exposed": bool(protected_fulfillment.get("license_api_exposed", False)),
        "bound_domain": bound_domain,
        "package": {
            "archive_path": str(package_payload.get("archive_path", "")),
            "package_filename": str(package_metadata.get("package_filename", "")),
            "plugin_version": str(package_metadata.get("plugin_version", "")),
            "package_sha256": str(package_metadata.get("package_sha256", "")),
            "release_channel": str(package_metadata.get("release_channel", "")),
        },
        "artifacts": {
            "license_object_path": args.license_object,
            "manifest_path": args.manifest,
            "entitlement_path": args.entitlement,
            "rollback_profile_path": args.rollback_profile,
            "validation_checklist_path": args.validation_checklist,
            "install_runbook_path": "docs/real-install-runbook.md",
            "safe_mode_runbook_path": "docs/real-safe-mode-test-runbook.md",
        },
        "customer_visibility": {
            "license_id": str(license_object.get("license_id", "")),
            "subscription_status": str(customer_visibility.get("subscription_status", "approval_required")),
            "renewal_state": str(customer_visibility.get("renewal_state", "operator_review_required")),
            "renewal_window_state": str(customer_visibility.get("renewal_window_state", "not_open")),
            "failed_payment_recovery_state": str(
                customer_visibility.get("failed_payment_recovery_state", "not_needed")
            ),
            "bound_domain": bound_domain,
            "domain_scope_summary": str(customer_visibility.get("domain_scope_summary", "source not yet confirmed")),
            "documentation_access": str(customer_visibility.get("documentation_access", "source not yet confirmed")),
            "licensed_download_access": str(customer_visibility.get("licensed_download_access", "approval_required")),
            "license_integrity_state": str(customer_visibility.get("license_integrity_state", "operator signing required")),
            "support_state": str(customer_visibility.get("support_state", "operator input required")),
            "support_email": str(customer_visibility.get("support_email", "")),
            "activation_state": str(customer_visibility.get("activation_state", "approval_required")),
            "customer_visibility_note": str(customer_visibility.get("customer_visibility_note", "source not yet confirmed")),
            "subscription_lifecycle_note": str(
                customer_visibility.get("subscription_lifecycle_note", "source not yet confirmed")
            ),
        },
        "protected_fulfillment": {
            "install_pack_state": str(protected_fulfillment.get("install_pack_state", "approval_required")),
            "manifest_state": str(protected_fulfillment.get("manifest_state", "approval_required")),
            "rollback_state": str(protected_fulfillment.get("rollback_state", "approval_required")),
            "signing_target": str(protected_fulfillment.get("signing_target", "operator_input_required")),
            "delivery_target": str(protected_fulfillment.get("delivery_target", "operator_input_required")),
            "delivery_grant_rule": str(protected_fulfillment.get("delivery_grant_rule", "operator_input_required")),
            "customer_release_decision_state": str(
                protected_fulfillment.get("customer_release_decision_state", "approval_required")
            ),
            "renewal_delivery_state": str(protected_fulfillment.get("renewal_delivery_state", "approval_required")),
            "failed_payment_recovery_delivery_state": str(
                protected_fulfillment.get("failed_payment_recovery_delivery_state", "approval_required")
            ),
            "expected_home_url": str(bridge_config.get("expected_home_url", "")),
            "expected_scoped_page_url": str(bridge_config.get("expected_scoped_page_url", "")),
        },
        "approval_required_reasons": [
            "real customer fulfillment remains protected and operator-gated",
            "public delivery, login, and open license API remain disabled",
            "staging-only install path still requires validation, rollback, and support ownership",
        ],
        "built_at": args.built_at,
    }

    validation = validate_protected_customer_install_pack(payload)
    output = {
        "valid": validation.valid,
        "issues": list(validation.issues),
        "install_pack": payload,
        "input_refs": {
            "bridge_config": args.bridge_config,
            "package_metadata": args.package_metadata,
            "license_object": args.license_object,
            "manifest": args.manifest,
            "entitlement": args.entitlement,
            "rollback_profile": args.rollback_profile,
            "validation_checklist": args.validation_checklist,
        },
        "license_object_status": str(license_object.get("status", "")),
        "entitlement_approval_state": str(entitlement.get("approval_state", "")),
        "rollback_registry_state": str(rollback_profile.get("registry_state", "")),
        "validation_status": str(validation_checklist.get("status", "")),
    }
    write_json(args.output, output)
    return 0 if validation.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
