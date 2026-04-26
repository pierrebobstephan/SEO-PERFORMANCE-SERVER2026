import json
from pathlib import Path
import unittest
import zipfile

from electri_city_ops.manifest_builder import validate_domain_entitlement, validate_plugin_package_metadata
from electri_city_ops.product_core import load_release_channels, validate_license_object, validate_update_manifest
from electri_city_ops.rollback_registry import validate_rollback_profile_entry


class RealStagingFinalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.channels = load_release_channels(self.workspace_root).channels

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_real_staging_gate_tracks_final_blocker(self) -> None:
        gate = self._load_json("config/real-staging-ready-gate.json")
        protected_preview = self._load_json("config/protected-pilot-preview.json")
        staging_preview = self._load_json("config/staging-test-preview.json")
        self.assertFalse(gate["ready_for_real_install_and_controlled_test"])
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["bound_test_host"], "wp.electri-c-ity-studios-24-7.com")
        self.assertIn("localhost", " ".join(gate["current_blockers"]))
        self.assertIn("backup_confirmation", gate["remaining_inputs"])
        self.assertEqual(
            protected_preview["package_preview"]["package_metadata_path"],
            "manifests/previews/final-real-staging-pilot-package-metadata.json",
        )
        self.assertEqual(
            protected_preview["pilot_manifest_preview"]["manifest_path"],
            "manifests/previews/final-real-staging-pilot-manifest-preview.json",
        )
        self.assertEqual(
            protected_preview["installability_preview"]["release_artifact_path"],
            "manifests/previews/final-real-staging-pilot-release-artifact-preview.json",
        )
        self.assertEqual(staging_preview["url_normalization_status"], "blocked")
        self.assertIn("localhost", staging_preview["current_url_residual"])

    def test_final_installable_staging_bundle_artifacts_are_valid(self) -> None:
        metadata_payload = self._load_json("manifests/previews/final-real-staging-pilot-package-metadata.json")
        raw_metadata = self._load_json("manifests/previews/final-real-staging-pilot-package-metadata.raw.json")
        domain_binding = self._load_json("manifests/previews/final-real-staging-pilot-license-domain-match-preview.json")
        license_object = self._load_json("manifests/previews/final-real-staging-pilot-license-object-preview.json")
        manifest = self._load_json("manifests/previews/final-real-staging-pilot-manifest-preview.json")
        entitlement = self._load_json("manifests/previews/final-real-staging-pilot-entitlement-preview.json")
        rollback_entry = self._load_json("manifests/previews/final-real-staging-pilot-rollback-profile-preview.json")
        validation_checklist = self._load_json(
            "manifests/previews/final-real-staging-pilot-validation-checklist-preview.json"
        )
        artifact_payload = self._load_json("manifests/previews/final-real-staging-pilot-release-artifact-preview.json")

        self.assertTrue(metadata_payload["valid"])
        self.assertTrue(validate_plugin_package_metadata(raw_metadata, self.channels).valid)
        self.assertEqual(domain_binding["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(validate_license_object(license_object, self.channels), [])
        self.assertEqual(validate_update_manifest(manifest, self.channels), [])
        self.assertTrue(validate_domain_entitlement(entitlement, self.channels).valid)
        self.assertTrue(validate_rollback_profile_entry(rollback_entry, self.channels).valid)
        self.assertTrue(artifact_payload["valid"])
        self.assertEqual(manifest["package_checksum"], raw_metadata["package_sha256"])
        self.assertEqual(manifest["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(entitlement["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(validation_checklist["status"], "approval_required")

        archive_path = self.workspace_root / metadata_payload["archive_path"]
        self.assertTrue(archive_path.exists())
        with zipfile.ZipFile(archive_path) as archive:
            self.assertIn("hetzner-seo-ops/hetzner-seo-ops.php", archive.namelist())

    def test_final_real_staging_docs_exist(self) -> None:
        expected = [
            "docs/final-url-normalization-fix-plan.md",
            "docs/final-wordpress-example-page-cleanup.md",
            "docs/final-staging-pilot-package-plan.md",
            "docs/final-staging-pilot-package-contents.md",
            "docs/final-staging-pilot-domain-binding.md",
            "docs/real-install-runbook.md",
            "docs/real-safe-mode-test-runbook.md",
            "docs/real-first-test-execution-checklist.md",
            "docs/real-staging-go-no-go-checklist.md",
            "docs/ready-for-real-staging-test-gate.md",
            "docs/real-install-verification-pass.md",
            "docs/first-safe-mode-observation-pass.md",
            "docs/real-rollback-drill.md",
            "docs/real-coexistence-pass.md",
            "docs/promotion-decision-to-reference-pilot.md",
        ]
        for relative_path in expected:
            with self.subTest(path=relative_path):
                self.assertTrue((self.workspace_root / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
