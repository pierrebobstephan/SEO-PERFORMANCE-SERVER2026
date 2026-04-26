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

from electri_city_ops.manifest_builder import build_release_artifact, validate_domain_entitlement
from electri_city_ops.product_core import (
    load_release_channels,
    validate_domain_binding,
    validate_license_object,
    validate_update_manifest,
)
from electri_city_ops.rollback_registry import validate_rollback_profile_entry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build final local real-staging pilot bundle artifacts.")
    parser.add_argument("--package-metadata", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--plugin-version", required=True)
    parser.add_argument("--bound-domain", required=True)
    parser.add_argument("--expected-home-url", required=True)
    parser.add_argument("--scoped-page-url", required=True)
    parser.add_argument("--channel", default="pilot")
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def load_json(path: str) -> dict:
    return json.loads((WORKSPACE_ROOT / path).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    channels = load_release_channels(WORKSPACE_ROOT).channels
    raw_metadata = load_json(args.package_metadata)
    output_prefix = (WORKSPACE_ROOT / args.output_prefix).resolve()
    package_url = f"local://{raw_metadata['package_filename']}"

    domain_binding = {
        "bound_domain": args.bound_domain,
        "allowed_subdomains": [],
        "allowed_scopes": [
            "homepage_only",
            "feature:meta_description",
            "feature:head_diagnostics",
            "feature:structure_visibility_diagnostics",
        ],
        "release_channel": args.channel,
        "policy_channel": args.channel,
        "rollback_profile_id": "rb-final-real-staging-pilot-001",
    }

    license_object = {
        "license_id": "lic-final-real-staging-pilot-001",
        "customer_id": "cust-real-staging-preview-001",
        "product_id": "hso-plugin",
        "status": "approval_required",
        "domain_binding": domain_binding,
        "allowed_features": [
            "meta_description",
            "head_diagnostics",
            "structure_visibility",
        ],
        "issued_at": args.built_at,
        "non_expiring": True,
        "integrity": {
            "signature": "source not yet confirmed",
            "signature_state": "operator_signing_required",
            "signing_key_reference": "local_server_signing_key",
        },
    }

    manifest = {
        "product_id": "hso-plugin",
        "plugin_version": args.plugin_version,
        "release_channel": args.channel,
        "license_id": license_object["license_id"],
        "bound_domain": args.bound_domain,
        "package_url": package_url,
        "package_checksum": raw_metadata["package_sha256"],
        "policy_version": "2026-03-30-final-real-staging-pilot",
        "rollback_version": domain_binding["rollback_profile_id"],
        "allowed_scopes": list(domain_binding["allowed_scopes"]),
        "required_features": list(license_object["allowed_features"]),
        "conflict_blocklist_version": "real-staging-pilot-v1",
        "min_plugin_version": args.plugin_version,
        "issued_at": args.built_at,
    }

    entitlement = {
        "entitlement_id": "ent-final-real-staging-pilot-001",
        "license_id": license_object["license_id"],
        "bound_domain": args.bound_domain,
        "release_channel": args.channel,
        "allowed_package_version": args.plugin_version,
        "allowed_scopes": list(domain_binding["allowed_scopes"]),
        "approval_state": "approval_required",
        "issued_at": args.built_at,
    }

    rollback_profile = {
        "registry_id": "rb-reg-final-real-staging-pilot-001",
        "profile": {
            "rollback_profile_id": domain_binding["rollback_profile_id"],
            "bound_domain": args.bound_domain,
            "release_channel": args.channel,
            "rollback_channel": "rollback",
            "rollback_steps": [
                "deactivate staging-only pilot package",
                "return plugin to observe_only or uninstall",
                f"confirm {args.expected_home_url} and {args.scoped_page_url} return to before-state owner",
            ],
            "verification_checks": [
                "no fatal error after rollback",
                "no duplicate meta output remains present",
                "homepage and scoped page diagnostics match before-state expectations",
            ],
            "abort_triggers": [
                "fatal error",
                "visible page damage",
                "unclear source ownership",
                "rollback no longer reproducible",
            ],
            "issued_at": args.built_at,
        },
        "registry_state": "approval_required",
        "created_at": args.built_at,
    }

    validation_checklist = {
        "status": "approval_required",
        "bound_test_host": args.bound_domain,
        "public_wordpress_base_url": args.expected_home_url,
        "scoped_test_page_url": args.scoped_page_url,
        "checks": [
            "plugin installs without fatal error",
            "plugin activates in safe_mode or observe_only",
            f"no visible page damage on {args.expected_home_url}",
            f"no visible page damage on {args.scoped_page_url}",
            "no duplicate head or meta output",
            "theme, builder and SEO plugin conflicts remain observable",
            "rollback path stays intact",
        ],
        "success_requires": [
            "validierbare diagnostics",
            "no fatal errors",
            "no visible page damage",
            "no unresolved coexistence conflict",
        ],
        "stop_conditions": [
            "fatal error",
            "visible page damage",
            "domain mismatch",
            "scope mismatch",
            "unclear ownership",
            "rollback path broken",
        ],
    }

    issues: list[str] = []
    issues.extend(validate_domain_binding(domain_binding, channels))
    issues.extend(validate_license_object(license_object, channels))
    issues.extend(validate_update_manifest(manifest, channels))
    issues.extend(list(validate_domain_entitlement(entitlement, channels).issues))
    issues.extend(list(validate_rollback_profile_entry(rollback_profile, channels).issues))

    release_artifact, artifact_issues = build_release_artifact(
        raw_metadata,
        manifest,
        entitlement,
        channels,
        artifact_id="art-final-real-staging-pilot-001",
        built_at=args.built_at,
    )
    issues.extend(list(artifact_issues))

    write_json(output_prefix.with_name(output_prefix.name + "-license-domain-match-preview.json"), domain_binding)
    write_json(output_prefix.with_name(output_prefix.name + "-license-object-preview.json"), license_object)
    write_json(output_prefix.with_name(output_prefix.name + "-manifest-preview.json"), manifest)
    write_json(output_prefix.with_name(output_prefix.name + "-entitlement-preview.json"), entitlement)
    write_json(output_prefix.with_name(output_prefix.name + "-rollback-profile-preview.json"), rollback_profile)
    write_json(output_prefix.with_name(output_prefix.name + "-validation-checklist-preview.json"), validation_checklist)
    write_json(
        output_prefix.with_name(output_prefix.name + "-release-artifact-preview.json"),
        {"valid": not issues and release_artifact is not None, "issues": issues, "artifact": release_artifact},
    )
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
