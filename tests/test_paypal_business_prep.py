import json
from pathlib import Path
import unittest

from electri_city_ops.fulfillment import (
    validate_invoice_automation_prep,
    validate_paypal_business_ops_prep,
    validate_paypal_webhook_prep,
)
from electri_city_ops.paypal_business import validate_paypal_business_config


class PayPalBusinessPrepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_paypal_business_config_is_valid_and_secret_ref_only(self) -> None:
        payload = self._load_json("config/paypal-business.json")
        validation = validate_paypal_business_config(payload)
        self.assertTrue(validation.valid, validation.issues)
        self.assertEqual(payload["payment_method"], "paypal_business")
        self.assertEqual(payload["environment"], "production")
        self.assertEqual(
            payload["webhook_listener_candidate_url"],
            "https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook",
        )
        self.assertEqual(payload["webhook_listener_candidate_state"], "modeled_protected_candidate")
        self.assertEqual(payload["webhook_delivery_scope"], "paypal_billing_events_only")
        self.assertEqual(payload["webhook_activation_state"], "approval_required")
        self.assertEqual(payload["env_load_point"], "deploy/systemd/paypal-business.env")
        self.assertEqual(payload["env_load_mode"], "systemd_environment_file")
        self.assertEqual(len(payload["subscription_plans"]), 3)
        self.assertEqual(payload["subscription_plans"][0]["plan_id"], "P-7Y554482SB478120XNHHYBXY")
        self.assertFalse(payload["cleartext_secrets_present"])
        self.assertFalse(payload["public_checkout_exposed"])
        self.assertFalse(payload["public_invoice_portal_exposed"])
        self.assertFalse(payload["public_webhook_route_exposed"])
        self.assertEqual(payload["server_validation_owner"], "server_managed_bridge")
        self.assertEqual(payload["server_rollback_owner"], "server_managed_bridge")

    def test_paypal_business_ops_prep_is_valid(self) -> None:
        payload = self._load_json("manifests/previews/final-real-staging-paypal-business-ops-prep.json")
        self.assertTrue(payload["config_valid"])
        self.assertTrue(payload["valid"])
        ops = payload["paypal_business_ops_prep"]
        self.assertTrue(validate_paypal_business_ops_prep(ops).valid)
        self.assertEqual(ops["environment"], "production")
        self.assertEqual(ops["support_email"], "pierre.stephan1@electri-c-ity-studios.com")
        self.assertFalse(ops["cleartext_secrets_present"])
        self.assertEqual(ops["secret_reference_state"]["env_load_point"], "deploy/systemd/paypal-business.env")
        self.assertEqual(ops["webhook_listener_candidate"]["state"], "protected_receiver_candidate_modeled")
        self.assertEqual(
            ops["webhook_listener_candidate"]["url"],
            "https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook",
        )
        self.assertEqual(ops["protected_webhook_runtime"]["handler_state"], "implemented_local_protected_only")
        self.assertEqual(ops["protected_webhook_runtime"]["receiver_runtime_state"], "implemented_but_unverified")
        self.assertEqual(ops["local_runtime_verification"]["state"], "passed")
        self.assertEqual(
            ops["local_runtime_verification"]["proof_mode"],
            "local_synthetic_paypal_signature_and_replay_self_test",
        )
        self.assertEqual(len(ops["subscription_plans"]), 3)

    def test_invoice_automation_and_webhook_prep_are_valid(self) -> None:
        invoice_payload = self._load_json("manifests/previews/final-real-staging-invoice-automation-prep.json")
        webhook_payload = self._load_json("manifests/previews/final-real-staging-paypal-webhook-prep.json")
        self.assertTrue(invoice_payload["config_valid"])
        self.assertTrue(invoice_payload["valid"])
        self.assertTrue(webhook_payload["config_valid"])
        self.assertTrue(webhook_payload["valid"])
        invoice = invoice_payload["invoice_automation_prep"]
        webhook = webhook_payload["paypal_webhook_prep"]
        self.assertTrue(validate_invoice_automation_prep(invoice).valid)
        self.assertTrue(validate_paypal_webhook_prep(webhook).valid)
        self.assertEqual(invoice["server_validation_state"], "server_managed_bridge")
        self.assertEqual(invoice["server_rollback_state"], "server_managed_bridge")
        self.assertFalse(webhook["public_route_exposed"])
        self.assertEqual(webhook["listener_candidate_state"], "protected_receiver_candidate_modeled")
        self.assertEqual(webhook["handler_state"], "implemented_local_protected_only")
        self.assertEqual(webhook["receiver_runtime_state"], "implemented_but_unverified")
        self.assertEqual(webhook["verification_runtime_state"], "implemented")
        self.assertEqual(webhook["replay_protection_runtime_state"], "implemented")
        self.assertEqual(webhook["local_runtime_verification"]["state"], "passed")
        self.assertEqual(webhook["verification_state"], "implemented_runtime_ready_when_env_refs_present")
        self.assertEqual(webhook["listener_candidate_delivery_scope"], "paypal_billing_events_only")
        for relative_path in (
            "docs/protected-paypal-webhook-receiver-model.md",
            "docs/paypal-webhook-separation-rule.md",
            "docs/paypal-webhook-verification-flow.md",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((self.workspace_root / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
