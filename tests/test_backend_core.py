from pathlib import Path
import unittest

from electri_city_ops.backend_core import derive_backend_state, validate_live_productization_gates
from electri_city_ops.manifest_builder import build_update_manifest_preview
from electri_city_ops.onboarding import transition_onboarding_state
from electri_city_ops.product_core import load_release_channels
from electri_city_ops.registry import (
    policy_scopes_are_narrowed,
    prevent_duplicate_license_or_domain,
    validate_license_registry_entry,
    validate_policy_registry_entry,
)
from electri_city_ops.rollback_registry import find_rollback_profile, validate_rollback_profile_entry


def _license_object() -> dict[str, object]:
    return {
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
        "integrity": {
            "signature": "signed",
            "signature_state": "trusted",
            "signing_key_reference": "test-key",
        },
    }


def _license_entry() -> dict[str, object]:
    return {
        "registry_id": "lic-reg-001",
        "license": _license_object(),
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
        "state": "pending",
        "created_at": "2026-03-29T00:00:00Z",
    }


class BackendCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.channels = load_release_channels(Path(".")).channels

    def test_registry_entry_validation(self) -> None:
        result = validate_license_registry_entry(_license_entry(), self.channels)
        self.assertTrue(result.valid)

    def test_duplicate_license_or_domain_is_prevented(self) -> None:
        first = _license_entry()
        second = _license_entry()
        second["registry_id"] = "lic-reg-002"
        result = prevent_duplicate_license_or_domain([first], second)
        self.assertFalse(result.valid)

    def test_policy_scope_narrowing(self) -> None:
        policy = _policy_entry()
        policy["allowed_scopes"] = ["homepage_only", "feature:meta_description", "template:archive.php"]
        result = policy_scopes_are_narrowed(policy, _license_object())
        self.assertFalse(result.valid)

    def test_manifest_build_requires_confirmed_registry_entries(self) -> None:
        request = {
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
        license_entry = _license_entry()
        license_entry["binding_state"] = "pending"
        result = build_update_manifest_preview(
            request,
            license_entry,
            _policy_entry(),
            _rollback_entry(),
            self.channels,
        )
        self.assertFalse(result.valid)

    def test_rollback_profile_lookup(self) -> None:
        lookup = find_rollback_profile([_rollback_entry()], "example.com", "rb-001")
        self.assertTrue(lookup.found)

    def test_onboarding_state_transitions(self) -> None:
        transition = transition_onboarding_state(_onboarding_entry(), "approval_required")
        self.assertTrue(transition.valid)
        assert transition.entry is not None
        self.assertEqual(transition.entry["state"], "approval_required")

    def test_policy_registry_entry_validation(self) -> None:
        result = validate_policy_registry_entry(_policy_entry(), self.channels, _license_object())
        self.assertTrue(result.valid)

    def test_rollback_profile_entry_validation(self) -> None:
        result = validate_rollback_profile_entry(_rollback_entry(), self.channels)
        self.assertTrue(result.valid)

    def test_backend_state_derivation_stays_approval_required_for_confirmed_objects(self) -> None:
        summary = derive_backend_state("confirmed", "confirmed", "confirmed", "confirmed")
        self.assertEqual(summary.state, "approval_required")

    def test_live_productization_gate_completeness(self) -> None:
        gates = {
            "license_registry_confirmed": True,
            "policy_registry_confirmed": True,
            "rollback_registry_confirmed": True,
            "onboarding_confirmed": True,
            "operator_approval_confirmed": True,
            "validation_defined": True,
            "rollback_defined": True,
            "source_mapping_confirmed": True,
        }
        valid, issues = validate_live_productization_gates(gates, workspace_root=Path("."))
        self.assertTrue(valid)
        self.assertEqual(issues, ())


if __name__ == "__main__":
    unittest.main()
