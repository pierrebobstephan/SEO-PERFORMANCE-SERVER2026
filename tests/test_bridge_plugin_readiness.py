import json
from pathlib import Path
import re
import unittest
import zipfile


class BridgePluginReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_bridge_package_and_gate_are_consistent(self) -> None:
        gate = self._load_json("config/real-staging-ready-gate.json")
        metadata_payload = self._load_json("manifests/previews/final-real-staging-pilot-package-metadata.json")
        bridge_config = self._load_json("packages/wp-plugin/hetzner-seo-ops/config/bridge-config.json")

        self.assertEqual(gate["installable_package_artifact"], metadata_payload["archive_path"])
        self.assertEqual(metadata_payload["metadata"]["package_filename"], "site-optimizer-bridge-0.1.0-real-staging1-wp-electri-c-ity-studios-24-7-com.zip")
        self.assertEqual(bridge_config["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(bridge_config["default_mode"], "safe_mode")
        self.assertEqual(bridge_config["fallback_mode"], "observe_only")
        self.assertEqual(bridge_config["suite_connection_mode"], "packaged_preview_only")
        self.assertEqual(bridge_config["current_blockers"], [])
        self.assertFalse(gate["ready_for_real_install_and_controlled_test"])

    def test_bridge_zip_contains_required_files(self) -> None:
        metadata_payload = self._load_json("manifests/previews/final-real-staging-pilot-package-metadata.json")
        archive_path = self.workspace_root / metadata_payload["archive_path"]
        self.assertTrue(archive_path.exists())

        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            self.assertIn("hetzner-seo-ops/hetzner-seo-ops.php", names)
            self.assertIn("hetzner-seo-ops/config/bridge-config.json", names)
            self.assertIn("hetzner-seo-ops/includes/class-hso-bridge-config.php", names)
            self.assertIn("hetzner-seo-ops/includes/class-hso-baseline-capture.php", names)
            self.assertIn("hetzner-seo-ops/includes/class-hso-optimization-gate.php", names)
            self.assertIn("hetzner-seo-ops/admin/class-hso-admin-screen.php", names)

            plugin_main = archive.read("hetzner-seo-ops/hetzner-seo-ops.php").decode("utf-8")
            self.assertIn("Plugin Name: Site Optimizer Bridge", plugin_main)
            self.assertIn("register_activation_hook", plugin_main)

    def test_bridge_zip_matches_current_plugin_source_tree(self) -> None:
        metadata_payload = self._load_json("manifests/previews/final-real-staging-pilot-package-metadata.json")
        archive_path = self.workspace_root / metadata_payload["archive_path"]
        plugin_root = self.workspace_root / "packages/wp-plugin/hetzner-seo-ops"
        expected_files = {
            f"hetzner-seo-ops/{path.relative_to(plugin_root).as_posix()}": path.read_bytes()
            for path in sorted(plugin_root.rglob("*"))
            if path.is_file()
        }

        self.assertEqual(metadata_payload["metadata"]["file_count"], len(expected_files))
        with zipfile.ZipFile(archive_path) as archive:
            archived_files = sorted(name for name in archive.namelist() if not name.endswith("/"))
            self.assertEqual(archived_files, sorted(expected_files))
            for archive_name, expected_bytes in expected_files.items():
                self.assertEqual(archive.read(archive_name), expected_bytes, archive_name)

    def test_bridge_config_models_operator_inputs_and_source_mapping(self) -> None:
        bridge_config = self._load_json("packages/wp-plugin/hetzner-seo-ops/config/bridge-config.json")
        self.assertIn("operator_inputs", bridge_config)
        self.assertIn("source_mapping", bridge_config)
        self.assertIn("customer_visibility", bridge_config)
        self.assertIn("protected_fulfillment", bridge_config)
        self.assertEqual(bridge_config["customer_id"], "cust-real-staging-preview-001")
        self.assertEqual(bridge_config["product_id"], "hso-plugin")
        self.assertEqual(bridge_config["issued_at"], "2026-03-30T00:00:00Z")
        self.assertTrue(bridge_config["non_expiring"])
        self.assertEqual(
            sorted(bridge_config["allowed_features"]),
            sorted(["meta_description", "head_diagnostics", "structure_visibility"]),
        )
        self.assertEqual(bridge_config["integrity"]["signature_state"], "operator_signing_required")
        self.assertEqual(bridge_config["integrity"]["signing_key_reference"], "local_server_signing_key")
        self.assertEqual(bridge_config["doctrine"]["policy_version"], "8.0")
        self.assertEqual(bridge_config["doctrine"]["ai_system_id"], "wordpress_bridge_plugin")
        self.assertEqual(bridge_config["doctrine"]["risk_class"], "R1")
        self.assertEqual(bridge_config["doctrine"]["impact_assessment_ref"], "ia-wordpress-bridge-plugin-v1")
        self.assertEqual(
            sorted(bridge_config["operator_inputs"].keys()),
            sorted(
                [
                    "wordpress_version",
                    "active_theme",
                    "active_builder",
                    "active_seo_plugin",
                    "plugin_inventory",
                    "backup_confirmation",
                    "restore_confirmation",
                    "rollback_owner",
                    "validation_owner",
                ]
            ),
        )
        self.assertIn("homepage_meta_description_single", bridge_config["source_mapping"])
        self.assertIn("double_output_detected", bridge_config["source_mapping"])
        self.assertEqual(bridge_config["source_mapping"]["double_output_verification"], "not_detected")
        self.assertEqual(bridge_config["customer_visibility"]["surface_mode"], "protected_admin_only")
        self.assertEqual(bridge_config["customer_visibility"]["license_integrity_state"], "operator_signing_required")
        self.assertEqual(bridge_config["customer_visibility"]["renewal_state"], "operator_review_required")
        self.assertEqual(bridge_config["customer_visibility"]["failed_payment_recovery_state"], "not_needed")
        self.assertEqual(bridge_config["customer_visibility"]["support_state"], "email_support_active")
        self.assertEqual(bridge_config["customer_visibility"]["support_email"], "pierre.stephan1@electri-c-ity-studios.com")
        self.assertIn("scope, health, delivery and cutover signals", bridge_config["customer_visibility"]["customer_visibility_note"])
        self.assertIn("operator- and server-governed", bridge_config["customer_visibility"]["subscription_lifecycle_note"])
        self.assertEqual(bridge_config["operator_inputs"]["rollback_owner"], "server_managed_bridge")
        self.assertEqual(bridge_config["operator_inputs"]["validation_owner"], "server_managed_bridge")
        self.assertFalse(bridge_config["protected_fulfillment"]["public_delivery"])
        self.assertFalse(bridge_config["protected_fulfillment"]["customer_login"])
        self.assertFalse(bridge_config["protected_fulfillment"]["license_api_exposed"])
        self.assertEqual(bridge_config["protected_fulfillment"]["signature_prep_state"], "operator_signing_required")
        self.assertEqual(bridge_config["protected_fulfillment"]["delivery_grant_state"], "approval_required")
        self.assertEqual(bridge_config["protected_fulfillment"]["renewal_delivery_state"], "approval_required")
        self.assertEqual(bridge_config["protected_fulfillment"]["failed_payment_recovery_delivery_state"], "approval_required")
        self.assertIn("local_report_ingest", bridge_config)
        self.assertFalse(bridge_config["local_report_ingest"]["enabled"])
        self.assertIn("bundled_snapshot_path", bridge_config["local_report_ingest"])

    def test_real_staging_license_object_preview_uses_integrity_and_exact_binding(self) -> None:
        license_object = self._load_json("manifests/previews/final-real-staging-pilot-license-object-preview.json")
        binding = license_object["domain_binding"]
        self.assertEqual(license_object["customer_id"], "cust-real-staging-preview-001")
        self.assertEqual(license_object["product_id"], "hso-plugin")
        self.assertTrue(license_object["non_expiring"])
        self.assertEqual(binding["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(binding["allowed_subdomains"], [])
        self.assertEqual(license_object["integrity"]["signature_state"], "operator_signing_required")
        self.assertEqual(license_object["integrity"]["signing_key_reference"], "local_server_signing_key")

    def test_private_root_release_artifact_matches_current_package_metadata(self) -> None:
        raw_metadata = self._load_json("manifests/previews/private-root-electri-city-package-metadata.raw.json")
        artifact_payload = self._load_json("manifests/previews/private-root-electri-city-release-artifact-preview.json")
        metadata_payload = self._load_json("manifests/previews/private-root-electri-city-package-metadata.json")
        artifact = artifact_payload["artifact"]

        self.assertEqual(artifact["package_metadata"], raw_metadata)
        self.assertEqual(artifact["manifest"]["package_checksum"], raw_metadata["package_sha256"])
        with zipfile.ZipFile(self.workspace_root / metadata_payload["archive_path"]) as archive:
            names = set(archive.namelist())
            self.assertIn("hetzner-seo-ops/config/private-site-report.latest.json", names)
            bundled_report = json.loads(archive.read("hetzner-seo-ops/config/private-site-report.latest.json"))
            action_types = {item["action_type"] for item in bundled_report["automation_candidates"]}
            self.assertIn("rank_math_homepage_meta_description_update", action_types)
            self.assertIn("rank_math_meta_description_update", action_types)

    def test_bridge_runtime_code_uses_dynamic_blocker_and_readiness_state(self) -> None:
        plugin_php = (self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-plugin.php").read_text(
            encoding="utf-8"
        )
        safe_mode_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-safe-mode.php"
        ).read_text(encoding="utf-8")
        optimization_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-optimization-gate.php"
        ).read_text(encoding="utf-8")
        conflict_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-conflict-detector.php"
        ).read_text(encoding="utf-8")
        module_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/modules/class-hso-meta-description-module.php"
        ).read_text(encoding="utf-8")

        self.assertIn("build_operator_input_state", plugin_php)
        self.assertIn("build_source_mapping_state", plugin_php)
        self.assertIn("build_runtime_blockers", plugin_php)
        self.assertIn("'resolved_blockers'", plugin_php)
        self.assertIn("'heuristic'", plugin_php)
        self.assertIn("'operator_input_state'", plugin_php)
        self.assertIn("'source_mapping_state'", plugin_php)
        self.assertIn("'license_domain_scope_panel'", plugin_php)
        self.assertIn("'customer_subscription_visibility'", plugin_php)
        self.assertIn("'renewal_state'", plugin_php)
        self.assertIn("'failed_payment_recovery_state'", plugin_php)
        self.assertIn("'installation_health_signals'", plugin_php)
        self.assertIn("'protected_delivery_status'", plugin_php)
        self.assertIn("'renewal_delivery_state'", plugin_php)
        self.assertIn("'production_cutover_checklist'", plugin_php)
        self.assertIn("'reference_pilot_runtime_snapshot'", plugin_php)
        self.assertIn("'innovation_control_deck'", plugin_php)
        self.assertIn("'recommendation_action_center'", plugin_php)
        self.assertIn("'doctrine_runtime_state'", plugin_php)
        self.assertIn("build_doctrine_runtime_state", plugin_php)
        self.assertIn("build_reference_pilot_runtime_snapshot", plugin_php)
        self.assertIn("build_innovation_control_deck", plugin_php)
        self.assertIn("HSO_Recommendation_Action_Center", plugin_php)
        self.assertIn("license_signature_trusted", plugin_php)
        self.assertIn("channel_allows_active_scoped", plugin_php)
        self.assertIn("'path_base'", plugin_php)
        self.assertIn("'domain_match'", plugin_php)
        self.assertIn("'baseline_captured'", plugin_php)
        self.assertIn("'operator_inputs_complete'", plugin_php)
        self.assertIn("'impact_assessment_ref'", plugin_php)
        self.assertIn("'blocking_requirements'", plugin_php)
        self.assertIn("'heuristic_requirements'", plugin_php)
        self.assertIn("'duplicate_output_status'", plugin_php)
        self.assertIn("'coexistence_mode'", plugin_php)
        self.assertIn("'coexistence_advisories'", plugin_php)
        self.assertIn("'external_seo_owner_active'", plugin_php)
        self.assertIn("'next_smallest_safe_step'", plugin_php)
        self.assertIn("'operating_model'", plugin_php)
        self.assertIn("'buyer_visibility_surface'", plugin_php)
        self.assertIn("'resilience_model'", plugin_php)
        self.assertIn("'buyer_insight_surface'", plugin_php)
        self.assertIn("'cutover_model'", plugin_php)
        action_center_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-recommendation-action-center.php"
        ).read_text(encoding="utf-8")
        self.assertIn("RANK_MATH_META_DESCRIPTION_CONTRACT_ID", action_center_php)
        self.assertIn("ac-rank-math-meta-description-update-v1", action_center_php)
        self.assertIn("RANK_MATH_HOMEPAGE_META_DESCRIPTION_CONTRACT_ID", action_center_php)
        self.assertIn("ac-rank-math-homepage-meta-description-update-v1", action_center_php)
        self.assertIn("rank_math_homepage_meta_description_update", action_center_php)
        self.assertIn("rank_math_titles.homepage_description", action_center_php)
        self.assertIn("rank-math-options-titles", action_center_php)
        self.assertIn("homepage_description", action_center_php)
        self.assertIn("rank_math_homepage_option_resolved", action_center_php)
        self.assertIn("automation_contract_id", action_center_php)
        self.assertIn("automation_contract_version", action_center_php)
        self.assertIn("automation_contract_state", action_center_php)
        self.assertIn("requires_admin_confirmation", action_center_php)
        self.assertIn("requires_before_state_capture", action_center_php)
        self.assertIn("requires_rollback", action_center_php)
        self.assertIn("previous_exists", action_center_php)
        self.assertIn("report_path_candidates", action_center_php)
        self.assertIn("bundled_snapshot_path", action_center_php)
        self.assertIn("is_readable", action_center_php)
        self.assertIn("target_resolution_state", action_center_php)
        self.assertIn("wordpress_page_resolved", action_center_php)
        self.assertIn("get_privacy_policy_url", action_center_php)
        self.assertIn("normalize_url_for_compare", action_center_php)
        self.assertIn("runtime_blockers['open']", safe_mode_php)
        self.assertIn("required operator inputs are incomplete", optimization_php)
        self.assertIn("duplicate head or meta output is present", optimization_php)
        self.assertIn("existing SEO owner remains active under controlled coexistence", optimization_php)
        self.assertIn("'external_seo_owner_active'", conflict_php)
        self.assertIn("'single_seo_plugin_slug'", conflict_php)
        self.assertIn("'coexistence_mode'", conflict_php)
        self.assertIn("external_seo_owner_active", module_php)

    def test_admin_surface_supports_local_operator_and_source_mapping_persistence(self) -> None:
        admin_php = (self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/admin/class-hso-admin-screen.php").read_text(
            encoding="utf-8"
        )
        bridge_config_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-bridge-config.php"
        ).read_text(encoding="utf-8")

        self.assertIn("save_operator_inputs", admin_php)
        self.assertIn("save_source_mapping", admin_php)
        self.assertIn("persist_operator_inputs", bridge_config_php)
        self.assertIn("persist_source_mapping", bridge_config_php)
        self.assertIn("'bundled_snapshot_path'", bridge_config_php)
        self.assertIn("'rollback_owner' => 'server_managed_bridge'", admin_php)
        self.assertIn("'validation_owner' => 'server_managed_bridge'", admin_php)
        self.assertIn("'rollback_owner' => 'server_managed_bridge'", bridge_config_php)
        self.assertIn("'validation_owner' => 'server_managed_bridge'", bridge_config_php)
        self.assertIn("normalize_allowed_subdomains", bridge_config_php)
        self.assertIn("Operator Input Completion", admin_php)
        self.assertIn("Source Mapping Confirmation", admin_php)
        self.assertIn("Recommendation Action Center", admin_php)
        self.assertIn("Automation contract", admin_php)
        self.assertIn("Contract state", admin_php)
        self.assertIn("Target resolution", admin_php)
        self.assertIn("Resolution note", admin_php)
        self.assertIn("Apply With Admin Confirmation", admin_php)
        self.assertIn("Rollback To Before-State", admin_php)
        self.assertIn("Duplicate output verification", admin_php)
        self.assertIn("Coexistence mode", admin_php)
        self.assertIn("Controlled coexistence notes", admin_php)
        self.assertIn("Unresolved Heuristic Findings", admin_php)
        self.assertIn("Next Smallest Safe Step", admin_php)
        self.assertIn("Installed Suite Insights", admin_php)
        self.assertIn("Innovation Control Deck", admin_php)
        self.assertIn("Innovation Posture", admin_php)
        self.assertIn("Immediate Safe Actions", admin_php)
        self.assertIn("Next Innovation Actions", admin_php)
        self.assertIn("Success Signals", admin_php)
        self.assertIn("Protected Holds", admin_php)
        self.assertIn("What The Installed Plugin Sees", admin_php)
        self.assertIn("Next Steps Before Production", admin_php)
        self.assertIn("Post-Purchase Visibility Layer", admin_php)
        self.assertIn("License / Domain / Scope Panel", admin_php)
        self.assertIn("Customer Subscription Visibility", admin_php)
        self.assertIn("Installation Health Signals", admin_php)
        self.assertIn("Doctrine 8.0 Governance", admin_php)
        self.assertIn("Protected Delivery Status", admin_php)
        self.assertIn("Production Cutover Checklist", admin_php)
        self.assertIn("bounded, explainable and reversible", admin_php)
        self.assertIn("buyer-readable instead of behaving like a black box", admin_php)
        self.assertIn("hso_recommendation_action_journal", (self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-recommendation-action-center.php").read_text(encoding="utf-8"))
        self.assertIn("rank_math_description", (self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-recommendation-action-center.php").read_text(encoding="utf-8"))

        license_check_php = (
            self.workspace_root / "packages/wp-plugin/hetzner-seo-ops/includes/class-hso-license-check.php"
        ).read_text(encoding="utf-8")
        self.assertIn("normalize_allowed_subdomains", license_check_php)
        self.assertIn("is_explicit_descendant", license_check_php)

    def test_plugin_php_has_no_invalid_local_type_annotations(self) -> None:
        invalid_local_var_pattern = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\s*:\s*[A-Za-z_\\\\]+\s*=")
        plugin_root = self.workspace_root / "packages/wp-plugin/hetzner-seo-ops"
        for php_file in plugin_root.rglob("*.php"):
            contents = php_file.read_text(encoding="utf-8")
            self.assertIsNone(
                invalid_local_var_pattern.search(contents),
                f"invalid local variable type annotation found in {php_file.relative_to(self.workspace_root)}",
            )

    def test_bridge_docs_exist(self) -> None:
        expected = [
            "docs/final-bridge-plugin-build-plan.md",
            "docs/bridge-plugin-package-contents.md",
            "docs/bridge-plugin-download-and-install-readiness.md",
            "docs/bridge-plugin-install-runbook.md",
            "docs/bridge-plugin-activation-checklist.md",
            "docs/bridge-plugin-admin-surface-plan.md",
            "docs/bridge-plugin-suite-connection-model.md",
            "docs/bridge-plugin-domain-binding-flow.md",
            "docs/bridge-plugin-safe-boot-sequence.md",
            "docs/post-install-baseline-flow.md",
            "docs/post-install-guardrail-sequence.md",
            "docs/post-install-coexistence-snapshot.md",
            "docs/first-controlled-optimization-stage.md",
            "docs/optimization-eligibility-gate.md",
            "docs/first-reversible-optimization-scope.md",
            "docs/ready-for-real-install-and-controlled-optimization.md",
            "docs/real-plugin-upload-pass.md",
            "docs/real-activation-pass.md",
            "docs/first-baseline-capture-pass.md",
            "docs/first-controlled-optimization-pass.md",
            "docs/production-readiness-roadmap.md",
            "docs/ai-system-register-model.md",
            "docs/ai-impact-assessment-model.md",
            "docs/provenance-and-supply-chain-evidence-model.md",
            "docs/operator-input-completion-runbook.md",
            "docs/operator-input-storage-model.md",
            "docs/operator-input-admin-surface.md",
            "docs/backup-restore-confirmation-pass.md",
            "docs/operator-input-closure-pass.md",
            "docs/source-mapping-confirmation-model.md",
            "docs/source-mapping-confirmation-runbook.md",
            "docs/single-source-head-meta-checklist.md",
            "docs/duplicate-head-meta-detection-model.md",
            "docs/duplicate-head-meta-verification-checklist.md",
            "docs/source-mapping-gate-reconciliation.md",
            "docs/customer-visible-plugin-insight-model.md",
            "docs/installed-suite-insight-surface.md",
            "docs/production-cutover-gap-register.md",
            "docs/post-purchase-customer-visibility-layer.md",
            "docs/post-purchase-license-domain-scope-panel.md",
            "docs/post-purchase-installation-health-signals.md",
            "docs/production-cutover-checklist-flow.md",
            "docs/installed-plugin-health-and-cutover-surface.md",
            "docs/protected-customer-fulfillment-model.md",
            "docs/local-license-issuance-and-delivery-path.md",
            "docs/customer-install-pack-model.md",
            "docs/customer-subscription-visibility-model.md",
            "docs/post-purchase-activation-boundaries.md",
            "docs/operator-protected-fulfillment-runbook.md",
            "docs/local-signed-delivery-prep-model.md",
            "docs/local-license-issuance-prep.md",
            "docs/operator-signed-delivery-prep-runbook.md",
            "docs/protected-release-grant-model.md",
            "docs/replay-protection-prep-model.md",
            "docs/license-signing-key-reference-model.md",
            "docs/local-checkout-to-issuance-orchestration.md",
            "docs/local-payment-confirmation-model.md",
            "docs/local-invoice-confirmation-model.md",
            "docs/local-subscription-lifecycle-model.md",
            "docs/local-renewal-prep-model.md",
            "docs/local-failed-payment-recovery-model.md",
            "docs/customer-release-authorization-model.md",
            "docs/protected-customer-release-decision-model.md",
            "docs/protected-order-record-model.md",
            "docs/operator-checkout-review-runbook.md",
            "docs/operator-payment-confirmation-runbook.md",
            "docs/operator-customer-release-runbook.md",
            "docs/operator-release-decision-runbook.md",
            "docs/operator-subscription-lifecycle-runbook.md",
            "docs/global-sales-cutover-sequence.md",
            "docs/global-sales-readiness-path.md",
            "docs/global-sales-go-live-gates.md",
            "docs/post-purchase-buyer-data-surface-plan.md",
            "docs/next-five-productization-steps.md",
            "docs/paypal-business-integration-model.md",
            "docs/automated-invoice-flow.md",
            "docs/paypal-webhook-verification-model.md",
            "docs/server-owned-rollback-and-validation-model.md",
            "docs/paypal-secret-reference-model.md",
            "docs/suite-v5-doctrine-product-harmonization.md",
            "docs/public-portal-v5-doctrine-narrative.md",
            "docs/plugin-v5-doctrine-surface-plan.md",
            "docs/automation-contract-gate.md",
            "docs/wordpress-bridge-php-validation-gate.md",
            "docs/global-usage-rights-and-valuation-model.md",
            "LICENSE.md",
            "tools/check_wordpress_bridge_php_syntax.py",
        ]
        for relative_path in expected:
            with self.subTest(path=relative_path):
                self.assertTrue((self.workspace_root / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
