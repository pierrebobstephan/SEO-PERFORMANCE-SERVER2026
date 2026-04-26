import json
from pathlib import Path
import unittest

from electri_city_ops.fulfillment import validate_protected_customer_install_pack


class ProtectedFulfillmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_install_pack_preview_is_valid_and_protected(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-protected-customer-install-pack.json")
        self.assertTrue(payload["valid"])
        install_pack = payload["install_pack"]
        self.assertTrue(validate_protected_customer_install_pack(install_pack).valid)
        self.assertFalse(install_pack["public_delivery"])
        self.assertFalse(install_pack["customer_login"])
        self.assertFalse(install_pack["license_api_exposed"])
        self.assertEqual(install_pack["bound_domain"], "wp.electri-c-ity-studios-24-7.com")

    def test_install_pack_refs_match_existing_staging_artifacts(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-protected-customer-install-pack.json")
        refs = payload["input_refs"]
        for key, relative_path in refs.items():
            with self.subTest(ref=key):
                self.assertTrue((self.workspace_root / relative_path).exists())

    def test_install_pack_customer_visibility_stays_local_and_guarded(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-protected-customer-install-pack.json")
        visibility = payload["install_pack"]["customer_visibility"]
        self.assertEqual(visibility["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(visibility["subscription_status"], "staging_only_pilot")
        self.assertEqual(visibility["renewal_state"], "operator_review_required")
        self.assertEqual(visibility["renewal_window_state"], "not_open")
        self.assertEqual(visibility["failed_payment_recovery_state"], "not_needed")
        self.assertEqual(visibility["licensed_download_access"], "protected_local_bundle_only")
        self.assertEqual(visibility["license_integrity_state"], "operator_signing_required")
        self.assertEqual(visibility["support_state"], "email_support_active")
        self.assertEqual(visibility["support_email"], "pierre.stephan1@electri-c-ity-studios.com")
        self.assertEqual(visibility["activation_state"], "approval_required")


if __name__ == "__main__":
    unittest.main()
