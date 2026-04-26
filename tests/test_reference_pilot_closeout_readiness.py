from pathlib import Path
import json
import unittest

from electri_city_ops.productization import build_reference_pilot_closeout_readiness


class ReferencePilotCloseoutReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def _load_json(self, relative_path: str) -> dict:
        return json.loads((self.workspace_root / relative_path).read_text(encoding="utf-8"))

    def test_closeout_builder_tool_and_doc_exist(self) -> None:
        self.assertTrue((self.workspace_root / "tools" / "build_reference_pilot_closeout_readiness.py").exists())
        self.assertTrue((self.workspace_root / "docs" / "reference-pilot-closeout-runbook.md").exists())

    def test_closeout_readiness_uses_runtime_export_and_is_ready_for_review(self) -> None:
        export_fixture = self._load_json("manifests/previews/reference-pilot-installed-bridge-runtime-export.json")
        closeout = build_reference_pilot_closeout_readiness(export_fixture)
        items = {item["key"]: item for item in closeout["closeout_items"]}

        self.assertEqual(closeout["status"], "ready_for_closeout_review")
        self.assertEqual(closeout["decision"], "prepare_reference_pilot_closeout_review")
        self.assertEqual(closeout["optimization_gate"], "reversible_change_ready")
        self.assertEqual(items["backup_confirmation"]["status"], "green")
        self.assertEqual(items["restore_confirmation"]["status"], "green")
        self.assertEqual(items["source_mapping_confirmed"]["status"], "green")
        self.assertEqual(closeout["open_blockers"], [])


if __name__ == "__main__":
    unittest.main()
