from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib

from electri_city_ops.workspace import WorkspaceGuard


ALLOWED_MODES = {"observe_only", "plan_only", "active_internal"}


@dataclass(slots=True)
class EmailNotificationConfig:
    enabled: bool
    sender: str
    recipients: tuple[str, ...]
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    starttls: bool

    def is_complete(self) -> bool:
        return bool(
            self.sender
            and self.recipients
            and self.smtp_host
            and self.smtp_port
            and self.smtp_username
            and self.smtp_password
        )


@dataclass(slots=True)
class AppConfig:
    workspace_root: Path
    config_path: Path
    mode: str
    timezone: str
    database_path: Path
    json_state_dir: Path
    reports_dir: Path
    logs_dir: Path
    cycle_interval_minutes: int
    domains: tuple[str, ...]
    user_agent: str
    request_timeout_seconds: int
    max_response_bytes: int
    allow_remote_fetch: bool
    allow_external_changes: bool
    allow_workspace_self_healing: bool
    warning_response_ms: int
    critical_response_ms: int
    large_html_bytes: int
    report_formats: tuple[str, ...]
    email: EmailNotificationConfig


def _section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def load_config(config_path: str | Path, workspace_root: str | Path | None = None) -> tuple[AppConfig, list[str]]:
    config_file = Path(config_path).resolve()
    root = Path(workspace_root).resolve() if workspace_root else config_file.parent.parent.resolve()
    guard = WorkspaceGuard(root)
    raw = tomllib.loads(config_file.read_text(encoding="utf-8"))

    notes: list[str] = []
    system = _section(raw, "system")
    storage = _section(raw, "storage")
    schedule = _section(raw, "schedule")
    targets = _section(raw, "targets")
    permissions = _section(raw, "permissions")
    thresholds = _section(raw, "thresholds")
    reports = _section(raw, "reports")
    notifications = _section(raw, "notifications")
    email_raw = _section(notifications, "email")

    mode = str(system.get("mode", "observe_only")).strip() or "observe_only"
    if mode not in ALLOWED_MODES:
        notes.append(f"Unknown mode '{mode}' detected. Falling back to observe_only.")
        mode = "observe_only"

    database_path = guard.resolve_inside(storage.get("database", "var/state/ops.sqlite3"))
    json_state_dir = guard.resolve_inside(storage.get("json_state_dir", "var/state/json"))
    reports_dir = guard.resolve_inside(storage.get("reports_dir", "var/reports"))
    logs_dir = guard.resolve_inside(storage.get("logs_dir", "var/logs"))

    domains = tuple(
        normalized
        for item in targets.get("domains", [])
        if isinstance(item, str)
        if (normalized := item.strip())
    )

    report_formats = tuple(
        item
        for item in reports.get("formats", ["json", "markdown"])
        if isinstance(item, str) and item in {"json", "markdown"}
    )
    if not report_formats:
        notes.append("No valid report format configured. Falling back to json + markdown.")
        report_formats = ("json", "markdown")

    email = EmailNotificationConfig(
        enabled=bool(email_raw.get("enabled", False)),
        sender=str(email_raw.get("sender", "")).strip(),
        recipients=tuple(
            item.strip()
            for item in email_raw.get("recipients", [])
            if isinstance(item, str) and item.strip()
        ),
        smtp_host=str(email_raw.get("smtp_host", "")).strip(),
        smtp_port=int(email_raw.get("smtp_port", 587)),
        smtp_username=str(email_raw.get("smtp_username", "")).strip(),
        smtp_password=str(email_raw.get("smtp_password", "")).strip(),
        starttls=bool(email_raw.get("starttls", True)),
    )

    config = AppConfig(
        workspace_root=root,
        config_path=config_file,
        mode=mode,
        timezone=str(system.get("timezone", "UTC")).strip() or "UTC",
        database_path=database_path,
        json_state_dir=json_state_dir,
        reports_dir=reports_dir,
        logs_dir=logs_dir,
        cycle_interval_minutes=max(1, int(schedule.get("cycle_interval_minutes", 60))),
        domains=domains,
        user_agent=str(targets.get("user_agent", "ElectriCityOps/0.1")).strip() or "ElectriCityOps/0.1",
        request_timeout_seconds=max(1, int(targets.get("request_timeout_seconds", 10))),
        max_response_bytes=max(1024, int(targets.get("max_response_bytes", 1048576))),
        allow_remote_fetch=bool(permissions.get("allow_remote_fetch", False)),
        allow_external_changes=bool(permissions.get("allow_external_changes", False)),
        allow_workspace_self_healing=bool(permissions.get("allow_workspace_self_healing", True)),
        warning_response_ms=max(100, int(thresholds.get("warning_response_ms", 1200))),
        critical_response_ms=max(100, int(thresholds.get("critical_response_ms", 3000))),
        large_html_bytes=max(4096, int(thresholds.get("large_html_bytes", 250000))),
        report_formats=report_formats,
        email=email,
    )

    if config.allow_external_changes:
        notes.append("External changes are enabled in config, but the current MVP never applies them automatically.")
    if config.email.enabled and not config.email.is_complete():
        notes.append("Email notifications are enabled but SMTP details are incomplete.")
    if not config.domains:
        notes.append("No target domains configured. SEO and performance checks stay partial.")

    return config, notes

