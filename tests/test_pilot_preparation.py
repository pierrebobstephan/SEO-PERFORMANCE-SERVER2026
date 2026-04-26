import json
from pathlib import Path
import unittest

from electri_city_ops.manifest_builder import validate_domain_entitlement, validate_plugin_package_metadata
from electri_city_ops.product_core import (
    load_release_channels,
    validate_domain_binding,
    validate_license_object,
    validate_update_manifest,
)
from electri_city_ops.rollback_registry import validate_rollback_profile_entry


class PilotPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.channels = load_release_channels(self.workspace_root).channels

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_protected_pilot_preview_config_stays_non_public(self) -> None:
        payload = self._load_json("config/protected-pilot-preview.json")
        self.assertEqual(payload["status"], "approval_required")
        self.assertEqual(payload["visibility"], "protected_preview_only")
        self.assertEqual(payload["target_environment"], "staging_wordpress_only")
        self.assertEqual(payload["bound_test_host"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(
            payload["expected_home_url"], "https://wp.electri-c-ity-studios-24-7.com/wordpress/"
        )
        self.assertEqual(payload["url_normalization_status"], "blocked")
        self.assertFalse(payload["installability_preview"]["public_delivery"])

    def test_domain_binding_manifest_and_entitlement_previews_are_valid(self) -> None:
        domain_binding = self._load_json("manifests/previews/first-plugin-pilot-license-domain-match-preview.json")
        manifest = self._load_json("manifests/previews/first-plugin-pilot-manifest-preview.json")
        entitlement = self._load_json("manifests/previews/first-plugin-pilot-entitlement-preview.json")
        self.assertEqual(validate_domain_binding(domain_binding, self.channels), [])
        self.assertEqual(validate_update_manifest(manifest, self.channels), [])
        self.assertTrue(validate_domain_entitlement(entitlement, self.channels).valid)
        self.assertEqual(domain_binding["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(manifest["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(entitlement["bound_domain"], "wp.electri-c-ity-studios-24-7.com")

    def test_staging_test_preview_config_stays_protected_and_requires_inputs(self) -> None:
        payload = self._load_json("config/staging-test-preview.json")
        self.assertEqual(payload["status"], "approval_required")
        self.assertEqual(payload["target_environment"], "staging_wordpress_only")
        self.assertEqual(
            payload["public_wordpress_base_url"], "https://wp.electri-c-ity-studios-24-7.com/wordpress/"
        )
        self.assertEqual(
            payload["scoped_test_page_url"],
            "https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/",
        )
        self.assertEqual(payload["bound_test_host"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(payload["default_mode"], "safe_mode")
        self.assertEqual(payload["fallback_mode"], "observe_only")
        self.assertEqual(payload["url_normalization_status"], "blocked")
        self.assertFalse(payload["public_delivery"])
        self.assertIn("backup_confirmation", payload["required_inputs"])
        self.assertIn("rollback_owner", payload["required_inputs"])
        self.assertEqual(payload["real_test_domain"], "wp.electri-c-ity-studios-24-7.com")

    def test_staging_license_and_rollback_previews_are_valid(self) -> None:
        license_object = self._load_json("manifests/previews/first-real-staging-test-license-object-preview.json")
        rollback_entry = self._load_json("manifests/previews/first-real-staging-test-rollback-profile-preview.json")
        validation_checklist = self._load_json(
            "manifests/previews/first-real-staging-test-validation-checklist-preview.json"
        )
        self.assertEqual(validate_license_object(license_object, self.channels), [])
        self.assertTrue(validate_rollback_profile_entry(rollback_entry, self.channels).valid)
        self.assertEqual(
            license_object["domain_binding"]["bound_domain"], "wp.electri-c-ity-studios-24-7.com"
        )
        self.assertEqual(
            rollback_entry["profile"]["bound_domain"], "wp.electri-c-ity-studios-24-7.com"
        )
        self.assertEqual(validation_checklist["status"], "approval_required")
        self.assertEqual(
            validation_checklist["public_wordpress_base_url"],
            "https://wp.electri-c-ity-studios-24-7.com/wordpress/",
        )
        self.assertEqual(
            validation_checklist["scoped_test_page_url"],
            "https://wp.electri-c-ity-studios-24-7.com/wordpress/beispiel-seite/",
        )
        self.assertIn("fatal error", " ".join(validation_checklist["stop_conditions"]))

    def test_package_and_release_preview_artifacts_are_local_only(self) -> None:
        package_payload = self._load_json("manifests/previews/first-installable-pilot-package-metadata.json")
        package_metadata = self._load_json("manifests/previews/first-installable-pilot-package-metadata.raw.json")
        artifact_payload = self._load_json("manifests/previews/first-plugin-pilot-release-artifact-preview.json")
        self.assertTrue(package_payload["valid"])
        self.assertTrue(validate_plugin_package_metadata(package_metadata, self.channels).valid)
        self.assertEqual(package_metadata["build_mode"], "local_preview_only")
        self.assertTrue(artifact_payload["valid"])
        self.assertEqual(artifact_payload["artifact"]["build_mode"], "local_preview_only")
        self.assertEqual(artifact_payload["artifact"]["release_channel"], "pilot")
        self.assertEqual(
            artifact_payload["artifact"]["manifest"]["bound_domain"], "wp.electri-c-ity-studios-24-7.com"
        )

    def test_staging_and_real_test_docs_exist(self) -> None:
        expected = [
            "docs/public-portal-home-tier-harmonization.md",
            "docs/public-portal-explore-page-harmonization.md",
            "docs/public-portal-page-purpose-map-v2.md",
            "docs/public-portal-navigation-finalization.md",
            "docs/public-portal-crosslink-consistency-plan.md",
            "docs/protected-pilot-path-model.md",
            "docs/first-plugin-pilot-boundaries.md",
            "docs/domain-bound-pilot-package-model.md",
            "docs/protected-test-delivery-model.md",
            "docs/staging-wordpress-test-model.md",
            "docs/test-domain-and-license-scope-plan.md",
            "docs/wordpress-pilot-environment-checklist.md",
            "docs/pre-test-backup-and-rollback-checklist.md",
            "docs/first-installable-pilot-package-plan.md",
            "docs/plugin-pilot-scope-v1.md",
            "docs/plugin-pilot-safemode-defaults.md",
            "docs/plugin-pilot-validation-and-rollback.md",
            "docs/first-real-product-test-plan.md",
            "docs/first-real-product-test-checklist.md",
            "docs/first-real-product-test-success-metrics.md",
            "docs/first-real-product-test-stop-conditions.md",
            "docs/first-real-staging-test-plan.md",
            "docs/first-real-staging-test-checklist.md",
            "docs/first-real-staging-test-scope-v1.md",
            "docs/first-real-staging-test-environment-requirements.md",
            "docs/first-installable-staging-pilot-package.md",
            "docs/staging-pilot-package-boundaries.md",
            "docs/staging-pilot-safemode-defaults.md",
            "docs/staging-pilot-installation-flow.md",
            "docs/first-safe-mode-execution-model.md",
            "docs/first-test-observe-only-metrics.md",
            "docs/first-test-stop-conditions.md",
            "docs/first-test-success-metrics.md",
            "docs/post-test-evaluation-runbook.md",
            "docs/post-test-rollback-rehearsal.md",
            "docs/post-test-learning-capture-model.md",
            "docs/post-test-decision-gates.md",
            "docs/second-staging-test-coexistence-plan.md",
            "docs/rank-math-coexistence-staging-test.md",
            "docs/theme-builder-coexistence-staging-test.md",
            "docs/reference-system-pilot-readiness.md",
            "docs/reference-system-pilot-entry-criteria.md",
            "docs/reference-system-pilot-no-go-conditions.md",
            "docs/controlled-pilot-delivery-rehearsal.md",
            "docs/staging-license-manifest-rehearsal.md",
            "docs/reference-pilot-scope-v2.md",
            "docs/first-real-pilot-report-template.md",
            "docs/go-no-go-board-for-real-pilot.md",
            "docs/real-staging-url-normalization-plan.md",
            "docs/wordpress-public-base-url-readiness.md",
            "docs/real-staging-scope-v1.md",
            "docs/real-staging-example-page-binding.md",
            "docs/real-staging-install-flow.md",
            "docs/real-staging-safe-mode-checklist.md",
            "docs/real-staging-rollback-checklist.md",
            "docs/real-staging-go-no-go-checklist.md",
            "docs/real-staging-input-register.md",
            "docs/real-staging-url-verification-pass.md",
            "docs/real-staging-before-after-template.md",
            "docs/real-staging-coexistence-snapshot.md",
            "docs/first-real-staging-pilot-report-template.md",
            "docs/real-staging-to-reference-pilot-gate.md",
        ]
        for relative_path in expected:
            with self.subTest(path=relative_path):
                self.assertTrue((self.workspace_root / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
