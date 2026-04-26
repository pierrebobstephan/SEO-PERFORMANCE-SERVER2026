import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from electri_city_ops.config import load_config
from electri_city_ops.public_portal import (
    _google_translate_texts,
    _partition_translation_batches,
    build_public_health_payload,
    build_public_portal_snapshot,
    load_public_portal_config,
    load_public_portal_operator_config,
    render_robots_txt,
    render_sitemap_xml,
    resolve_portal_request,
)


class PublicPortalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.config, _ = load_config("config/settings.toml", self.workspace_root)
        self.portal = load_public_portal_config(self.workspace_root)

    def test_portal_binds_localhost_only(self) -> None:
        self.assertEqual(self.portal.bind_host, "127.0.0.1")
        self.assertEqual(self.portal.selected_subdomain, "site-optimizer.electri-c-ity-studios-24-7.com")

    def test_public_snapshot_contains_safe_status(self) -> None:
        snapshot = build_public_portal_snapshot(self.workspace_root, self.config, self.portal)
        self.assertIn("portal_status", snapshot)
        self.assertFalse(snapshot["portal_status"]["operator_console_public"])
        self.assertGreaterEqual(len(snapshot["reference_metrics"]), 4)
        self.assertIn("readiness_summary", snapshot)
        self.assertEqual(len(snapshot["readiness_summary"]), 5)
        self.assertEqual(snapshot["operator_fields"]["legal_readiness_state"], "configured")

    def test_home_route_contains_landingpage_seo_markup(self) -> None:
        response = resolve_portal_request("/", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Modern sales platform", body)
        self.assertIn("Premium WordPress SEO and performance growth platform", body)
        self.assertIn("WordPress SEO and Performance Optimization Platform", body)
        self.assertIn("A guarded WordPress SEO and Performance Suite with visible public tiers.", body)
        self.assertIn("Buyer-readable installed insights after protected plugin activation", body)
        self.assertIn("After protected activation, the bridge is designed to explain what it sees", body)
        self.assertIn("What to prepare before requesting access", body)
        self.assertIn("What remains approval_required", body)
        self.assertIn("Guardian Core Monthly: EUR 2,500.00 / month for one exact licensed domain", body)
        self.assertIn("Controlled validation and protected access expectations stay visible across the public monthly plans", body)
        self.assertIn('rel="canonical" href="https://site-optimizer.electri-c-ity-studios-24-7.com/"', body)
        self.assertIn('"@type": "FAQPage"', body)
        self.assertIn("Differentiation", body)
        self.assertIn("Impressum / Legal Notice", body)
        self.assertIn("Privacy Policy", body)
        self.assertIn("Terms / License Terms", body)
        self.assertIn("Refund Policy", body)
        self.assertIn("Contact / Support", body)
        self.assertIn("Pierre (Bob) Stephan", body)
        self.assertIn("DE363614431", body)
        self.assertIn("pierre.stephan1@electri-c-ity-studios.com", body)

    def test_home_and_explore_harmonize_public_tiers_and_protected_delivery(self) -> None:
        home = resolve_portal_request("/", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        explore = resolve_portal_request("/explore", self.workspace_root, self.config, self.portal).body.decode(
            "utf-8"
        )
        self.assertIn('href="/buy"', home)
        self.assertIn('href="/terms"', home)
        self.assertIn('href="/licensing"', home)
        self.assertIn('href="/downloads"', home)
        self.assertIn('href="/support"', home)
        self.assertIn("Guardian Core Monthly: one exact licensed domain", explore)
        self.assertIn("Sovereign Enterprise Monthly: commercially reviewed exact licensed multi-domain scope", explore)
        self.assertIn("Sovereign Critical Monthly: individually approved exact licensed high-compliance scope", explore)
        self.assertIn("Documentation, validation posture and protected access expectations remain visible across the public plans", explore)
        self.assertIn("bounded, explainable and reversible", explore)
        self.assertIn("The bridge is built to explain itself after installation", explore)
        self.assertIn('href="/buy"', explore)
        self.assertIn('href="/terms"', explore)
        self.assertIn('href="/licensing"', explore)
        self.assertIn('href="/downloads"', explore)
        self.assertIn('href="/support"', explore)
        self.assertIn('href="/docs"', explore)

    def test_plugin_page_mentions_rank_math_coexistence(self) -> None:
        response = resolve_portal_request("/plugin", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Rank Math", body)
        self.assertIn("Homepage Meta Description is the first planned plugin pilot", body)
        self.assertIn("Installed admin surface shows scope, health, delivery and cutover state", body)
        self.assertIn('rel="canonical" href="https://site-optimizer.electri-c-ity-studios-24-7.com/plugin"', body)

    def test_download_page_states_gated_access(self) -> None:
        response = resolve_portal_request("/downloads", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("No open anonymous production download", body)
        self.assertIn("What to prepare before requesting access", body)
        self.assertIn("Request-ready does not mean open delivery", body)
        self.assertIn("protected delivery and installed buyer visibility fit together", body)
        self.assertIn("Portal-visible readiness without protected execution", body)
        self.assertIn("approval_required", body)
        self.assertIn("Legal readiness", body)
        self.assertNotIn("<form", body)
        self.assertNotIn("/downloads/private", body)

    def test_support_page_keeps_operator_input_required_honest(self) -> None:
        response = resolve_portal_request("/support", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("operator input required", body)
        self.assertIn("Support can be public. Protected operator authority cannot.", body)
        self.assertIn("buyer-visible model the installed bridge is designed to expose", body)
        self.assertIn("commercial inquiry", body.lower())
        self.assertIn("What support needs from you", body)
        self.assertIn("Support readiness", body)
        self.assertNotIn("<form", body)

    def test_licensing_page_prepares_commercial_placeholders_without_inventing_pricing(self) -> None:
        response = resolve_portal_request("/licensing", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Who this licensing model is for", body)
        self.assertIn("Pricing model: configured public tiers", body)
        self.assertIn("Quoted package tiers: configured public tiers", body)
        self.assertIn("buyer-readable scope and delivery visibility inside the installed bridge", body)
        self.assertIn("What remains approval_required", body)
        self.assertIn("Commercial readiness", body)
        self.assertIn("Related pages", body)

    def test_legal_page_is_public_and_contains_synced_identity(self) -> None:
        response = resolve_portal_request("/legal", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Impressum / Legal Notice", body)
        self.assertIn("Pierre (Bob) Stephan", body)
        self.assertIn("trading as Electri_C_ity - Studios", body)
        self.assertIn("DE363614431", body)
        self.assertIn("Invoices are issued for completed orders.", body)
        self.assertNotIn("<form", body)

    def test_impressum_alias_uses_legal_canonical(self) -> None:
        response = resolve_portal_request("/impressum", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn('rel="canonical" href="https://site-optimizer.electri-c-ity-studios-24-7.com/legal"', body)

    def test_privacy_page_contains_expected_synced_points(self) -> None:
        response = resolve_portal_request("/privacy", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("For privacy requests, support, licensing, billing, or technical questions", body)
        self.assertIn("PayPal", body)
        self.assertIn("Google tag / measurement scripts", body)
        self.assertIn("access, rectification, erasure, restriction, objection, and complaint", body)

    def test_terms_page_contains_expected_public_offer(self) -> None:
        response = resolve_portal_request("/terms", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Guardian Core Monthly", body)
        self.assertIn("Sovereign Enterprise Monthly", body)
        self.assertIn("Sovereign Critical Monthly", body)
        self.assertIn("EUR 2,500.00 / month", body)
        self.assertIn("EUR 9,500.00 / month", body)
        self.assertIn("EUR 25,000.00 / month", body)
        self.assertIn("Monthly optimization scope for one exact licensed domain.", body)
        self.assertIn("Monthly multi-domain optimization for an exact licensed domain set confirmed during commercial review.", body)
        self.assertIn("Monthly high-compliance scope for an individually approved exact licensed domain set.", body)
        self.assertIn("controlled SEO and performance optimization with validation and rollback.", body)
        self.assertIn("Not included under the public offer: open multi-domain rights beyond the exact licensed scope", body)
        self.assertIn("Licensed download access remains protected and scope-bound.", body)

    def test_buy_terms_and_licensing_keep_public_offer_consistent(self) -> None:
        buy = resolve_portal_request("/buy", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        terms = resolve_portal_request("/terms", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        licensing = resolve_portal_request("/licensing", self.workspace_root, self.config, self.portal).body.decode(
            "utf-8"
        )
        for body in (buy, terms):
            self.assertIn("Guardian Core Monthly", body)
            self.assertIn("Sovereign Enterprise Monthly", body)
            self.assertIn("Sovereign Critical Monthly", body)
            self.assertIn("EUR 2,500.00 / month", body)
            self.assertIn("EUR 9,500.00 / month", body)
            self.assertIn("EUR 25,000.00 / month", body)
        self.assertIn("Guardian Core Monthly: one exact licensed domain", licensing)
        self.assertIn("Sovereign Enterprise Monthly: commercially reviewed exact licensed multi-domain scope", licensing)
        self.assertIn("Sovereign Critical Monthly: individually approved exact licensed high-compliance scope", licensing)
        self.assertIn(
            "The portal now shows the public monthly plans directly: Guardian Core Monthly EUR 2,500.00, Sovereign Enterprise Monthly EUR 9,500.00 and Sovereign Critical Monthly EUR 25,000.00.",
            licensing,
        )

    def test_refund_page_contains_expected_consumer_rights(self) -> None:
        response = resolve_portal_request("/refund", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("14-day right of withdrawal", body)
        self.assertIn("Refunds remain available where required by applicable consumer law.", body)
        self.assertIn("pierre.stephan1@electri-c-ity-studios.com", body)

    def test_contact_page_is_public_and_has_no_form(self) -> None:
        response = resolve_portal_request("/contact", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Support for licensing, activation, download, billing, and technical issues is available by email.", body)
        self.assertIn("1-3 business days (Europe/Berlin)", body)
        self.assertIn("VAT ID: DE363614431", body)
        self.assertNotIn("<form", body)

    def test_explore_agencies_publishers_and_buy_routes_are_public_and_informative(self) -> None:
        expectations = {
            "/explore": "Explore the guarded routes into the WordPress optimization product.",
            "/agencies": "Agency-friendly product logic without pretending multi-domain rights.",
            "/publishers": "Built for operators who want clearer ownership over homepage SEO and performance.",
            "/buy": "Choose the public monthly plan before any protected delivery step begins.",
        }
        for route, needle in expectations.items():
            with self.subTest(route=route):
                response = resolve_portal_request(route, self.workspace_root, self.config, self.portal)
                body = response.body.decode("utf-8")
                self.assertEqual(response.status, 200)
                self.assertIn(needle, body)
                self.assertNotIn("<form", body)
                self.assertNotIn("/downloads/private", body)
        buy_body = resolve_portal_request("/buy", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        self.assertIn("EUR 2,500.00 / month", buy_body)
        self.assertIn("EUR 9,500.00 / month", buy_body)
        self.assertIn("EUR 25,000.00 / month", buy_body)
        self.assertIn("Controlled SEO and performance optimization with validation and rollback.", buy_body)
        self.assertIn("Licensed download access remains protected and scope-bound.", buy_body)

    def test_buy_page_polish_keeps_offer_clear_and_guarded(self) -> None:
        response = resolve_portal_request("/buy", self.workspace_root, self.config, self.portal)
        body = response.body.decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("Move from public visibility to protected activation", body)
        self.assertIn("A high-modern sales surface for premium WordPress optimization.", body)
        self.assertIn("<title>WordPress SEO and Performance Suite Pricing and Offer |", body)
        self.assertIn("Compare the public monthly plans", body)
        self.assertIn("Guardian Core, Sovereign Enterprise and Sovereign Critical stay visible, bounded and protected.", body)
        self.assertIn("installed bridge later stays buyer-readable, bounded and reversible", body)
        self.assertIn("Who this is for", body)
        self.assertIn("What remains protected after this public offer page", body)
        self.assertIn("Monthly optimization scope for one exact licensed domain.", body)
        self.assertIn("Monthly multi-domain optimization for an exact licensed domain set confirmed during commercial review.", body)
        self.assertIn("Monthly high-compliance scope for an individually approved exact licensed domain set.", body)
        self.assertIn("Controlled SEO and performance optimization with validation and rollback.", body)
        self.assertIn("Not included under the public offer: open multi-domain rights beyond the exact licensed scope", body)
        self.assertIn(
            "Licensed download access remains protected and scope-bound. Public pages describe the offer, but they do not open private delivery, login, activation, or customer execution flows.",
            body,
        )
        self.assertIn("Installed plugin state is designed to stay explainable to the buyer", body)
        self.assertIn('href="/terms"', body)
        self.assertIn('href="/licensing"', body)
        self.assertIn('href="/downloads"', body)
        self.assertIn('href="/support"', body)
        self.assertIn('href="/refund"', body)
        self.assertNotIn("<form", body)
        self.assertNotIn('href="/downloads/private"', body)
        self.assertNotIn('href="/api/license"', body)

    def test_home_and_buy_include_sales_offer_deck_and_journey(self) -> None:
        for route in ("/", "/buy"):
            with self.subTest(route=route):
                body = resolve_portal_request(route, self.workspace_root, self.config, self.portal).body.decode(
                    "utf-8"
                )
                self.assertIn("Public offer deck", body)
                self.assertIn("Turn interest into a governed buying decision.", body)
                self.assertIn("Guardian Core Monthly", body)
                self.assertIn("Sovereign Enterprise Monthly", body)
                self.assertIn("Sovereign Critical Monthly", body)

    def test_portal_translation_artifacts_exist(self) -> None:
        self.assertEqual(self.portal.translation.provider, "google_cloud_translation_basic_v2")
        self.assertEqual(self.portal.translation.env_load_point, "deploy/systemd/public-portal.env")
        self.assertTrue((self.workspace_root / "deploy/systemd/public-portal.env").exists())
        self.assertTrue((self.workspace_root / "deploy/systemd/public-portal.env.example").exists())

    def test_buy_page_translation_falls_back_to_english_without_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            config_dir = workspace / "config"
            deploy_dir = workspace / "deploy/systemd"
            config_dir.mkdir(parents=True, exist_ok=True)
            deploy_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "public-portal.json").write_text(
                json.dumps(
                    {
                        "bind_host": "127.0.0.1",
                        "port": 8781,
                        "selected_subdomain": "site-optimizer.electri-c-ity-studios-24-7.com",
                        "canonical_base_url": "https://site-optimizer.electri-c-ity-studios-24-7.com",
                        "product_name": "Electri City Site Optimizer",
                        "download_gate_state": "approval_required",
                        "translation": {
                            "enabled": True,
                            "provider": "google_cloud_translation_basic_v2",
                            "default_language": "en",
                            "supported_languages": ["en", "de"],
                            "api_key_env": "GOOGLE_TRANSLATE_API_KEY",
                            "env_load_point": "deploy/systemd/public-portal.env",
                            "activation_state": "operator_input_required",
                        },
                        "public_routes": ["/", "/buy", "/licensing", "/support", "/downloads", "/terms"],
                        "protected_route_prefixes": ["/operator", "/downloads/private"],
                    }
                ),
                encoding="utf-8",
            )
            (config_dir / "public-portal-operator.json").write_text(
                (self.workspace_root / "config/public-portal-operator.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (deploy_dir / "public-portal.env").write_text("GOOGLE_TRANSLATE_API_KEY=\n", encoding="utf-8")
            portal = load_public_portal_config(workspace)
            with mock.patch.dict(os.environ, {}, clear=False):
                body = resolve_portal_request("/buy?lang=de", workspace, self.config, portal).body.decode("utf-8")
            self.assertIn('lang="en"', body)
            self.assertIn("Google translation is configured as an optional portal layer", body)
            self.assertIn("Guardian Core Monthly", body)

    def test_buy_page_translation_uses_google_path_when_api_key_is_present(self) -> None:
        with mock.patch.dict(os.environ, {"GOOGLE_TRANSLATE_API_KEY": "test-key"}, clear=False):
            with mock.patch(
                "electri_city_ops.public_portal._google_translate_texts",
                side_effect=lambda texts, target_language, api_key: [f"DE::{item}" for item in texts],
            ):
                body = resolve_portal_request("/buy?lang=de", self.workspace_root, self.config, self.portal).body.decode(
                    "utf-8"
                )
        self.assertIn('lang="de"', body)
        self.assertIn("Machine-translated from the English source via Google Cloud Translation", body)
        self.assertIn("DE::Guardian Core Monthly", body)
        self.assertIn("noindex,follow,max-image-preview:large", body)

    def test_translation_batches_large_payloads_and_preserves_order(self) -> None:
        texts = [f"chunk-{index}-{'x' * 110}" for index in range(40)]
        batches = _partition_translation_batches(texts)
        self.assertGreater(len(batches), 1)
        self.assertEqual([item for batch in batches for item in batch], texts)

        class _FakeResponse:
            def __init__(self, payload: str) -> None:
                self.payload = payload

            def read(self) -> bytes:
                return self.payload.encode("utf-8")

            def __enter__(self) -> "_FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> None:
                return None

        calls: list[list[str]] = []

        def _fake_urlopen(request, timeout=10):
            query = request.data.decode("utf-8")
            items = []
            for part in query.split("&"):
                if part.startswith("q="):
                    items.append(part[2:].replace("+", " "))
            from urllib.parse import unquote_plus

            decoded = [unquote_plus(item) for item in items]
            calls.append(decoded)
            return _FakeResponse(
                json.dumps({"data": {"translations": [{"translatedText": f"T::{item}"} for item in decoded]}})
            )

        with mock.patch("electri_city_ops.public_portal.urlopen", side_effect=_fake_urlopen):
            translated = _google_translate_texts(texts, "de", "test-key")

        self.assertEqual(translated, [f"T::{item}" for item in texts])
        self.assertGreater(len(calls), 1)

    def test_crosslinks_harmonize_buy_support_and_legal_paths(self) -> None:
        home = resolve_portal_request("/", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        buy = resolve_portal_request("/buy", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        support = resolve_portal_request("/support", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        legal = resolve_portal_request("/legal", self.workspace_root, self.config, self.portal).body.decode("utf-8")
        self.assertIn('href="/buy"', home)
        self.assertIn('href="/terms"', buy)
        self.assertIn('href="/licensing"', buy)
        self.assertIn('href="/downloads"', buy)
        self.assertIn('href="/support"', buy)
        self.assertIn('href="/refund"', buy)
        self.assertIn('href="/contact"', support)
        self.assertIn('href="/privacy"', legal)
        self.assertIn('href="/terms"', legal)

    def test_operator_fields_default_to_required_when_blank(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            config_dir = workspace / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "public-portal.json").write_text(
                json.dumps(
                    {
                        "bind_host": "127.0.0.1",
                        "port": 8781,
                        "selected_subdomain": "site-optimizer.electri-c-ity-studios-24-7.com",
                        "canonical_base_url": "https://site-optimizer.electri-c-ity-studios-24-7.com",
                        "product_name": "Electri City Site Optimizer",
                        "download_gate_state": "approval_required",
                        "public_routes": ["/", "/support", "/downloads", "/licensing"],
                        "protected_route_prefixes": ["/operator", "/downloads/private"],
                    }
                ),
                encoding="utf-8",
            )
            (config_dir / "public-portal-operator.json").write_text(
                json.dumps(
                    {
                        "support_contact": "",
                        "support_email": "",
                        "commercial_inquiry_label": "",
                        "commercial_inquiry_state": "",
                        "pricing_model_state": "",
                        "package_tiers_state": "",
                        "access_request_state": "",
                        "support_readiness_state": "",
                        "commercial_readiness_state": "",
                        "legal_readiness_state": "",
                        "download_readiness_state": "",
                    }
                ),
                encoding="utf-8",
            )
            operator = load_public_portal_operator_config(workspace)
            self.assertEqual(operator.support_contact, "operator input required")
            self.assertEqual(operator.support_email, "operator input required")
            self.assertEqual(operator.commercial_inquiry_label, "Commercial inquiry path")
            self.assertEqual(operator.package_tiers_state, "source not yet confirmed")
            self.assertEqual(operator.access_request_state, "approval_required")
            self.assertEqual(operator.legal_readiness_state, "configured")

    def test_filled_operator_fields_appear_in_snapshot_and_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            config_dir = workspace / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            (config_dir / "public-portal.json").write_text(
                json.dumps(
                    {
                        "bind_host": "127.0.0.1",
                        "port": 8781,
                        "selected_subdomain": "site-optimizer.electri-c-ity-studios-24-7.com",
                        "canonical_base_url": "https://site-optimizer.electri-c-ity-studios-24-7.com",
                        "product_name": "Electri City Site Optimizer",
                        "download_gate_state": "approval_required",
                        "public_routes": ["/", "/support", "/downloads", "/licensing"],
                        "protected_route_prefixes": ["/operator", "/downloads/private"],
                    }
                ),
                encoding="utf-8",
            )
            (config_dir / "public-portal-operator.json").write_text(
                json.dumps(
                    {
                        "support_contact": "Pierre Stephan",
                        "support_email": "support@example.invalid",
                        "commercial_inquiry_label": "Commercial inquiry contact",
                        "commercial_inquiry_state": "configured",
                        "pricing_model_state": "configured",
                        "package_tiers_state": "configured",
                        "access_request_state": "configured",
                        "support_readiness_state": "configured",
                        "commercial_readiness_state": "configured",
                        "legal_readiness_state": "configured",
                        "download_readiness_state": "configured",
                    }
                ),
                encoding="utf-8",
            )
            portal = load_public_portal_config(workspace)
            snapshot = build_public_portal_snapshot(workspace, self.config, portal)
            self.assertEqual(snapshot["operator_fields"]["support_contact"], "Pierre Stephan")
            self.assertEqual(snapshot["operator_fields"]["support_email"], "support@example.invalid")
            self.assertEqual(snapshot["operator_fields"]["legal_readiness_state"], "configured")
            body = resolve_portal_request("/support", workspace, self.config, portal).body.decode("utf-8")
            self.assertIn("Pierre Stephan", body)
            self.assertIn("support@example.invalid", body)
            self.assertIn("configured", body)

    def test_protected_route_is_blocked(self) -> None:
        response = resolve_portal_request("/operator", self.workspace_root, self.config, self.portal)
        self.assertEqual(response.status, 403)

    def test_private_download_route_is_blocked(self) -> None:
        response = resolve_portal_request("/downloads/private", self.workspace_root, self.config, self.portal)
        self.assertEqual(response.status, 403)

    def test_robots_txt_contains_sitemap_and_protected_disallow(self) -> None:
        content = render_robots_txt(self.portal)
        self.assertIn("Sitemap:", content)
        self.assertIn("/operator", content)
        self.assertIn("/downloads/private", content)

    def test_sitemap_contains_home_and_docs(self) -> None:
        xml = render_sitemap_xml(self.portal)
        self.assertIn("site-optimizer.electri-c-ity-studios-24-7.com/", xml)
        self.assertIn("/docs", xml)
        self.assertIn("/explore", xml)
        self.assertIn("/buy", xml)

    def test_health_payload_reports_local_upstream(self) -> None:
        payload = build_public_health_payload(self.workspace_root, self.config, self.portal)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["public_routes_only"])
        self.assertEqual(payload["landing_variant"], "seo_conversion_sales_platform_v3")


if __name__ == "__main__":
    unittest.main()
