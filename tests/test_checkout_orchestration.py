import json
from pathlib import Path
import unittest

from electri_city_ops.fulfillment import (
    validate_invoice_confirmation_prep,
    validate_protected_customer_release_decision,
    validate_customer_release_authorization,
    validate_checkout_record_prep,
    validate_checkout_to_issuance_orchestration,
    validate_payment_confirmation_prep,
)


class CheckoutOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_checkout_record_prep_is_valid_and_matches_guardian_core_plan(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-checkout-record-prep.json")
        self.assertTrue(payload["valid"])
        checkout_record = payload["checkout_record_prep"]
        self.assertTrue(validate_checkout_record_prep(checkout_record).valid)
        self.assertEqual(checkout_record["selected_plan"], "Guardian Core Monthly")
        self.assertEqual(checkout_record["licensed_domain_count"], 1)
        self.assertEqual(checkout_record["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(checkout_record["payment_method"], "paypal_business")
        self.assertEqual(checkout_record["support_email"], "pierre.stephan1@electri-c-ity-studios.com")

    def test_payment_confirmation_prep_is_valid_and_bound_to_paypal_business(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-payment-confirmation-prep.json")
        self.assertTrue(payload["valid"])
        confirmation = payload["payment_confirmation_prep"]
        self.assertTrue(validate_payment_confirmation_prep(confirmation).valid)
        self.assertEqual(confirmation["payment_method"], "paypal_business")
        self.assertEqual(confirmation["payment_processor_label"], "PayPal Business")
        self.assertEqual(confirmation["invoice_state"], "approval_required")

    def test_customer_release_authorization_is_valid_and_stays_protected(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-customer-release-authorization.json")
        self.assertTrue(payload["valid"])
        authorization = payload["customer_release_authorization"]
        self.assertTrue(validate_customer_release_authorization(authorization).valid)
        self.assertEqual(authorization["customer_release_channel"], "protected_operator_delivery_only")
        self.assertFalse(authorization["public_delivery"])
        self.assertFalse(authorization["customer_login"])
        self.assertFalse(authorization["license_api_exposed"])

    def test_invoice_confirmation_prep_is_valid_and_stays_approval_required(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-invoice-confirmation-prep.json")
        self.assertTrue(payload["valid"])
        invoice_confirmation = payload["invoice_confirmation_prep"]
        self.assertTrue(validate_invoice_confirmation_prep(invoice_confirmation).valid)
        self.assertEqual(invoice_confirmation["invoice_state"], "approval_required")
        self.assertEqual(invoice_confirmation["invoice_confirmation_state"], "approval_required")
        self.assertEqual(invoice_confirmation["operator_review_owner"], "server_managed_bridge")

    def test_protected_customer_release_decision_is_valid_and_not_public(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-protected-customer-release-decision.json")
        self.assertTrue(payload["valid"])
        decision = payload["protected_customer_release_decision"]
        self.assertTrue(validate_protected_customer_release_decision(decision).valid)
        self.assertEqual(decision["go_no_go_state"], "operator_review_required")
        self.assertEqual(decision["rollback_readiness_state"], "server_managed_bridge")
        self.assertEqual(decision["validation_readiness_state"], "server_managed_bridge")
        self.assertFalse(decision["public_delivery"])
        self.assertFalse(decision["customer_login"])
        self.assertFalse(decision["license_api_exposed"])

    def test_checkout_to_issuance_orchestration_is_valid_and_approval_gated(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-checkout-to-issuance-orchestration.json")
        self.assertTrue(payload["valid"])
        orchestration = payload["checkout_to_issuance_orchestration"]
        self.assertTrue(validate_checkout_to_issuance_orchestration(orchestration).valid)
        self.assertEqual(orchestration["status"], "approval_required")
        self.assertEqual(orchestration["selected_plan"], "Guardian Core Monthly")
        self.assertEqual(orchestration["payment_method"], "paypal_business")
        self.assertIn("customer_release_authorized", [step["name"] for step in orchestration["steps"]])
        self.assertIn("payment_confirmation_prepared", [step["name"] for step in orchestration["steps"]])
        self.assertIn("invoice_confirmation_prepared", [step["name"] for step in orchestration["steps"]])
        self.assertIn("protected_customer_release_decision_prepared", [step["name"] for step in orchestration["steps"]])


if __name__ == "__main__":
    unittest.main()
