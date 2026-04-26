from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from electri_city_ops.config import load_config
from electri_city_ops.paypal_webhook_runtime import (
    PROTECTED_PAYPAL_WEBHOOK_PATH,
    build_protected_paypal_webhook_runtime_state,
    handle_protected_paypal_webhook,
    run_local_paypal_webhook_runtime_self_test,
)


class PayPalWebhookRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace_root = Path(".").resolve()
        self.app_config, _ = load_config("config/settings.toml", self.workspace_root)

    def _runtime_config(self, temp_root: Path):
        return replace(
            self.app_config,
            json_state_dir=(temp_root / "var" / "state" / "json"),
            logs_dir=(temp_root / "var" / "logs"),
            reports_dir=(temp_root / "var" / "reports"),
            database_path=(temp_root / "var" / "state" / "ops.sqlite3"),
        )

    def test_runtime_state_is_implemented_but_unverified(self) -> None:
        state = build_protected_paypal_webhook_runtime_state(self.workspace_root, environ={})
        self.assertEqual(state["handler_path"], PROTECTED_PAYPAL_WEBHOOK_PATH)
        self.assertEqual(state["handler_state"], "implemented_local_protected_only")
        self.assertEqual(state["receiver_runtime_state"], "implemented_but_unverified")
        self.assertEqual(state["verification_runtime_state"], "implemented")
        self.assertEqual(state["replay_protection_runtime_state"], "implemented")
        self.assertEqual(state["env_ref_readiness_state"], "missing_env_refs")
        self.assertEqual(state["activation_state"], "approval_required")

    def test_handler_fails_closed_when_env_refs_are_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_config = self._runtime_config(Path(tmp))
            status, payload = handle_protected_paypal_webhook(
                self.workspace_root,
                runtime_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers={
                    "PAYPAL-AUTH-ALGO": "SHA256withRSA",
                    "PAYPAL-CERT-URL": "https://api-m.paypal.com/certs/example",
                    "PAYPAL-TRANSMISSION-ID": "tx-001",
                    "PAYPAL-TRANSMISSION-SIG": "signature",
                    "PAYPAL-TRANSMISSION-TIME": "2026-04-03T10:00:00Z",
                },
                body=json.dumps(
                    {
                        "id": "evt-001",
                        "event_type": "PAYMENT.SALE.COMPLETED",
                        "resource": {"id": "sale-001"},
                    }
                ).encode("utf-8"),
                environ={},
                now=datetime(2026, 4, 3, 10, 0, 0, tzinfo=UTC),
            )
            self.assertEqual(status, 503)
            self.assertEqual(payload["verification_state"], "missing_env_refs")
            self.assertEqual(payload["routing_state"], "rejected_signature_verification")
            evidence_path = runtime_config.json_state_dir / "paypal_webhook_evidence.jsonl"
            self.assertTrue(evidence_path.exists())
            lines = evidence_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertTrue(lines)

    def test_handler_rejects_unsupported_scope(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_config = self._runtime_config(Path(tmp))
            status, payload = handle_protected_paypal_webhook(
                self.workspace_root,
                runtime_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers={},
                body=json.dumps(
                    {
                        "id": "evt-unsupported",
                        "event_type": "CHECKOUT.ORDER.APPROVED",
                        "resource": {"id": "order-001"},
                    }
                ).encode("utf-8"),
                environ={},
            )
            self.assertEqual(status, 422)
            self.assertEqual(payload["routing_state"], "rejected_unsupported_event_scope")
            self.assertEqual(payload["verification_state"], "not_attempted")

    def test_handler_records_path_mismatch_in_evidence_log(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_config = self._runtime_config(Path(tmp))
            status, payload = handle_protected_paypal_webhook(
                self.workspace_root,
                runtime_config,
                method="POST",
                path="/protected/paypal/not-the-webhook",
                headers={},
                body=b"{}",
                environ={},
            )
            self.assertEqual(status, 404)
            self.assertEqual(payload["routing_state"], "rejected_path_mismatch")
            evidence_path = runtime_config.json_state_dir / "paypal_webhook_evidence.jsonl"
            self.assertTrue(evidence_path.exists())
            lines = evidence_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertTrue(lines)
            self.assertEqual(json.loads(lines[-1])["routing_state"], "rejected_path_mismatch")

    def test_handler_detects_replay_after_verified_event(self) -> None:
        def fake_http_post(url: str, headers: dict[str, str], body: bytes, timeout: int):
            if url.endswith("/v1/oauth2/token"):
                return 200, {"access_token": "token-123"}
            if url.endswith("/verify-webhook-signature"):
                return 200, {"verification_status": "SUCCESS"}
            raise AssertionError(f"unexpected url {url}")

        event_headers = {
            "PAYPAL-AUTH-ALGO": "SHA256withRSA",
            "PAYPAL-CERT-URL": "https://api-m.paypal.com/certs/example",
            "PAYPAL-TRANSMISSION-ID": "tx-verified-001",
            "PAYPAL-TRANSMISSION-SIG": "signature",
            "PAYPAL-TRANSMISSION-TIME": "2026-04-03T10:00:00Z",
        }
        event_body = json.dumps(
            {
                "id": "evt-verified-001",
                "event_type": "PAYMENT.SALE.COMPLETED",
                "resource": {"id": "sale-verified-001"},
            }
        ).encode("utf-8")
        env = {
            "PAYPAL_BUSINESS_CLIENT_ID": "client-id",
            "PAYPAL_BUSINESS_CLIENT_SECRET": "client-secret",
            "PAYPAL_BUSINESS_WEBHOOK_ID": "webhook-id",
        }

        with TemporaryDirectory() as tmp:
            runtime_config = self._runtime_config(Path(tmp))
            first_status, first_payload = handle_protected_paypal_webhook(
                self.workspace_root,
                runtime_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers=event_headers,
                body=event_body,
                environ=env,
                http_post=fake_http_post,
                now=datetime(2026, 4, 3, 10, 0, 0, tzinfo=UTC),
            )
            second_status, second_payload = handle_protected_paypal_webhook(
                self.workspace_root,
                runtime_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers=event_headers,
                body=event_body,
                environ=env,
                http_post=fake_http_post,
                now=datetime(2026, 4, 3, 10, 0, 10, tzinfo=UTC),
            )

            self.assertEqual(first_status, 202)
            self.assertEqual(first_payload["verification_state"], "verified")
            self.assertEqual(first_payload["replay_state"], "clear")
            self.assertEqual(first_payload["routing_state"], "protected_operator_server_governed")
            self.assertEqual(second_status, 409)
            self.assertEqual(second_payload["replay_state"], "replay_suspected")
            nonce_registry_path = runtime_config.json_state_dir / "paypal_webhook_nonce_registry.json"
            self.assertTrue(nonce_registry_path.exists())

    def test_local_runtime_self_test_passes(self) -> None:
        result = run_local_paypal_webhook_runtime_self_test(self.workspace_root, app_config=self.app_config)
        self.assertEqual(result["state"], "passed")
        self.assertEqual(result["proof_mode"], "local_synthetic_paypal_signature_and_replay_self_test")
        self.assertEqual(result["first_delivery"]["status_code"], 202)
        self.assertEqual(result["first_delivery"]["verification_state"], "verified")
        self.assertEqual(result["first_delivery"]["replay_state"], "clear")
        self.assertEqual(result["second_delivery"]["status_code"], 409)
        self.assertEqual(result["second_delivery"]["replay_state"], "replay_suspected")
        self.assertTrue(result["evidence_log_written"])
        self.assertTrue(result["nonce_registry_written"])
        self.assertEqual(result["issues"], [])


if __name__ == "__main__":
    unittest.main()
