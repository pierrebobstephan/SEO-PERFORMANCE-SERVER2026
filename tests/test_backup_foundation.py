import json
from pathlib import Path
import unittest

from electri_city_ops.backup_foundation import (
    collect_backup_inventory,
    load_backup_policy,
    migration_preflight,
    post_restore_validation,
)


class BackupFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()

    def test_backup_policy_contains_required_sets(self) -> None:
        policy = load_backup_policy(self.workspace_root)
        names = {item["name"] for item in policy["backup_sets"]}
        self.assertIn("application_code", names)
        self.assertIn("configuration", names)
        self.assertIn("database_and_state", names)
        self.assertIn("portal_and_deploy_artifacts", names)
        self.assertIn("certificates", policy["separate_sensitive_material"])
        self.assertIn("secrets", policy["separate_sensitive_material"])

    def test_backup_inventory_reports_database_and_portal_config(self) -> None:
        payload = collect_backup_inventory(self.workspace_root)
        self.assertTrue(payload["public_portal_config_present"])
        self.assertTrue(payload["database_path"].endswith("var/state/ops.sqlite3"))
        backup_sets = {item["name"]: item for item in payload["backup_sets"]}
        self.assertTrue(backup_sets["database_and_state"]["all_present"])
        self.assertTrue(backup_sets["configuration"]["all_present"])

    def test_post_restore_validation_checks_public_and_protected_routes(self) -> None:
        payload = post_restore_validation(self.workspace_root)
        self.assertTrue(payload["config_loaded"])
        self.assertTrue(payload["portal_loaded"])
        self.assertEqual(payload["health_payload"]["status"], "ok")
        self.assertTrue(all(item["ok"] for item in payload["public_checks"]))
        self.assertTrue(all(item["ok"] for item in payload["protected_checks"]))

    def test_migration_preflight_stays_local_and_requires_external_inputs(self) -> None:
        payload = migration_preflight(self.workspace_root)
        self.assertTrue(payload["all_required_backup_sets_present"])
        self.assertIn("target_server_hostname_or_ip", payload["external_input_required"])
        self.assertIn("real Hetzner snapshot creation", payload["approval_required_operations"])

    def test_backup_docs_exist(self) -> None:
        docs = [
            "docs/backup-and-snapshot-strategy.md",
            "docs/restore-runbook.md",
            "docs/server-migration-plan.md",
            "docs/disaster-recovery-boundaries.md",
            "docs/backup-scope-register.md",
            "docs/secret-and-certificate-handling-plan.md",
            "docs/hetzner-scale-up-migration-checklist.md",
            "docs/backup-restore-test-log-template.md",
            "docs/public-portal-backup-and-migration-positioning.md",
        ]
        for relative in docs:
            with self.subTest(path=relative):
                self.assertTrue((self.workspace_root / relative).exists())


if __name__ == "__main__":
    unittest.main()
