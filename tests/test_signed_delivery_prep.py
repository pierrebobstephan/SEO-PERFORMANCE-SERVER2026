import json
from pathlib import Path
import unittest

from electri_city_ops.fulfillment import validate_license_issuance_prep, validate_signed_delivery_prep


class SignedDeliveryPrepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_license_issuance_prep_is_valid_and_stays_guarded(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-license-issuance-prep.json")
        self.assertTrue(payload["valid"])
        prep = payload["license_issuance_prep"]
        self.assertTrue(validate_license_issuance_prep(prep).valid)
        self.assertEqual(prep["status"], "approval_required")
        self.assertEqual(prep["signing_key_reference"], "local_server_signing_key")
        self.assertEqual(prep["signing_target"], "local_server_signing_key")

    def test_signed_delivery_prep_is_valid_and_contains_no_cleartext_secret(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-signed-delivery-prep.json")
        self.assertTrue(payload["valid"])
        prep = payload["signed_delivery_prep"]
        self.assertTrue(validate_signed_delivery_prep(prep).valid)
        self.assertFalse(prep["signing"]["cleartext_secret_present"])
        self.assertEqual(prep["signing"]["signing_target"], "local_server_signing_key")
        self.assertEqual(prep["replay_protection"]["state"], "local_policy_defined")
        self.assertEqual(prep["replay_protection"]["nonce_strategy"], "domain_bound_issued_at_expires_at_window")
        self.assertFalse(prep["delivery_grant"]["public_delivery"])
        self.assertFalse(prep["delivery_grant"]["customer_login"])
        self.assertFalse(prep["delivery_grant"]["license_api_exposed"])
        self.assertEqual(prep["delivery_grant"]["delivery_target"], "protected_signed_download_on_hetzner")
        self.assertEqual(
            prep["delivery_grant"]["delivery_grant_rule"],
            "payment_confirmed_and_exact_domain_bound_and_license_issued_and_signed_and_operator_approved",
        )


if __name__ == "__main__":
    unittest.main()
