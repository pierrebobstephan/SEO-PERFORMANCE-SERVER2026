from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from electri_city_ops.orchestrator import run_cycle


CONFIG_TEMPLATE = """
[system]
mode = "observe_only"
timezone = "UTC"

[storage]
database = "var/state/ops.sqlite3"
json_state_dir = "var/state/json"
reports_dir = "var/reports"
logs_dir = "var/logs"

[schedule]
cycle_interval_minutes = 15

[targets]
domains = []
user_agent = "ElectriCityOps/Test"
request_timeout_seconds = 5
max_response_bytes = 4096

[permissions]
allow_remote_fetch = false
allow_external_changes = false
allow_workspace_self_healing = true

[thresholds]
warning_response_ms = 1000
critical_response_ms = 2000
large_html_bytes = 200000

[reports]
formats = ["json", "markdown"]

[notifications.email]
enabled = false
sender = ""
recipients = []
smtp_host = ""
smtp_port = 587
smtp_username = ""
smtp_password = ""
starttls = true
"""


class CycleSmokeTests(unittest.TestCase):
    def test_observe_only_cycle_generates_reports_and_state(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "config"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "settings.toml"
            config_path.write_text(CONFIG_TEMPLATE, encoding="utf-8")

            result = run_cycle(config_path, root)

            self.assertEqual(result.status, "validated")
            self.assertTrue(any(item.title == "No target domains configured" for item in result.findings))
            self.assertTrue(any(item.name == "doctrine_policy_schema_valid" and item.success for item in result.validations))
            self.assertTrue(any(item.name == "doctrine_external_changes_locked" and item.success for item in result.validations))
            self.assertTrue((root / "var" / "reports" / "latest.json").exists())
            self.assertTrue((root / "var" / "reports" / "latest.md").exists())
            self.assertTrue((root / "var" / "reports" / "rollups" / "1d.json").exists())
            self.assertTrue((root / "var" / "state" / "ops.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
