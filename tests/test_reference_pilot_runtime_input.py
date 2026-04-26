import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from electri_city_ops.productization import (
    REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS,
    build_reference_pilot_runtime_input,
    validate_reference_pilot_runtime_input,
)


class ReferencePilotRuntimeInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def test_build_runtime_input_from_direct_snapshot(self) -> None:
        payload = build_reference_pilot_runtime_input(
            {
                "reference_pilot_runtime_snapshot": {
                    "schema_version": 1,
                    "source": "installed_bridge_runtime_snapshot",
                    "status": "captured_from_installed_bridge",
                    "captured_at": "2026-04-03T00:00:00Z",
                    "bound_domain": "wp.electri-c-ity-studios-24-7.com",
                    "current_domain": "wp.electri-c-ity-studios-24-7.com",
                    "path_base": "/wordpress/",
                    "domain_match": True,
                    "url_normalization_clean": True,
                    "baseline_captured": True,
                    "blocking_conflicts": "green",
                    "mode": "safe_mode",
                    "optimization_gate": "reversible_change_ready",
                    "operator_inputs_complete": True,
                    "source_mapping_confirmed": True,
                    "open_blockers": [],
                    "next_smallest_safe_step": "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
                    "notes": ["Captured from installed bridge runtime."],
                }
            }
        )
        self.assertEqual(payload["status"], REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS)
        self.assertEqual(payload["path_base"], "/wordpress/")
        self.assertTrue(payload["operator_inputs_complete"])
        self.assertTrue(payload["source_mapping_confirmed"])
        self.assertEqual(
            payload["next_smallest_safe_step"],
            "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
        )
        self.assertEqual(validate_reference_pilot_runtime_input(payload), [])

    def test_build_runtime_input_from_runtime_context_fallback(self) -> None:
        payload = build_reference_pilot_runtime_input(
            {
                "runtime_context": {
                    "current_domain": "wp.electri-c-ity-studios-24-7.com",
                    "bound_domain": "wp.electri-c-ity-studios-24-7.com",
                    "path_base": "/wordpress/",
                    "mode": "safe_mode",
                    "domain_match": True,
                    "url_normalization_clean": True,
                    "baseline_captured": True,
                    "operator_inputs_complete": True,
                    "source_mapping_confirmed": True,
                    "open_blockers": [],
                    "next_smallest_safe_step": "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
                    "installation_health_signals": {
                        "blocking_conflicts": "green",
                        "optimization_gate": "reversible_change_ready",
                    },
                },
                "validation_snapshot": {
                    "baseline_status": {
                        "captured": True,
                        "url_normalization_clean": True,
                    }
                },
            }
        )
        self.assertEqual(payload["bound_domain"], "wp.electri-c-ity-studios-24-7.com")
        self.assertEqual(payload["optimization_gate"], "reversible_change_ready")
        self.assertEqual(
            payload["next_smallest_safe_step"],
            "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
        )
        self.assertIn("stay in staging", payload["notes"][0])
        self.assertEqual(validate_reference_pilot_runtime_input(payload), [])

    def test_validate_runtime_input_rejects_missing_runtime_booleans(self) -> None:
        issues = validate_reference_pilot_runtime_input(
            {
                "schema_version": 1,
                "source": "installed_bridge_runtime_snapshot",
                "status": "captured_from_installed_bridge",
                "bound_domain": "wp.electri-c-ity-studios-24-7.com",
                "path_base": "/wordpress/",
                "blocking_conflicts": "green",
                "mode": "safe_mode",
                "optimization_gate": "blocked",
                "open_blockers": [],
            }
        )
        self.assertIn("reference pilot runtime input domain_match must be a boolean", issues)
        self.assertIn("reference pilot runtime input operator_inputs_complete must be a boolean", issues)
        self.assertIn("reference pilot runtime input next_smallest_safe_step must be set", issues)

    def test_builder_tool_exists(self) -> None:
        self.assertTrue((self.workspace_root / "tools" / "build_reference_pilot_runtime_input.py").exists())
        self.assertTrue((self.workspace_root / "schemas" / "reference-pilot-runtime-input.schema.json").exists())

    def test_builder_roundtrip_works_with_local_export_fixture(self) -> None:
        fixture_path = self.workspace_root / "manifests" / "previews" / "reference-pilot-installed-bridge-runtime-export.json"
        self.assertTrue(fixture_path.exists())

        tmp_root = self.workspace_root / "var" / "state" / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp_root) as tmp_dir:
            output_path = Path(tmp_dir) / "reference-pilot-runtime-input.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/build_reference_pilot_runtime_input.py",
                    "--input",
                    str(fixture_path.relative_to(self.workspace_root)),
                    "--output",
                    str(output_path.relative_to(self.workspace_root)),
                ],
                cwd=self.workspace_root,
                env={"PYTHONPATH": "src"},
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], REFERENCE_PILOT_RUNTIME_CAPTURED_STATUS)
            self.assertEqual(payload["current_domain"], "wp.electri-c-ity-studios-24-7.com")
            self.assertEqual(payload["path_base"], "/wordpress/")
            self.assertEqual(payload["optimization_gate"], "reversible_change_ready")
            self.assertTrue(payload["operator_inputs_complete"])
            self.assertTrue(payload["source_mapping_confirmed"])
            self.assertEqual(
                payload["next_smallest_safe_step"],
                "stay in staging, validate the reversible homepage meta preparation path, and keep rollback ready",
            )
            self.assertEqual(validate_reference_pilot_runtime_input(payload), [])


if __name__ == "__main__":
    unittest.main()
