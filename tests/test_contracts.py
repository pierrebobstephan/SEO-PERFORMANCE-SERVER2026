from pathlib import Path
import unittest

from electri_city_ops.contracts import (
    determine_plugin_handshake,
    validate_customer_domain_onboarding,
    validate_license_check_response,
    validate_plugin_policy_response,
    validate_rollback_profile,
)
from electri_city_ops.product_core import load_release_channels


def _sample_license(status: str = "active_scoped", release_channel: str = "pilot") -> dict[str, object]:
    return {
        "license_id": "lic-001",
        "customer_id": "cust-001",
        "product_id": "hso-plugin",
        "status": status,
        "domain_binding": {
            "bound_domain": "example.com",
            "allowed_subdomains": ["www.example.com"],
            "allowed_scopes": ["homepage_only", "feature:meta_description"],
            "release_channel": release_channel,
            "policy_channel": release_channel,
            "rollback_profile_id": "rb-001",
        },
        "allowed_features": ["meta_description"],
        "issued_at": "2026-03-29T00:00:00Z",
        "non_expiring": True,
    }


def _sample_license_response(status: str = "active_scoped", release_channel: str = "pilot") -> dict[str, object]:
    return {
        "response_status": "ok",
        "signature_status": "trusted",
        "license": _sample_license(status=status, release_channel=release_channel),
        "issued_at": "2026-03-29T00:00:00Z",
    }


def _sample_policy_response(release_channel: str = "pilot") -> dict[str, object]:
    return {
        "license_id": "lic-001",
        "bound_domain": "example.com",
        "release_channel": release_channel,
        "policy_version": "2026-03-29",
        "default_mode": "active_scoped",
        "allowed_scopes": ["homepage_only", "feature:meta_description"],
        "module_flags": {"meta_description": True},
        "rollback_profile_id": "rb-001",
        "issued_at": "2026-03-29T00:00:00Z",
    }


def _sample_rollback_profile(release_channel: str = "pilot") -> dict[str, object]:
    return {
        "rollback_profile_id": "rb-001",
        "bound_domain": "example.com",
        "release_channel": release_channel,
        "rollback_channel": "rollback",
        "rollback_steps": ["restore previous homepage meta description owner"],
        "verification_checks": ["exactly one meta description remains present"],
        "abort_triggers": ["title or canonical regression detected"],
        "issued_at": "2026-03-29T00:00:00Z",
    }


class ContractsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.channels = load_release_channels(Path(".")).channels

    def test_license_check_response_validates_sample(self) -> None:
        result = validate_license_check_response(_sample_license_response(), self.channels)
        self.assertTrue(result.valid)

    def test_policy_response_validates_sample(self) -> None:
        result = validate_plugin_policy_response(_sample_policy_response(), self.channels)
        self.assertTrue(result.valid)

    def test_rollback_profile_validates_sample(self) -> None:
        result = validate_rollback_profile(_sample_rollback_profile(), self.channels)
        self.assertTrue(result.valid)

    def test_onboarding_requires_wordpress_and_scopes(self) -> None:
        result = validate_customer_domain_onboarding(
            {
                "customer_id": "cust-001",
                "requested_domain": "example.com",
                "requested_channel": "pilot",
                "requested_scopes": ["homepage_only"],
                "site_role": "customer_site",
                "cms_platform": "wordpress",
                "operator_contact_status": "confirmed",
            },
            self.channels,
        )
        self.assertTrue(result.valid)

    def test_invalid_license_response_enters_safe_mode(self) -> None:
        decision = determine_plugin_handshake(
            "example.com",
            {"response_status": "invalid"},
            None,
            None,
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "safe_mode")

    def test_mismatched_bound_domain_enters_observe_only(self) -> None:
        decision = determine_plugin_handshake(
            "other.example.com",
            _sample_license_response(),
            _sample_policy_response(),
            _sample_rollback_profile(),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "observe_only")

    def test_missing_policy_response_falls_back_to_observe_only(self) -> None:
        decision = determine_plugin_handshake(
            "example.com",
            _sample_license_response(),
            None,
            _sample_rollback_profile(),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "observe_only")

    def test_missing_rollback_profile_keeps_approval_required(self) -> None:
        decision = determine_plugin_handshake(
            "example.com",
            _sample_license_response(),
            _sample_policy_response(),
            None,
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "approval_required")

    def test_untrusted_license_signature_enters_safe_mode(self) -> None:
        response = _sample_license_response()
        response["signature_status"] = "untrusted"
        decision = determine_plugin_handshake(
            "example.com",
            response,
            _sample_policy_response(),
            _sample_rollback_profile(),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "safe_mode")

    def test_policy_default_mode_can_keep_observe_only(self) -> None:
        policy = _sample_policy_response()
        policy["default_mode"] = "observe_only"
        decision = determine_plugin_handshake(
            "example.com",
            _sample_license_response(),
            policy,
            _sample_rollback_profile(),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "observe_only")

    def test_stable_and_pilot_channels_are_interpreted(self) -> None:
        pilot = determine_plugin_handshake(
            "example.com",
            _sample_license_response(release_channel="pilot"),
            _sample_policy_response(release_channel="pilot"),
            _sample_rollback_profile(release_channel="pilot"),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        stable = determine_plugin_handshake(
            "example.com",
            _sample_license_response(release_channel="stable"),
            _sample_policy_response(release_channel="stable"),
            _sample_rollback_profile(release_channel="stable"),
            self.channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(pilot.channel, "pilot")
        self.assertEqual(stable.channel, "stable")
        self.assertEqual(pilot.mode, "active_scoped")
        self.assertEqual(stable.mode, "active_scoped")


if __name__ == "__main__":
    unittest.main()
