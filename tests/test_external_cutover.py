import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from electri_city_ops.external_cutover import (
    build_external_cutover_package,
    load_external_cutover_checklist,
    validate_external_cutover_checklist,
)


class ExternalCutoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def test_external_cutover_checklist_is_valid(self) -> None:
        payload = load_external_cutover_checklist(self.workspace_root)
        self.assertEqual(validate_external_cutover_checklist(payload), [])
        self.assertEqual(payload["status"], "operator_input_required")
        self.assertEqual(
            payload["next_smallest_safe_step"],
            "inject PayPal env refs and verify the protected webhook receiver in the real staging server context",
        )

    def test_external_cutover_package_is_ready_for_external_execution(self) -> None:
        package = build_external_cutover_package(self.workspace_root)
        self.assertEqual(package["status"], "ready_for_external_execution")
        self.assertEqual(
            package["local_preconditions"]["commercial_chain_local_readiness_state"],
            "locally_verified_waiting_external_inputs",
        )
        self.assertEqual(package["local_preconditions"]["local_webhook_runtime_verification_state"], "passed")
        self.assertIn("PAYPAL_BUSINESS_CLIENT_ID", package["required_external_inputs"])
        self.assertIn(
            "protected PayPal webhook receiver verification and activation",
            package["required_external_inputs"],
        )
        self.assertIn("paypal_business_client_id_env_ref", package["blocking_pending_item_ids"])
        self.assertIn("protected_webhook_target_delivery_verification", package["blocking_pending_item_ids"])
        self.assertIn("phase_summaries", package)
        self.assertTrue(package["ordered_execution_steps"])

    def test_builder_tool_roundtrip_works(self) -> None:
        self.assertTrue((self.workspace_root / "tools" / "build_external_cutover_package.py").exists())
        self.assertTrue((self.workspace_root / "schemas" / "external-cutover-checklist.schema.json").exists())

        tmp_root = self.workspace_root / "var" / "state" / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp_root) as tmp_dir:
            output_path = Path(tmp_dir) / "external-cutover-package.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/build_external_cutover_package.py",
                    "--output",
                    str(output_path.relative_to(self.workspace_root)),
                    "--built-at",
                    "2026-04-22T00:00:00Z",
                ],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            package = payload["external_cutover_package"]
            self.assertEqual(package["status"], "ready_for_external_execution")
            self.assertEqual(package["local_preconditions"]["local_webhook_runtime_verification_state"], "passed")


if __name__ == "__main__":
    unittest.main()
