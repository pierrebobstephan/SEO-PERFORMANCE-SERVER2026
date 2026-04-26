from __future__ import annotations

import base64
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
import json
from tempfile import TemporaryDirectory
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping

from electri_city_ops.config import AppConfig, load_config
from electri_city_ops.paypal_business import build_secret_reference_state, load_paypal_business_config


PROTECTED_PAYPAL_WEBHOOK_PATH = "/protected/paypal/webhook"
PAYPAL_WEBHOOK_EVIDENCE_FILENAME = "paypal_webhook_evidence.jsonl"
PAYPAL_WEBHOOK_NONCE_REGISTRY_FILENAME = "paypal_webhook_nonce_registry.json"
PAYPAL_WEBHOOK_TIME_WINDOW_SECONDS = 300
PAYPAL_WEBHOOK_REGISTRY_TTL_SECONDS = 86400
ALLOWED_BILLING_EVENT_TYPES = {
    "BILLING.SUBSCRIPTION.ACTIVATED",
    "BILLING.SUBSCRIPTION.CANCELLED",
    "BILLING.SUBSCRIPTION.EXPIRED",
    "BILLING.SUBSCRIPTION.PAYMENT.FAILED",
    "BILLING.SUBSCRIPTION.RE-ACTIVATED",
    "BILLING.SUBSCRIPTION.SUSPENDED",
    "INVOICING.INVOICE.CANCELLED",
    "INVOICING.INVOICE.PAID",
    "PAYMENT.CAPTURE.COMPLETED",
    "PAYMENT.CAPTURE.DENIED",
    "PAYMENT.CAPTURE.REFUNDED",
    "PAYMENT.SALE.COMPLETED",
    "PAYMENT.SALE.DENIED",
    "PAYMENT.SALE.REFUNDED",
}

HttpPost = Callable[[str, dict[str, str], bytes, int], tuple[int, dict[str, Any]]]


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _json_state_dir(workspace_root: Path, json_state_dir: Path | None = None) -> Path:
    return (json_state_dir or (workspace_root / "var" / "state" / "json")).resolve()


def _evidence_path(workspace_root: Path, json_state_dir: Path | None = None) -> Path:
    return _json_state_dir(workspace_root, json_state_dir) / PAYPAL_WEBHOOK_EVIDENCE_FILENAME


def _nonce_registry_path(workspace_root: Path, json_state_dir: Path | None = None) -> Path:
    return _json_state_dir(workspace_root, json_state_dir) / PAYPAL_WEBHOOK_NONCE_REGISTRY_FILENAME


