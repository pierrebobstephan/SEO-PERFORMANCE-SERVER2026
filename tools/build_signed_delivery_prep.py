#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.fulfillment import validate_license_issuance_prep, validate_signed_delivery_prep


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local signed-delivery-prep and license-issuance-prep artifacts.")
    parser.add_argument("--bridge-config", required=True)
    parser.add_argument("--package-metadata", required=True)
    parser.add_argument("--license-object", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--entitlement", required=True)
    parser.add_argument("--install-pack", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def load_json(relative_path: str) -> dict:
    return json.loads((WORKSPACE_ROOT / relative_path).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256_relative(relative_path: str) -> str:
    digest = hashlib.sha256()
    with (WORKSPACE_ROOT / relative_path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    bridge_config = load_json(args.bridge_config)
    package_payload = load_json(args.package_metadata)
    license_object = load_json(args.license_object)
    manifest = load_json(args.manifest)
    entitlement = load_json(args.entitlement)
    install_pack_payload = load_json(args.install_pack)

    protected_fulfillment = dict(bridge_config.get("protected_fulfillment", {}))
    bound_domain = str(manifest.get("bound_domain", "")).strip().lower()
    release_channel = str(manifest.get("release_channel", "pilot"))
    output_prefix = (WORKSPACE_ROOT / args.output_prefix).resolve()

    delivery_grant = {
        "grant_id": "grant-final-real-staging-pilot-001",
        "state": str(protected_fulfillment.get("delivery_grant_state", "approval_required")),
        "public_delivery": bool(protected_fulfillment.get("public_delivery", False)),
        "customer_login": bool(protected_fulfillment.get("customer_login", False)),
        "license_api_exposed": bool(protected_fulfillment.get("license_api_exposed", False)),
    }

    issuance_prep = {
        "issuance_id": "issuance-final-real-staging-pilot-001",
        "status": "approval_required",
        "license_id": str(license_object.get("license_id", "")),
        "bound_domain": bound_domain,
        "license_object_path": args.license_object,
        "signature_state": str(protected_fulfillment.get("signature_prep_state", "operator_signing_required")),
        "signing_key_reference": str(protected_fulfillment.get("signing_key_reference", "operator_input_required")),
        "signing_target": str(protected_fulfillment.get("signing_target", "operator_input_required")),
        "delivery_grant_id": delivery_grant["grant_id"],
        "install_pack_path": args.install_pack,
        "approval_required_reasons": [
            "real signing keys remain outside the workspace",
            "license issuance stays operator-gated until signing, replay protection, and support ownership are complete",
        ],
        "built_at": args.built_at,
    }

    signed_delivery_prep = {
        "prep_id": "signed-delivery-prep-final-real-staging-pilot-001",
        "status": "approval_required",
        "bound_domain": bound_domain,
        "release_channel": release_channel,
        "signing": {
            "signature_mode": "detached_signature_prep_only",
            "signature_state": str(protected_fulfillment.get("signature_prep_state", "operator_signing_required")),
            "signing_key_reference": str(protected_fulfillment.get("signing_key_reference", "operator_input_required")),
            "signing_target": str(protected_fulfillment.get("signing_target", "operator_input_required")),
            "signature_algorithm": "source not yet confirmed",
            "cleartext_secret_present": False,
        },
        "replay_protection": {
            "state": str(protected_fulfillment.get("replay_protection_state", "operator_input_required")),
            "nonce_strategy": str(protected_fulfillment.get("replay_nonce_strategy", "source not yet confirmed")),
            "issued_at_binding": True,
            "expires_at_required": True,
        },
        "delivery_grant": {
            **delivery_grant,
            "delivery_target": str(protected_fulfillment.get("delivery_target", "operator_input_required")),
            "delivery_grant_rule": str(
                protected_fulfillment.get("delivery_grant_rule", "operator_input_required")
            ),
        },
        "digests": {
            "package_sha256": str(package_payload.get("metadata", {}).get("package_sha256", "")),
            "manifest_sha256": sha256_relative(args.manifest),
            "license_object_sha256": sha256_relative(args.license_object),
            "entitlement_sha256": sha256_relative(args.entitlement),
            "install_pack_sha256": sha256_relative(args.install_pack),
        },
        "approval_required_reasons": [
            "real signing keys and signing service remain outside the workspace",
            "replay protection policy is not yet fully configured",
            "delivery grant remains protected and not customer-public",
        ],
        "built_at": args.built_at,
    }

    issuance_validation = validate_license_issuance_prep(issuance_prep)
    signed_validation = validate_signed_delivery_prep(signed_delivery_prep)

    issuance_output = {
        "valid": issuance_validation.valid,
        "issues": list(issuance_validation.issues),
        "license_issuance_prep": issuance_prep,
        "install_pack_valid": bool(install_pack_payload.get("valid", False)),
    }
    signed_output = {
        "valid": signed_validation.valid,
        "issues": list(signed_validation.issues),
        "signed_delivery_prep": signed_delivery_prep,
        "install_pack_valid": bool(install_pack_payload.get("valid", False)),
    }

    write_json(output_prefix.with_name(output_prefix.name + "-license-issuance-prep.json"), issuance_output)
    write_json(output_prefix.with_name(output_prefix.name + "-signed-delivery-prep.json"), signed_output)
    return 0 if issuance_validation.valid and signed_validation.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
