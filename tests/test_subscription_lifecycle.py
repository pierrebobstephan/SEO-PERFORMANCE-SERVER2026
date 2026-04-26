import json
from pathlib import Path
import unittest

from electri_city_ops.fulfillment import (
    validate_failed_payment_recovery_prep,
    validate_renewal_prep,
    validate_subscription_lifecycle_prep,
)


class SubscriptionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_subscription_lifecycle_prep_is_valid(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-subscription-lifecycle-prep.json")
        self.assertTrue(payload["valid"])
        lifecycle = payload["subscription_lifecycle_prep"]
        self.assertTrue(validate_subscription_lifecycle_prep(lifecycle).valid)
        self.assertEqual(lifecycle["payment_method"], "paypal_business")
        self.assertEqual(lifecycle["subscription_status"], "staging_only_pilot")

    def test_renewal_prep_is_valid_and_guarded(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-renewal-prep.json")
        self.assertTrue(payload["valid"])
        renewal = payload["renewal_prep"]
        self.assertTrue(validate_renewal_prep(renewal).valid)
        self.assertEqual(renewal["renewal_state"], "operator_review_required")
        self.assertEqual(renewal["renewal_delivery_state"], "approval_required")

    def test_failed_payment_recovery_prep_is_valid_and_non_destructive(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-failed-payment-recovery-prep.json")
        self.assertTrue(payload["valid"])
        recovery = payload["failed_payment_recovery_prep"]
        self.assertTrue(validate_failed_payment_recovery_prep(recovery).valid)
        self.assertEqual(recovery["customer_release_impact"], "hold_future_delivery_only")
        self.assertEqual(recovery["immediate_site_effect"], "none")


if __name__ == "__main__":
    unittest.main()