def _build_missing_env_refs(secret_state: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    if not bool(secret_state.get("client_id_present", False)):
        missing.append(str(secret_state.get("client_id_env", "")).strip())
    if not bool(secret_state.get("client_secret_present", False)):
        missing.append(str(secret_state.get("client_secret_env", "")).strip())
    if not bool(secret_state.get("webhook_id_present", False)):
        missing.append(str(secret_state.get("webhook_id_env", "")).strip())
    return [item for item in missing if item]


def build_protected_paypal_webhook_runtime_state(
    workspace_root: Path,
    *,
    json_state_dir: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    paypal_config = load_paypal_business_config(workspace_root)
    secret_state = build_secret_reference_state(paypal_config, environ)
    missing_env_refs = _build_missing_env_refs(secret_state)
    state_dir = _json_state_dir(workspace_root, json_state_dir)
    return {
        "handler_path": PROTECTED_PAYPAL_WEBHOOK_PATH,
        "accepted_methods": ["POST"],
        "scope": "paypal_billing_events_only",
        "handler_state": "implemented_local_protected_only",
        "receiver_runtime_state": "implemented_but_unverified",
        "verification_runtime_state": "implemented",
        "replay_protection_runtime_state": "implemented",
        "env_ref_readiness_state": "ready" if not missing_env_refs else "missing_env_refs",
        "missing_env_refs": missing_env_refs,
        "activation_state": str(paypal_config.get("webhook_activation_state", "approval_required")).strip() or "approval_required",
        "route_exposed_via_public_portal": False,
        "event_routing_state": "protected_operator_server_governed_only",
        "evidence_log_path": str(_evidence_path(workspace_root, state_dir)),
        "nonce_registry_path": str(_nonce_registry_path(workspace_root, state_dir)),
        "verification_model": str(paypal_config.get("webhook_verification_model", "")).strip(),
        "replay_protection_expectation": str(paypal_config.get("webhook_replay_protection_expectation", "")).strip(),
    }


def run_local_paypal_webhook_runtime_self_test(
    workspace_root: Path,
    *,
    app_config: AppConfig | None = None,
) -> dict[str, Any]:
    workspace_root = workspace_root.resolve()
    config = app_config or load_config("config/settings.toml", workspace_root)[0]
    paypal_config = load_paypal_business_config(workspace_root)

    client_id_env = str(paypal_config.get("client_id_env", "")).strip()
    client_secret_env = str(paypal_config.get("client_secret_env", "")).strip()
    webhook_id_env = str(paypal_config.get("webhook_id_env", "")).strip()
    missing_env_names = [item for item in (client_id_env, client_secret_env, webhook_id_env) if not item]
    if missing_env_names:
        return {
            "state": "failed",
            "proof_mode": "local_synthetic_paypal_signature_and_replay_self_test",
            "issues": ["paypal business config is missing one or more env var names required for the local self-test"],
            "remaining_external_requirements": [
                "load real PayPal env refs on the protected server",
                "verify the protected receiver in the real staging server context",
                "approve webhook activation for real billing events",
            ],
        }

    env = {
        client_id_env: "local-self-test-client-id",
        client_secret_env: "local-self-test-client-secret",
        webhook_id_env: "local-self-test-webhook-id",
    }

    def fake_http_post(url: str, headers: dict[str, str], body: bytes, timeout: int) -> tuple[int, dict[str, Any]]:
        if url.endswith("/v1/oauth2/token"):
            return 200, {"access_token": "local-self-test-token"}
        if url.endswith("/verify-webhook-signature"):
            return 200, {"verification_status": "SUCCESS"}
        raise AssertionError(f"unexpected url {url}")

    headers = {
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-CERT-URL": "https://api-m.paypal.com/certs/local-self-test",
        "PAYPAL-TRANSMISSION-ID": "tx-local-self-test-001",
        "PAYPAL-TRANSMISSION-SIG": "local-self-test-signature",
        "PAYPAL-TRANSMISSION-TIME": "2026-04-03T10:00:00Z",
    }
    body = json.dumps(
        {
            "id": "evt-local-self-test-001",
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {"id": "sale-local-self-test-001"},
        }
    ).encode("utf-8")

    try:
        with TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            temp_config = replace(
                config,
                json_state_dir=(temp_root / "var" / "state" / "json"),
                logs_dir=(temp_root / "var" / "logs"),
                reports_dir=(temp_root / "var" / "reports"),
                database_path=(temp_root / "var" / "state" / "ops.sqlite3"),
            )
            first_status, first_payload = handle_protected_paypal_webhook(
                workspace_root,
                temp_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers=headers,
                body=body,
                environ=env,
                http_post=fake_http_post,
                now=datetime(2026, 4, 3, 10, 0, 0, tzinfo=UTC),
            )
            second_status, second_payload = handle_protected_paypal_webhook(
                workspace_root,
                temp_config,
                method="POST",
                path=PROTECTED_PAYPAL_WEBHOOK_PATH,
                headers=headers,
                body=body,
                environ=env,
                http_post=fake_http_post,
                now=datetime(2026, 4, 3, 10, 0, 10, tzinfo=UTC),
            )
            evidence_log_path = temp_config.json_state_dir / PAYPAL_WEBHOOK_EVIDENCE_FILENAME
            nonce_registry_path = temp_config.json_state_dir / PAYPAL_WEBHOOK_NONCE_REGISTRY_FILENAME
            evidence_log_written = evidence_log_path.exists()
            nonce_registry_written = nonce_registry_path.exists()
    except Exception as error:  # pragma: no cover - defensive fallback
        return {
            "state": "failed",
            "proof_mode": "local_synthetic_paypal_signature_and_replay_self_test",
            "issues": [f"local self-test raised an unexpected error: {error}"],
            "remaining_external_requirements": [
                "load real PayPal env refs on the protected server",
                "verify the protected receiver in the real staging server context",
                "approve webhook activation for real billing events",
            ],
        }

    issues: list[str] = []
    if first_status != 202:
        issues.append("first protected webhook delivery did not return HTTP 202")
    if first_payload.get("verification_state") != "verified":
        issues.append("first protected webhook delivery did not reach verified signature state")
    if first_payload.get("replay_state") != "clear":
        issues.append("first protected webhook delivery did not clear replay protection")
    if first_payload.get("routing_state") != "protected_operator_server_governed":
        issues.append("first protected webhook delivery did not reach protected operator routing")
    if second_status != 409:
        issues.append("second protected webhook delivery did not return HTTP 409 for replay protection")
    if second_payload.get("replay_state") != "replay_suspected":
        issues.append("second protected webhook delivery did not trigger replay protection")
    if not evidence_log_written:
        issues.append("local self-test did not write the evidence log")
    if not nonce_registry_written:
        issues.append("local self-test did not write the nonce registry")

    return {
        "state": "passed" if not issues else "failed",
        "proof_mode": "local_synthetic_paypal_signature_and_replay_self_test",
        "first_delivery": {
            "status_code": first_status,
            "verification_state": first_payload.get("verification_state", ""),
            "replay_state": first_payload.get("replay_state", ""),
            "routing_state": first_payload.get("routing_state", ""),
        },
        "second_delivery": {
            "status_code": second_status,
            "verification_state": second_payload.get("verification_state", ""),
            "replay_state": second_payload.get("replay_state", ""),
            "routing_state": second_payload.get("routing_state", ""),
        },
        "evidence_log_written": evidence_log_written,
        "nonce_registry_written": nonce_registry_written,
        "issues": issues,
        "remaining_external_requirements": [
            "load real PayPal env refs on the protected server",
            "verify the protected receiver in the real staging server context",
            "approve webhook activation for real billing events",
        ],
    }


def _append_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _load_nonce_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"entries": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"entries": []}
    if not isinstance(payload, dict):
        return {"entries": []}
    entries = payload.get("entries", [])
    return {"entries": entries if isinstance(entries, list) else []}


def _save_nonce_registry(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _header(headers: Mapping[str, str], name: str) -> str:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return str(value).strip()
    return ""


def _parse_datetime(value: str) -> datetime | None:
    candidate = value.strip()
    if not candidate:
        return None
    try:
        return datetime.fromisoformat(candidate.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(candidate).astimezone(UTC)
    except (TypeError, ValueError):
        return None


def _default_http_post(url: str, headers: dict[str, str], body: bytes, timeout: int) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        payload = json.loads(raw) if raw else {}
        return int(getattr(response, "status", 200)), payload


def _oauth_access_token(
    paypal_config: Mapping[str, Any],
    environ: Mapping[str, str],
    http_post: HttpPost,
) -> tuple[bool, str]:
    client_id_env = str(paypal_config.get("client_id_env", "")).strip()
    client_secret_env = str(paypal_config.get("client_secret_env", "")).strip()
    client_id = environ.get(client_id_env, "")
    client_secret = environ.get(client_secret_env, "")
    if not client_id or not client_secret:
        return False, ""

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    status, payload = http_post(
        str(paypal_config.get("oauth_token_url", "")).strip(),
        headers,
        b"grant_type=client_credentials",
        10,
    )
    if status >= 400:
        return False, ""
    access_token = str(payload.get("access_token", "")).strip()
    return bool(access_token), access_token


def verify_paypal_webhook_signature(
    paypal_config: Mapping[str, Any],
    headers: Mapping[str, str],
    event: Mapping[str, Any],
    *,
    environ: Mapping[str, str] | None = None,
    http_post: HttpPost | None = None,
) -> dict[str, Any]:
    env = environ or {}
    secret_state = build_secret_reference_state(dict(paypal_config), env)
    missing_env_refs = _build_missing_env_refs(secret_state)
    if missing_env_refs:
        return {
            "state": "missing_env_refs",
            "reason": "required PayPal env refs are missing for signature verification",
            "missing_env_refs": missing_env_refs,
        }

    auth_algo = _header(headers, "PAYPAL-AUTH-ALGO")
    cert_url = _header(headers, "PAYPAL-CERT-URL")
    transmission_id = _header(headers, "PAYPAL-TRANSMISSION-ID")
    transmission_sig = _header(headers, "PAYPAL-TRANSMISSION-SIG")
    transmission_time = _header(headers, "PAYPAL-TRANSMISSION-TIME")
    if not all((auth_algo, cert_url, transmission_id, transmission_sig, transmission_time)):
        return {
            "state": "malformed_event",
            "reason": "required PayPal transmission headers are missing",
            "missing_env_refs": [],
        }

    http_fn = http_post or _default_http_post
    token_ok, access_token = _oauth_access_token(paypal_config, env, http_fn)
    if not token_ok:
        return {
            "state": "invalid_signature",
            "reason": "PayPal access token exchange failed; signature verification cannot proceed",
            "missing_env_refs": [],
        }

    verification_payload = {
        "auth_algo": auth_algo,
        "cert_url": cert_url,
        "transmission_id": transmission_id,
        "transmission_sig": transmission_sig,
        "transmission_time": transmission_time,
        "webhook_id": env.get(str(paypal_config.get("webhook_id_env", "")).strip(), ""),
        "webhook_event": event,
    }
    request_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    try:
        status, payload = http_fn(
            str(paypal_config.get("webhook_verify_url", "")).strip(),
            request_headers,
            json.dumps(verification_payload).encode("utf-8"),
            10,
        )
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return {
            "state": "invalid_signature",
            "reason": "PayPal signature verification request failed; failing closed",
            "missing_env_refs": [],
        }

    verification_status = str(payload.get("verification_status", "")).strip().upper()
    if status < 400 and verification_status == "SUCCESS":
        return {
            "state": "verified",
            "reason": "PayPal signature verification succeeded",
            "missing_env_refs": [],
        }
    return {
        "state": "invalid_signature",
        "reason": "PayPal signature verification did not return SUCCESS",
        "missing_env_refs": [],
    }


def _assess_replay(
    workspace_root: Path,
    headers: Mapping[str, str],
    event: Mapping[str, Any],
    *,
    json_state_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = (now or _now_utc()).astimezone(UTC)
    transmission_id = _header(headers, "PAYPAL-TRANSMISSION-ID")
    transmission_time_raw = _header(headers, "PAYPAL-TRANSMISSION-TIME")
    event_id = str(event.get("id", "")).strip()
    transmission_time = _parse_datetime(transmission_time_raw)
    if not transmission_id or not event_id or transmission_time is None:
        return {
            "state": "malformed_event",
            "reason": "transmission id, transmission time or event id is missing",
        }

    age = abs((current_time - transmission_time).total_seconds())
    if age > PAYPAL_WEBHOOK_TIME_WINDOW_SECONDS:
        return {
            "state": "replay_suspected",
            "reason": "transmission time is outside the accepted replay window",
        }

    registry_path = _nonce_registry_path(workspace_root, json_state_dir)
    registry = _load_nonce_registry(registry_path)
    cutoff = current_time - timedelta(seconds=PAYPAL_WEBHOOK_REGISTRY_TTL_SECONDS)
    pruned_entries = [
        entry
        for entry in registry.get("entries", [])
        if _parse_datetime(str(entry.get("recorded_at", ""))) and _parse_datetime(str(entry.get("recorded_at", ""))) >= cutoff
    ]
    nonce_key = f"{transmission_id}:{event_id}"
    if any(str(entry.get("nonce_key", "")) == nonce_key for entry in pruned_entries):
        registry["entries"] = pruned_entries
        _save_nonce_registry(registry_path, registry)
        return {
            "state": "replay_suspected",
            "reason": "transmission id and event id were already recorded in the nonce registry",
        }

    pruned_entries.append(
        {
            "nonce_key": nonce_key,
            "transmission_id": transmission_id,
            "event_id": event_id,
            "recorded_at": current_time.isoformat(),
        }
    )
    registry["entries"] = pruned_entries
    _save_nonce_registry(registry_path, registry)
    return {
        "state": "clear",
        "reason": "transmission id and event id are within the accepted replay window and not yet recorded",
    }


def handle_protected_paypal_webhook(
    workspace_root: Path,
    app_config: AppConfig,
    *,
    method: str,
    path: str,
    headers: Mapping[str, str],
    body: bytes,
    environ: Mapping[str, str] | None = None,
    http_post: HttpPost | None = None,
    now: datetime | None = None,
) -> tuple[int, dict[str, Any]]:
    paypal_config = load_paypal_business_config(workspace_root)
    runtime_state = build_protected_paypal_webhook_runtime_state(
        workspace_root,
        json_state_dir=app_config.json_state_dir,
        environ=environ,
    )
    received_at = (now or _now_utc()).astimezone(UTC).isoformat()
    evidence_base = {
        "received_at": received_at,
        "path": path,
        "handler_path": PROTECTED_PAYPAL_WEBHOOK_PATH,
        "doctrine_state": "approval_required",
        "receiver_runtime_state": runtime_state["receiver_runtime_state"],
        "handler_state": runtime_state["handler_state"],
    }

    if path != PROTECTED_PAYPAL_WEBHOOK_PATH:
        payload = {
            **evidence_base,
            "event_type": "",
            "verification_state": "malformed_event",
            "replay_state": "not_assessed",
            "routing_state": "rejected_path_mismatch",
            "status": "blocked",
            "reason": "path does not match the protected PayPal webhook receiver",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 404, payload

    if method.upper() != "POST":
        payload = {
            **evidence_base,
            "event_type": "",
            "verification_state": "malformed_event",
            "replay_state": "not_assessed",
            "routing_state": "rejected_method_not_allowed",
            "status": "blocked",
            "reason": "protected PayPal webhook receiver accepts POST only",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 405, payload

    try:
        event = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        payload = {
            **evidence_base,
            "event_type": "",
            "verification_state": "malformed_event",
            "replay_state": "not_assessed",
            "routing_state": "rejected_malformed_event",
            "status": "blocked",
            "reason": "request body is not valid JSON",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 400, payload

    if not isinstance(event, dict):
        payload = {
            **evidence_base,
            "event_type": "",
            "verification_state": "malformed_event",
            "replay_state": "not_assessed",
            "routing_state": "rejected_malformed_event",
            "status": "blocked",
            "reason": "request body must decode into an event object",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 400, payload

    event_type = str(event.get("event_type", "")).strip()
    if not event_type or "resource" not in event or str(event.get("id", "")).strip() == "":
        payload = {
            **evidence_base,
            "event_type": event_type,
            "verification_state": "malformed_event",
            "replay_state": "not_assessed",
            "routing_state": "rejected_malformed_event",
            "status": "blocked",
            "reason": "event is missing id, event_type or resource",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 400, payload

    if event_type not in ALLOWED_BILLING_EVENT_TYPES:
        payload = {
            **evidence_base,
            "event_type": event_type,
            "verification_state": "not_attempted",
            "replay_state": "not_assessed",
            "routing_state": "rejected_unsupported_event_scope",
            "status": "blocked",
            "reason": "event type is outside paypal_billing_events_only",
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 422, payload

    verification = verify_paypal_webhook_signature(
        paypal_config,
        headers,
        event,
        environ=environ,
        http_post=http_post,
    )
    if verification["state"] != "verified":
        payload = {
            **evidence_base,
            "event_type": event_type,
            "verification_state": verification["state"],
            "missing_env_refs": verification.get("missing_env_refs", []),
            "replay_state": "not_assessed",
            "routing_state": "rejected_signature_verification",
            "status": "blocked",
            "reason": verification["reason"],
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        status = 503 if verification["state"] == "missing_env_refs" else (400 if verification["state"] == "malformed_event" else 403)
        return status, payload

    replay = _assess_replay(
        workspace_root,
        headers,
        event,
        json_state_dir=app_config.json_state_dir,
        now=now,
    )
    if replay["state"] != "clear":
        payload = {
            **evidence_base,
            "event_type": event_type,
            "verification_state": "verified",
            "replay_state": replay["state"],
            "routing_state": "rejected_replay_protection",
            "status": "blocked",
            "reason": replay["reason"],
        }
        _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
        return 409 if replay["state"] == "replay_suspected" else 400, payload

    payload = {
        **evidence_base,
        "event_type": event_type,
        "verification_state": "verified",
        "replay_state": "clear",
        "routing_state": "protected_operator_server_governed",
        "status": "approval_required",
        "reason": "event was verified and logged into the protected staging-only routing layer",
    }
    _append_evidence(_evidence_path(workspace_root, app_config.json_state_dir), payload)
    return 202, payload
