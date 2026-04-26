import json
from pathlib import Path
import tempfile
import unittest

from electri_city_ops.config import load_config
from electri_city_ops.http_probe import FetchResult
from electri_city_ops.private_site_report import (
    build_private_site_recommend_only_report,
    render_private_site_report_markdown,
    resolve_private_site_report_email_config,
)


class _FakeProbe:
    def __init__(self, payloads: dict[str, FetchResult]) -> None:
        self.payloads = payloads

    def fetch(self, url: str) -> FetchResult:
        return self.payloads[url]


class PrivateSiteReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.app_config, _ = load_config("config/settings.toml", self.workspace_root)

    def _env_file_password_present(self) -> bool:
        env_path = self.workspace_root / "deploy/systemd/private-site-report.env"
        for line in env_path.read_text().splitlines():
            if line.startswith("SMTP_PASSWORD="):
                return bool(line.split("=", 1)[1].strip())
        return False

    def test_private_site_report_profile_exists_and_uses_ionos_env_refs(self) -> None:
        profile = json.loads((self.workspace_root / "config/private-site-recommend-only-report.json").read_text())
        self.assertEqual(profile["bound_domain"], "electri-c-ity-studios-24-7.com")
        self.assertEqual(profile["runtime_guardrail_snapshot"]["optimization_gate"], "recommend_only")
        self.assertEqual(profile["email_delivery"]["recipient"], "pierre.stephan1@outlook.com")
        self.assertTrue(profile["email_delivery"]["enabled"])
        self.assertEqual(profile["email_delivery"]["smtp_host"], "smtp.ionos.de")
        self.assertEqual(profile["email_delivery"]["env_load_point"], "deploy/systemd/private-site-report.env")
        self.assertEqual(profile["email_delivery"]["sender_env"], "SMTP_FROM")
        self.assertEqual(profile["email_delivery"]["smtp_username_env"], "SMTP_USER")
        self.assertEqual(profile["email_delivery"]["smtp_password_env"], "SMTP_PASSWORD")
        self.assertTrue((self.workspace_root / "deploy/systemd/electri-city-private-site-report.service").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/electri-city-private-site-report.timer").exists())
        self.assertTrue((self.workspace_root / "deploy/cron/electri-city-private-site-report.cron").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/electri-city-private-site-report.service.example").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/electri-city-private-site-report.timer.example").exists())
        self.assertTrue((self.workspace_root / "deploy/cron/electri-city-private-site-report.cron.example").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/private-site-report.env.example").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/private-site-report.env").exists())

    def test_activation_artifacts_use_expected_paths(self) -> None:
        service_text = (self.workspace_root / "deploy/systemd/electri-city-private-site-report.service").read_text()
        timer_text = (self.workspace_root / "deploy/systemd/electri-city-private-site-report.timer").read_text()
        cron_text = (self.workspace_root / "deploy/cron/electri-city-private-site-report.cron").read_text()
        self.assertIn("EnvironmentFile=/opt/electri-city-ops/deploy/systemd/private-site-report.env", service_text)
        self.assertIn("tools/build_private_site_recommend_only_report.py --config config/private-site-recommend-only-report.json --settings config/settings.toml --send-email", service_text)
        self.assertIn("OnCalendar=*-*-* 08:00:00", timer_text)
        self.assertIn("Unit=electri-city-private-site-report.service", timer_text)
        self.assertIn("/opt/electri-city-ops/deploy/systemd/private-site-report.env", cron_text)
        self.assertIn("/usr/bin/python3 tools/build_private_site_recommend_only_report.py --config config/private-site-recommend-only-report.json --settings config/settings.toml --send-email", cron_text)

    def test_build_private_site_report_detects_short_meta_and_multiple_h1(self) -> None:
        html_home = """
        <html lang="en"><head>
        <title>Electri_C_ity Studios | 24/7 Online Radio & Crypto Art</title>
        <meta name="description" content="Short homepage description." />
        <meta name="robots" content="follow, index" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="canonical" href="https://electri-c-ity-studios-24-7.com/" />
        </head><body><h1>Hero</h1><h1>Duplicate</h1></body></html>
        """
        html_about = """
        <html lang="en"><head>
        <title>about-us - Electri_C_ity - Studios 24/7</title>
        <meta name="description" content="This about page description is intentionally long enough to be considered acceptable for the recommend only report flow." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="robots" content="follow, index" />
        <link rel="canonical" href="https://electri-c-ity-studios-24-7.com/about-us/" />
        </head><body><h1>About</h1><h1>Again</h1></body></html>
        """
        urls = {
            "https://electri-c-ity-studios-24-7.com/": FetchResult(
                requested_url="https://electri-c-ity-studios-24-7.com/",
                final_url="https://electri-c-ity-studios-24-7.com/",
                status_code=200,
                headers={},
                body=html_home,
                elapsed_ms=210.0,
                body_bytes=len(html_home),
                truncated=False,
            ),
            "https://electri-c-ity-studios-24-7.com/about-us/": FetchResult(
                requested_url="https://electri-c-ity-studios-24-7.com/about-us/",
                final_url="https://electri-c-ity-studios-24-7.com/about-us/",
                status_code=200,
                headers={},
                body=html_about,
                elapsed_ms=180.0,
                body_bytes=len(html_about),
                truncated=False,
            ),
        }
        profile = {
            "report_id": "test-private-report",
            "bound_domain": "electri-c-ity-studios-24-7.com",
            "runtime_guardrail_snapshot": {
                "plugin_mode": "safe_mode",
                "optimization_gate": "recommend_only",
                "coexistence_mode": "rank_math_controlled_coexistence",
                "active_seo_plugin": "seo-by-rank-math/rank-math.php",
            },
            "pages": [
                {"label": "Homepage", "page_type": "homepage", "url": "https://electri-c-ity-studios-24-7.com/"},
                {"label": "About Us", "page_type": "about", "url": "https://electri-c-ity-studios-24-7.com/about-us/"},
            ],
            "email_delivery": {
                "enabled": False,
                "recipient": "pierre.stephan1@outlook.com",
                "smtp_host": "smtp.ionos.de",
                "smtp_port": 587,
                "starttls": True,
                "sender_env": "SMTP_FROM",
                "smtp_username_env": "SMTP_USER",
                "smtp_password_env": "SMTP_PASSWORD",
            },
        }
        report = build_private_site_recommend_only_report(profile, self.app_config, _FakeProbe(urls))
        self.assertEqual(report["summary"]["page_count"], 2)
        self.assertEqual(report["summary"]["live_change_state"], "no_live_change_proposed")
        self.assertEqual(report["innovation_control_deck"]["execution_mode"], "controlled_growth_under_external_seo_owner")
        self.assertEqual(report["priority_execution_queue"][0]["label"], "Homepage")
        self.assertEqual(report["priority_execution_queue"][0]["priority"], "high")
        self.assertIn("heading", report["priority_execution_queue"][0]["focus"])
        self.assertEqual(report["automation_contract_state"]["status"], "valid")
        self.assertEqual(len(report["automation_candidates"]), 1)
        self.assertEqual(report["automation_candidates"][0]["action_type"], "rank_math_homepage_meta_description_update")
        self.assertEqual(report["automation_candidates"][0]["execution_lane"], "admin_confirmed_assisted_resolution_only")
        self.assertEqual(report["automation_candidates"][0]["runtime_gate"], "recommend_only")
        self.assertEqual(report["automation_candidates"][0]["active_seo_owner"], "seo-by-rank-math/rank-math.php")
        self.assertEqual(report["automation_candidates"][0]["bound_domain"], "electri-c-ity-studios-24-7.com")
        self.assertEqual(report["automation_candidates"][0]["target_domain"], "electri-c-ity-studios-24-7.com")
        self.assertEqual(report["automation_candidates"][0]["target_field"], "rank_math_titles.homepage_description")
        self.assertEqual(report["automation_candidates"][0]["automation_contract_id"], "ac-rank-math-homepage-meta-description-update-v1")
        self.assertEqual(report["automation_candidates"][0]["automation_contract_state"], "contract_verified")
        self.assertTrue(report["automation_candidates"][0]["requires_admin_confirmation"])
        self.assertTrue(report["automation_candidates"][0]["requires_rollback"])
        homepage = report["pages"][0]
        about_page = report["pages"][1]
        self.assertTrue(any(item["title"] == "Short meta description" for item in homepage["findings"]))
        self.assertTrue(any(item["title"] == "Multiple H1 headings" for item in homepage["findings"]))
        self.assertTrue(any(item["title"] == "Slug-style about title" for item in about_page["findings"]))
        markdown = render_private_site_report_markdown(report)
        self.assertIn("Private Site Recommend-Only Report", markdown)
        self.assertIn("Innovation Control Deck", markdown)
        self.assertIn("Admin-Confirmed Automation Candidates", markdown)
        self.assertIn("Contract status: `valid`", markdown)
        self.assertIn("Automation contract: `ac-rank-math-homepage-meta-description-update-v1`", markdown)
        self.assertIn("Runtime gate: `recommend_only`", markdown)
        self.assertIn("Priority Execution Queue", markdown)
        self.assertIn("Homepage", markdown)
        self.assertIn("About Us", markdown)

    def test_resolve_private_site_report_email_config_reports_missing_envs(self) -> None:
        profile = {
            "email_delivery": {
                "enabled": True,
                "recipient": "pierre.stephan1@outlook.com",
                "smtp_host": "smtp.ionos.de",
                "smtp_port": 587,
                "starttls": True,
                "sender_env": "SMTP_FROM",
                "smtp_username_env": "SMTP_USER",
                "smtp_password_env": "SMTP_PASSWORD",
            }
        }
        config, missing = resolve_private_site_report_email_config(profile)
        self.assertTrue(config.enabled)
        self.assertIn("SMTP_FROM", missing)
        self.assertIn("SMTP_USER", missing)
        self.assertIn("SMTP_PASSWORD", missing)

    def test_resolve_private_site_report_email_config_reads_local_env_file(self) -> None:
        profile = {
            "email_delivery": {
                "enabled": True,
                "recipient": "pierre.stephan1@outlook.com",
                "smtp_host": "smtp.ionos.de",
                "smtp_port": 587,
                "starttls": True,
                "env_load_point": "deploy/systemd/private-site-report.env",
                "sender_env": "SMTP_FROM",
                "smtp_username_env": "SMTP_USER",
                "smtp_password_env": "SMTP_PASSWORD",
            }
        }
        config, missing = resolve_private_site_report_email_config(profile, self.workspace_root)
        self.assertEqual(config.sender, "pierre.stephan1@electri-c-ity-studios.com")
        self.assertEqual(config.smtp_username, "pierre.stephan1@electri-c-ity-studios.com")
        self.assertNotIn("SMTP_FROM", missing)
        self.assertNotIn("SMTP_USER", missing)
        if self._env_file_password_present():
            self.assertNotIn("SMTP_PASSWORD", missing)
        else:
            self.assertIn("SMTP_PASSWORD", missing)

    def test_build_private_site_report_uses_env_load_point_for_delivery_state(self) -> None:
        html = """
        <html lang="en"><head>
        <title>Electri_C_ity Studios</title>
        <meta name="description" content="This description is long enough to avoid a short-description warning in this test fixture." />
        <meta name="robots" content="follow, index" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="canonical" href="https://electri-c-ity-studios-24-7.com/" />
        </head><body><h1>Hero</h1></body></html>
        """
        profile = {
            "report_id": "test-private-report-email-state",
            "bound_domain": "electri-c-ity-studios-24-7.com",
            "runtime_guardrail_snapshot": {
                "plugin_mode": "safe_mode",
                "optimization_gate": "recommend_only",
                "coexistence_mode": "rank_math_controlled_coexistence",
            },
            "pages": [
                {"label": "Homepage", "page_type": "homepage", "url": "https://electri-c-ity-studios-24-7.com/"},
            ],
            "email_delivery": {
                "enabled": True,
                "recipient": "pierre.stephan1@outlook.com",
                "smtp_profile": "ionos_starttls_submission",
                "smtp_host": "smtp.ionos.de",
                "smtp_port": 587,
                "starttls": True,
                "env_load_point": "deploy/systemd/private-site-report.env",
                "sender_env": "SMTP_FROM",
                "smtp_username_env": "SMTP_USER",
                "smtp_password_env": "SMTP_PASSWORD",
            },
        }
        urls = {
            "https://electri-c-ity-studios-24-7.com/": FetchResult(
                requested_url="https://electri-c-ity-studios-24-7.com/",
                final_url="https://electri-c-ity-studios-24-7.com/",
                status_code=200,
                headers={},
                body=html,
                elapsed_ms=180.0,
                body_bytes=len(html),
                truncated=False,
            ),
        }
        report = build_private_site_recommend_only_report(profile, self.app_config, _FakeProbe(urls))
        self.assertEqual(report["email_delivery_state"]["smtp_profile"], "ionos_starttls_submission")
        if self._env_file_password_present():
            self.assertEqual(report["email_delivery_state"]["missing_env_refs"], [])
            self.assertEqual(report["email_delivery_state"]["activation_state"], "ready")
        else:
            self.assertEqual(report["email_delivery_state"]["missing_env_refs"], ["SMTP_PASSWORD"])
            self.assertEqual(report["email_delivery_state"]["activation_state"], "operator_input_required")


if __name__ == "__main__":
    unittest.main()
