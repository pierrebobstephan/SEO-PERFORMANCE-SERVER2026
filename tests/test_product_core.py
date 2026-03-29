from pathlib import Path
import unittest

from electri_city_ops.product_core import (
    build_domain_runtime_profile,
    channel_allows_active_scoped,
    domain_matches,
    evaluate_local_plugin_mode,
    load_release_channels,
    validate_domain_binding,
    validate_license_object,
    validate_release_channels,
    validate_scope_value,
    validate_update_manifest,
)


def _sample_license() -> dict[str, object]:
    return {
        "license_id": "lic-001",
        "customer_id": "cust-001",
        "product_id": "hso-plugin",
        "status": "approval_required",
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
        "signature": "signed",
    }


class ProductCoreTests(unittest.TestCase):
    def test_release_channels_config_is_valid(self) -> None:
        result = load_release_channels(Path("."))
        self.assertEqual(result.source, "workspace_file")
        self.assertEqual(validate_release_channels(result.channels), [])

    def test_scope_validation_blocks_global_scope(self) -> None:
        issues = validate_scope_value("global:all-pages")
        self.assertTrue(any("forbidden pattern" in item for item in issues))

    def test_domain_binding_rejects_invalid_channel(self) -> None:
        channels = load_release_channels(Path(".")).channels
        binding = {
            "bound_domain": "example.com",
            "allowed_subdomains": [],
            "allowed_scopes": ["homepage_only"],
            "release_channel": "unknown",
            "policy_channel": "pilot",
            "rollback_profile_id": "rb-001",
        }
        issues = validate_domain_binding(binding, channels)
        self.assertTrue(any("release_channel" in item for item in issues))

    def test_license_object_is_valid_for_sample(self) -> None:
        channels = load_release_channels(Path(".")).channels
        self.assertEqual(validate_license_object(_sample_license(), channels), [])

    def test_build_domain_runtime_profile_returns_expected_values(self) -> None:
        channels = load_release_channels(Path(".")).channels
        profile, issues = build_domain_runtime_profile(_sample_license(), channels)
        self.assertEqual(issues, ())
        assert profile is not None
        self.assertEqual(profile.bound_domain, "example.com")
        self.assertEqual(profile.release_channel, "pilot")
        self.assertIn("homepage_only", profile.allowed_scopes)

    def test_update_manifest_validates_scope_and_channel(self) -> None:
        channels = load_release_channels(Path(".")).channels
        manifest = {
            "product_id": "hso-plugin",
            "plugin_version": "0.1.0",
            "release_channel": "pilot",
            "license_id": "lic-001",
            "bound_domain": "example.com",
            "package_url": "https://example.invalid/download.zip",
            "package_checksum": "abc123",
            "policy_version": "2026-03-29",
            "rollback_version": "0.0.9",
            "allowed_scopes": ["homepage_only"],
            "required_features": ["meta_description"],
            "conflict_blocklist_version": "1",
            "min_plugin_version": "0.1.0",
            "issued_at": "2026-03-29T00:00:00Z",
        }
        self.assertEqual(validate_update_manifest(manifest, channels), [])

    def test_channel_allows_active_scoped_for_stable_and_pilot_only(self) -> None:
        channels = load_release_channels(Path(".")).channels
        self.assertTrue(channel_allows_active_scoped("stable", channels))
        self.assertTrue(channel_allows_active_scoped("pilot", channels))
        self.assertFalse(channel_allows_active_scoped("rollback", channels))

    def test_domain_match_allows_bound_domain_and_allowed_subdomain(self) -> None:
        self.assertTrue(domain_matches("example.com", "example.com", ["www.example.com"]))
        self.assertTrue(domain_matches("www.example.com", "example.com", ["www.example.com"]))
        self.assertFalse(domain_matches("other.example.com", "example.com", ["www.example.com"]))

    def test_plugin_mode_falls_back_to_observe_only_on_domain_mismatch(self) -> None:
        channels = load_release_channels(Path(".")).channels
        decision = evaluate_local_plugin_mode(
            _sample_license(),
            "other.example.com",
            channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "observe_only")

    def test_plugin_mode_stays_approval_required_when_source_mapping_is_unclear(self) -> None:
        channels = load_release_channels(Path(".")).channels
        decision = evaluate_local_plugin_mode(
            _sample_license(),
            "example.com",
            channels,
            known_conflicts=False,
            source_mapping_confirmed=False,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "approval_required")

    def test_plugin_mode_uses_safe_mode_on_conflict(self) -> None:
        channels = load_release_channels(Path(".")).channels
        decision = evaluate_local_plugin_mode(
            _sample_license(),
            "example.com",
            channels,
            known_conflicts=True,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "safe_mode")

    def test_plugin_mode_respects_non_active_release_channel(self) -> None:
        channels = load_release_channels(Path(".")).channels
        license_object = _sample_license()
        license_object["status"] = "active_scoped"
        license_object["domain_binding"]["release_channel"] = "rollback"
        decision = evaluate_local_plugin_mode(
            license_object,
            "example.com",
            channels,
            known_conflicts=False,
            source_mapping_confirmed=True,
            scope_confirmed=True,
        )
        self.assertEqual(decision.mode, "observe_only")


if __name__ == "__main__":
    unittest.main()
