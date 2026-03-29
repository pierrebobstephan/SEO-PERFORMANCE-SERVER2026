from pathlib import Path
import unittest

from electri_city_ops.manifest_builder import (
    build_plugin_package_metadata,
    build_release_artifact,
    build_update_manifest_preview,
    validate_domain_entitlement,
    validate_plugin_package_metadata,
)
from electri_city_ops.onboarding import validate_dry_run_onboarding_constraints
from electri_city_ops.product_core import load_release_channels


def _license_entry() -> dict[str, object]:
    return {
        "registry_id": "lic-reg-001",
        "license": {
            "license_id": "lic-001",
            "customer_id": "cust-001",
            "product_id": "hso-plugin",
            "status": "active_scoped",
            "domain_binding": {
                "bound_domain": "example.com",
                "allowed_subdomains": ["www.example.com"],
                "allowed_scopes": ["homepage_only", "feature:meta_description"],
                "release_channel": "pilot",
                "policy_channel": "pilot",
                "rollback_profile_id": "rb-001",
            },
            "allowed_features": ["meta_description"],
            "issued_at": "2026-03-29T00:00:00Z",
            "non_expiring": True,
        },
        "binding_state": "confirmed",
        "source_role": "reference_site",
        "created_at": "2026-03-29T00:00:00Z",
    }


def _policy_entry() -> dict[str, object]:
    return {
        "registry_id": "pol-reg-001",
        "license_id": "lic-001",
        "bound_domain": "example.com",
        "release_channel": "pilot",
        "policy_version": "2026-03-29",
        "default_mode": "approval_required",
        "allowed_scopes": ["homepage_only", "feature:meta_description"],
        "module_flags": {"meta_description": True},
        "rollback_profile_id": "rb-001",
        "registry_state": "confirmed",
        "created_at": "2026-03-29T00:00:00Z",
    }


def _rollback_entry() -> dict[str, object]:
    return {
        "registry_id": "rb-reg-001",
        "profile": {
            "rollback_profile_id": "rb-001",
            "bound_domain": "example.com",
            "release_channel": "pilot",
            "rollback_channel": "rollback",
            "rollback_steps": ["restore previous homepage meta description owner"],
            "verification_checks": ["exactly one meta description remains present"],
            "abort_triggers": ["title or canonical regression detected"],
            "issued_at": "2026-03-29T00:00:00Z",
        },
        "registry_state": "confirmed",
        "created_at": "2026-03-29T00:00:00Z",
    }


def _manifest_request() -> dict[str, object]:
    return {
        "license_id": "lic-001",
        "policy_registry_id": "pol-reg-001",
        "rollback_registry_id": "rb-reg-001",
        "requested_channel": "pilot",
        "plugin_version": "0.0.1-dev",
        "package_basename": "hetzner-seo-ops-0.0.1-dev",
        "min_plugin_version": "0.0.1-dev",
        "conflict_blocklist_version": "1",
        "issued_at": "2026-03-29T00:00:00Z",
    }


def _entitlement() -> dict[str, object]:
    return {
        "entitlement_id": "ent-001",
        "license_id": "lic-001",
        "bound_domain": "example.com",
        "release_channel": "pilot",
        "allowed_package_version": "0.0.1-dev",
        "allowed_scopes": ["homepage_only", "feature:meta_description"],
        "approval_state": "approval_required",
        "issued_at": "2026-03-29T00:00:00Z",
    }


def _onboarding_entry() -> dict[str, object]:
    return {
        "onboarding_id": "onb-001",
        "onboarding": {
            "customer_id": "cust-001",
            "requested_domain": "example.com",
            "requested_channel": "pilot",
            "requested_scopes": ["homepage_only"],
            "site_role": "customer_site",
            "cms_platform": "wordpress",
            "operator_contact_status": "confirmed",
        },
        "state": "approval_required",
        "created_at": "2026-03-29T00:00:00Z",
    }


class ReleaseWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.channels = load_release_channels(Path(".")).channels

    def test_package_metadata_validation(self) -> None:
        metadata = build_plugin_package_metadata(
            Path("packages/wp-plugin/hetzner-seo-ops"),
            plugin_slug="hetzner-seo-ops",
            plugin_version="0.0.1-dev",
            release_channel="pilot",
            built_at="2026-03-29T00:00:00Z",
        )
        result = validate_plugin_package_metadata(metadata, self.channels)
        self.assertTrue(result.valid)

    def test_release_artifact_consistency(self) -> None:
        manifest_result = build_update_manifest_preview(
            _manifest_request(),
            _license_entry(),
            _policy_entry(),
            _rollback_entry(),
            self.channels,
        )
        self.assertTrue(manifest_result.valid)
        assert manifest_result.manifest is not None
        metadata = build_plugin_package_metadata(
            Path("packages/wp-plugin/hetzner-seo-ops"),
            plugin_slug="hetzner-seo-ops",
            plugin_version="0.0.1-dev",
            release_channel="pilot",
            built_at="2026-03-29T00:00:00Z",
        )
        artifact, issues = build_release_artifact(
            metadata,
            manifest_result.manifest,
            _entitlement(),
            self.channels,
            artifact_id="art-001",
            built_at="2026-03-29T00:00:00Z",
        )
        self.assertEqual(issues, ())
        assert artifact is not None
        self.assertEqual(artifact["release_channel"], "pilot")

    def test_entitlement_validation(self) -> None:
        result = validate_domain_entitlement(_entitlement(), self.channels)
        self.assertTrue(result.valid)

    def test_dry_run_onboarding_constraints(self) -> None:
        result = validate_dry_run_onboarding_constraints(_onboarding_entry())
        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()
