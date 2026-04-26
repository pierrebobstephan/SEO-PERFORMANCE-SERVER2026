import json
from pathlib import Path
import unittest

from electri_city_ops.productization import (
    build_reference_pilot_closeout_readiness,
    derive_global_productization_readiness,
    validate_reference_pilot_runtime_input,
)


class GlobalProductizationReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_global_productization_readiness_derives_five_layers(self) -> None:
        readiness = derive_global_productization_readiness(self.workspace_root)
        self.assertEqual(readiness["status"], "commercial_chain_not_closed")
        self.assertFalse(readiness["ready_for_global_go_live"])
        self.assertIn("ai_governance", readiness["layers"])
        self.assertIn("reference_pilot", readiness["layers"])
        self.assertIn("commercial_chain", readiness["layers"])
        self.assertIn("operations", readiness["layers"])
        self.assertIn("product", readiness["layers"])
        self.assertEqual(
            readiness["next_smallest_safe_step"],
            "inject PayPal env refs and verify the protected webhook receiver in the real server context",
        )
        self.assertEqual(readiness["layers"]["reference_pilot"]["status"], "ready_for_reference_pilot")
        self.assertEqual(readiness["layers"]["reference_pilot"]["blockers"], [])
        self.assertIn("PAYPAL_BUSINESS_CLIENT_ID", readiness["required_external_inputs"])
        self.assertIn("PAYPAL_BUSINESS_CLIENT_SECRET", readiness["required_external_inputs"])
        self.assertIn("PAYPAL_BUSINESS_WEBHOOK_ID", readiness["required_external_inputs"])
        self.assertIn("protected PayPal webhook receiver verification and activation", readiness["required_external_inputs"])
        self.assertNotIn("real protected PayPal webhook receiver URL", readiness["required_external_inputs"])
        self.assertNotIn("protected delivery infrastructure target and delivery grant release rule", readiness["required_external_inputs"])
        self.assertEqual(readiness["layers"]["ai_governance"]["status"], "blueprint_ready")
        self.assertIn("impact assessments are present for all required systems", readiness["layers"]["ai_governance"]["proof_points"])
        self.assertIn(
            "secret hygiene gate is green for workspace env files and ignore rules",
            readiness["layers"]["ai_governance"]["proof_points"],
        )
        self.assertIn("rollback ownership is server-managed through the bridge", readiness["layers"]["operations"]["proof_points"])
        self.assertIn("buyer-visible license / domain / scope panel is populated", readiness["layers"]["product"]["proof_points"])
        self.assertIn("repository-level license position is documented", readiness["layers"]["product"]["proof_points"])
        self.assertIn("global usage rights and valuation model is documented", readiness["layers"]["product"]["proof_points"])
        self.assertEqual(
            readiness["layers"]["commercial_chain"]["local_readiness_state"],
            "locally_verified_waiting_external_inputs",
        )
        self.assertIn(
            "protected webhook receiver candidate is separated from public portal pages",
            readiness["layers"]["commercial_chain"]["proof_points"],
        )
        self.assertIn(
            "protected webhook handler exists in the local protected runtime",
            readiness["layers"]["commercial_chain"]["proof_points"],
        )
        self.assertIn(
            "protected webhook runtime is locally self-verified through signature and replay checks",
            readiness["layers"]["commercial_chain"]["proof_points"],
        )
        self.assertEqual(readiness["neutral_rating"]["target_score"], "10/10")
        self.assertEqual(readiness["neutral_rating"]["current_score"], "8/10_local_blueprint")
        self.assertFalse(readiness["neutral_rating"]["production_claim_allowed"])
        self.assertIn(
            "sign a global usage rights agreement before granting global commercial rights",
            readiness["neutral_rating"]["open_10_10_gates"],
        )

    def test_runtime_input_and_docs_exist(self) -> None:
        runtime_input = self._load_json("config/reference-pilot-runtime-input.json")
        export_fixture = self._load_json("manifests/previews/reference-pilot-installed-bridge-runtime-export.json")
        self.assertEqual(runtime_input["status"], "captured_from_installed_bridge")
        self.assertEqual(runtime_input["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertTrue(runtime_input["domain_match"])
        self.assertTrue(runtime_input["url_normalization_clean"])
        self.assertTrue(runtime_input["baseline_captured"])
        self.assertEqual(runtime_input["mode"], "safe_mode")
        self.assertEqual(runtime_input["optimization_gate"], "reversible_change_ready")
        self.assertTrue(runtime_input["operator_inputs_complete"])
        self.assertTrue(runtime_input["source_mapping_confirmed"])
        self.assertEqual(
            runtime_input["next_smallest_safe_step"],
            "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
        )
        self.assertEqual(validate_reference_pilot_runtime_input(runtime_input), [])
        self.assertEqual(
            export_fixture["runtime_context"]["reference_pilot_runtime_snapshot"]["source"],
            "installed_bridge_runtime_snapshot",
        )
        self.assertEqual(
            export_fixture["runtime_context"]["reference_pilot_runtime_snapshot"]["next_smallest_safe_step"],
            runtime_input["next_smallest_safe_step"],
        )
        for relative_path in (
            "docs/global-productization-readiness-model.md",
            "docs/global-usage-rights-and-valuation-model.md",
            "docs/reference-pilot-runtime-input-model.md",
            "docs/external-inputs-required-for-real-cutover.md",
            "LICENSE.md",
        ):
            with self.subTest(path=relative_path):
                self.assertTrue((self.workspace_root / relative_path).exists())

    def test_closeout_readiness_moves_to_review_after_backup_restore_and_source_mapping_close(self) -> None:
        export_fixture = self._load_json("manifests/previews/reference-pilot-installed-bridge-runtime-export.json")
        closeout = build_reference_pilot_closeout_readiness(export_fixture)
        self.assertEqual(closeout["status"], "ready_for_closeout_review")
        self.assertEqual(closeout["decision"], "prepare_reference_pilot_closeout_review")
        self.assertEqual(closeout["optimization_gate"], "reversible_change_ready")
        self.assertEqual(
            closeout["next_smallest_safe_step"],
            "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
        )
        self.assertEqual(closeout["open_blockers"], [])

    def test_built_readiness_artifact_is_consistent(self) -> None:
        payload = self._load_json("manifests/previews/final-global-productization-readiness.json")
        readiness = payload["global_productization_readiness"]
        self.assertEqual(readiness["status"], "commercial_chain_not_closed")
        self.assertIn("ai_governance", readiness["layers"])
        self.assertIn("reference_pilot", readiness["layers"])
        self.assertIn("commercial_chain", readiness["layers"])
        self.assertIn("operations", readiness["layers"])
        self.assertIn("product", readiness["layers"])
        self.assertEqual(readiness["layers"]["reference_pilot"]["status"], "ready_for_reference_pilot")
        self.assertEqual(
            readiness["layers"]["commercial_chain"]["local_readiness_state"],
            "locally_verified_waiting_external_inputs",
        )
        self.assertIn("neutral_rating", readiness)
        self.assertEqual(readiness["neutral_rating"]["target_score"], "10/10")


if __name__ == "__main__":
    unittest.main()
