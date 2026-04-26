from pathlib import Path
import unittest

from electri_city_ops.config import load_config
from electri_city_ops.local_console import (
    build_health_payload,
    build_preview_objects,
    collect_console_snapshot,
    execute_local_action,
    load_local_console_config,
    render_index_html,
    run_schema_checks,
)


class LocalConsoleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.config, _ = load_config("config/settings.toml", self.workspace_root)
        self.console_config = load_local_console_config(self.workspace_root)

    def test_local_console_config_stays_local_only(self) -> None:
        self.assertEqual(self.console_config.host, "127.0.0.1")
        self.assertIn("run_python_tests", self.console_config.allowed_actions)

    def test_preview_objects_include_manifest_and_package_metadata(self) -> None:
        previews = build_preview_objects(self.workspace_root, self.config)
        self.assertIn("license_object", previews)
        self.assertIn("plugin_package_metadata_preview", previews)
        self.assertEqual(previews["plugin_package_metadata_preview"]["release_channel"], "pilot")
        self.assertIsNotNone(previews["manifest_preview"])

    def test_collect_console_snapshot_contains_required_sections(self) -> None:
        snapshot = collect_console_snapshot(self.workspace_root, self.config, self.console_config)
        for key in (
            "runtime",
            "doctrine",
            "ai_governance",
            "domain_configuration",
            "reports",
            "product_core_status",
            "plugin_mvp_status",
            "backend_core_status",
            "packaging_release_preview_status",
            "operator_fulfillment_cockpit",
            "global_productization_readiness",
            "external_cutover_package",
            "dry_run_onboarding_preview",
            "preview_objects",
            "test_status",
            "local_console",
        ):
            self.assertIn(key, snapshot)
        self.assertEqual(snapshot["operator_fulfillment_cockpit"]["status"], "local_operator_only")
        self.assertIn("reference_pilot", snapshot["global_productization_readiness"]["layers"])
        self.assertIn("R0", snapshot["doctrine"]["risk_classes"])
        self.assertIn("govern", snapshot["doctrine"]["required_lifecycle_stages"])
        self.assertEqual(snapshot["ai_governance"]["status"], "blueprint_ready")

    def test_schema_checks_are_valid(self) -> None:
        payload = run_schema_checks(self.workspace_root, self.config, self.console_config)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["validations"]["ai_system_register"], [])
        self.assertEqual(payload["validations"]["ai_impact_assessments"], [])
        self.assertEqual(payload["validations"]["provenance_evidence"], [])
        self.assertEqual(payload["validations"]["supply_chain_evidence"], [])
        self.assertEqual(payload["validations"]["external_cutover_checklist"], [])

    def test_local_preview_action_builds_manifest(self) -> None:
        result = execute_local_action("build_manifest_preview", self.workspace_root, self.config, self.console_config)
        self.assertTrue(result.ok)
        self.assertIn("manifest_preview", result.output)

    def test_health_payload_is_local_only(self) -> None:
        payload = build_health_payload(self.workspace_root, self.config, self.console_config)
        self.assertEqual(payload["host"], "127.0.0.1")
        self.assertTrue(payload["local_only"])

    def test_rendered_console_contains_local_only_notice(self) -> None:
        html_output = render_index_html(
            collect_console_snapshot(self.workspace_root, self.config, self.console_config),
            self.console_config,
        )
        self.assertIn("Local only / no external effect", html_output)
        self.assertIn("Operator Fulfillment Cockpit", html_output)

    def test_operator_fulfillment_actions_are_available(self) -> None:
        self.assertIn("build_protected_customer_install_pack", self.console_config.allowed_actions)
        self.assertIn("build_signed_delivery_prep", self.console_config.allowed_actions)
        self.assertIn("build_checkout_to_issuance_orchestration", self.console_config.allowed_actions)
        self.assertIn("build_payment_confirmation_and_customer_release", self.console_config.allowed_actions)
        self.assertIn("build_invoice_confirmation_and_release_decision", self.console_config.allowed_actions)
        self.assertIn("build_subscription_lifecycle_prep", self.console_config.allowed_actions)
        self.assertIn("build_paypal_business_and_invoice_prep", self.console_config.allowed_actions)
        self.assertIn("build_global_productization_readiness", self.console_config.allowed_actions)
        self.assertIn("build_external_cutover_package", self.console_config.allowed_actions)

        install_pack_result = execute_local_action(
            "build_protected_customer_install_pack", self.workspace_root, self.config, self.console_config
        )
        signed_delivery_result = execute_local_action(
            "build_signed_delivery_prep", self.workspace_root, self.config, self.console_config
        )
        checkout_orchestration_result = execute_local_action(
            "build_checkout_to_issuance_orchestration", self.workspace_root, self.config, self.console_config
        )
        payment_release_result = execute_local_action(
            "build_payment_confirmation_and_customer_release", self.workspace_root, self.config, self.console_config
        )
        release_decision_result = execute_local_action(
            "build_invoice_confirmation_and_release_decision", self.workspace_root, self.config, self.console_config
        )
        lifecycle_result = execute_local_action(
            "build_subscription_lifecycle_prep", self.workspace_root, self.config, self.console_config
        )
        paypal_invoice_result = execute_local_action(
            "build_paypal_business_and_invoice_prep", self.workspace_root, self.config, self.console_config
        )
        readiness_result = execute_local_action(
            "build_global_productization_readiness", self.workspace_root, self.config, self.console_config
        )
        external_cutover_result = execute_local_action(
            "build_external_cutover_package", self.workspace_root, self.config, self.console_config
        )
        self.assertTrue(install_pack_result.ok)
        self.assertTrue(signed_delivery_result.ok)
        self.assertTrue(checkout_orchestration_result.ok)
        self.assertTrue(payment_release_result.ok)
        self.assertTrue(release_decision_result.ok)
        self.assertTrue(lifecycle_result.ok)
        self.assertTrue(paypal_invoice_result.ok)
        self.assertTrue(readiness_result.ok)
        self.assertTrue(external_cutover_result.ok)

    def test_operator_fulfillment_snapshot_includes_payment_and_release_state(self) -> None:
        snapshot = collect_console_snapshot(self.workspace_root, self.config, self.console_config)
        summary = snapshot["operator_fulfillment_cockpit"]["summary"]
        previews = snapshot["preview_objects"]
        self.assertEqual(summary["payment_method"], "paypal_business")
        self.assertEqual(summary["payment_processor_label"], "PayPal Business")
        self.assertEqual(summary["invoice_confirmation_state"], "approval_required")
        self.assertEqual(summary["release_go_no_go_state"], "operator_review_required")
        self.assertEqual(summary["renewal_state"], "operator_review_required")
        self.assertEqual(summary["failed_payment_recovery_state"], "not_needed")
        self.assertEqual(summary["support_email"], "pierre.stephan1@electri-c-ity-studios.com")
        self.assertEqual(summary["paypal_environment"], "production")
        self.assertEqual(summary["invoice_automation_state"], "approval_required")
        self.assertEqual(summary["webhook_verification_state"], "implemented_runtime_ready_when_env_refs_present")
        self.assertEqual(
            summary["paypal_webhook_candidate_url"],
            "https://site-optimizer.electri-c-ity-studios-24-7.com/protected/paypal/webhook",
        )
        self.assertEqual(summary["paypal_webhook_candidate_state"], "protected_receiver_candidate_modeled")
        self.assertEqual(summary["paypal_webhook_candidate_delivery_scope"], "paypal_billing_events_only")
        self.assertEqual(summary["paypal_webhook_handler_state"], "implemented_local_protected_only")
        self.assertEqual(summary["paypal_webhook_receiver_runtime_state"], "implemented_but_unverified")
        self.assertEqual(summary["paypal_webhook_verification_runtime_state"], "implemented")
        self.assertEqual(summary["paypal_webhook_replay_runtime_state"], "implemented")
        self.assertEqual(summary["paypal_webhook_env_ref_readiness_state"], "missing_env_refs")
        self.assertEqual(summary["paypal_webhook_activation_state"], "approval_required")
        self.assertEqual(summary["paypal_webhook_local_runtime_verification_state"], "passed")
        self.assertEqual(
            summary["paypal_webhook_local_runtime_verification_mode"],
            "local_synthetic_paypal_signature_and_replay_self_test",
        )
        self.assertIn("payment_confirmation_prep_preview", previews)
        self.assertIn("invoice_confirmation_prep_preview", previews)
        self.assertIn("customer_release_authorization_preview", previews)
        self.assertIn("protected_customer_release_decision_preview", previews)
        self.assertIn("subscription_lifecycle_prep_preview", previews)
        self.assertIn("renewal_prep_preview", previews)
        self.assertIn("failed_payment_recovery_prep_preview", previews)
        self.assertIn("paypal_business_ops_prep_preview", previews)
        self.assertIn("invoice_automation_prep_preview", previews)
        self.assertIn("paypal_webhook_prep_preview", previews)
        self.assertIn("external_cutover_package_preview", previews)
        readiness = snapshot["global_productization_readiness"]
        external_cutover = snapshot["external_cutover_package"]
        self.assertEqual(readiness["status"], "commercial_chain_not_closed")
        self.assertIn("PAYPAL_BUSINESS_CLIENT_ID", readiness["required_external_inputs"])
        self.assertIn("protected PayPal webhook receiver verification and activation", readiness["required_external_inputs"])
        self.assertEqual(readiness["layers"]["reference_pilot"]["status"], "ready_for_reference_pilot")
        self.assertIn("reference_pilot", readiness["layers"])
        self.assertIn("commercial_chain", readiness["layers"])
        self.assertEqual(external_cutover["status"], "ready_for_external_execution")
        self.assertEqual(
            external_cutover["local_preconditions"]["commercial_chain_local_readiness_state"],
            "locally_verified_waiting_external_inputs",
        )


if __name__ == "__main__":
    unittest.main()
