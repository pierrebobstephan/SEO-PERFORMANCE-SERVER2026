from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
from typing import Any

from electri_city_ops.config import load_config
from electri_city_ops.public_portal import (
    build_public_health_payload,
    load_public_portal_config,
    resolve_portal_request,
)


def backup_policy_path(workspace_root: Path) -> Path:
    return workspace_root.resolve() / "config" / "backup-policy.json"


def load_backup_policy(workspace_root: Path) -> dict[str, Any]:
    return json.loads(backup_policy_path(workspace_root).read_text(encoding="utf-8"))


def _path_entry(path: Path) -> dict[str, Any]:
    exists = path.exists()
    entry = {
        "path": str(path),
        "exists": exists,
        "kind": "missing",
    }
    if exists:
        if path.is_dir():
            entry["kind"] = "directory"
            entry["children"] = sum(1 for _ in path.iterdir())
        else:
            entry["kind"] = "file"
            entry["size_bytes"] = path.stat().st_size
    return entry


def collect_backup_inventory(workspace_root: Path, config_path: str | Path = "config/settings.toml") -> dict[str, Any]:
    config, _ = load_config(config_path, workspace_root)
    policy = load_backup_policy(workspace_root)
    backup_sets: list[dict[str, Any]] = []
    for item in policy.get("backup_sets", []):
        entries = [_path_entry(workspace_root / rel_path) for rel_path in item.get("paths", [])]
        backup_sets.append(
            {
                "name": item["name"],
                "required": bool(item.get("required", False)),
                "all_present": all(entry["exists"] for entry in entries),
                "entries": entries,
            }
        )
    return {
        "workspace_root": str(workspace_root.resolve()),
        "mode": policy.get("mode", "local_preview_only"),
        "database_path": str(config.database_path),
        "public_portal_config_present": (workspace_root / "config" / "public-portal.json").exists(),
        "backup_sets": backup_sets,
        "separate_sensitive_material": policy.get("separate_sensitive_material", {}),
        "migration_notes": policy.get("migration_notes", []),
    }


def post_restore_validation(
    workspace_root: Path,
    config_path: str | Path = "config/settings.toml",
    *,
    run_tests: bool = False,
) -> dict[str, Any]:
    config, _ = load_config(config_path, workspace_root)
    portal = load_public_portal_config(workspace_root)
    policy = load_backup_policy(workspace_root)
    public_checks = []
    for route in policy.get("restore_validation", {}).get("public_routes", []):
        response = resolve_portal_request(route, workspace_root, config, portal)
        public_checks.append({"route": route, "status": response.status, "ok": response.status == 200})
    protected_checks = []
    for route in policy.get("restore_validation", {}).get("protected_routes", []):
        response = resolve_portal_request(route, workspace_root, config, portal)
        protected_checks.append({"route": route, "status": response.status, "ok": response.status == 403})
    test_result: dict[str, Any] = {"run_tests": run_tests, "status": "not_run"}
    if run_tests:
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=workspace_root,
            env={**os.environ, "PYTHONPATH": "src"},
            capture_output=True,
            text=True,
            check=False,
        )
        test_result = {
            "run_tests": True,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
        }
    return {
        "workspace_root": str(workspace_root.resolve()),
        "config_loaded": True,
        "portal_loaded": True,
        "database_exists": config.database_path.exists(),
        "health_payload": build_public_health_payload(workspace_root, config, portal),
        "public_checks": public_checks,
        "protected_checks": protected_checks,
        "test_suite": test_result,
    }


def migration_preflight(workspace_root: Path, config_path: str | Path = "config/settings.toml") -> dict[str, Any]:
    inventory = collect_backup_inventory(workspace_root, config_path)
    missing_required = [
        backup_set["name"]
        for backup_set in inventory["backup_sets"]
        if backup_set["required"] and not backup_set["all_present"]
    ]
    return {
        "workspace_root": inventory["workspace_root"],
        "mode": inventory["mode"],
        "all_required_backup_sets_present": not missing_required,
        "missing_required_backup_sets": missing_required,
        "external_input_required": [
            "target_server_hostname_or_ip",
            "dns_cutover_plan",
            "certificate_export_and_restore_plan",
            "secret_transfer_plan",
            "final_service_reload_window",
        ],
        "approval_required_operations": [
            "real Hetzner snapshot creation",
            "real server restore",
            "real migration to a new Hetzner server",
            "DNS or TLS cutover",
            "public service reload outside the workspace",
        ],
        "next_validation_steps": [
            "validate-config",
            "public portal healthcheck",
            "legal route rendering",
            "protected route blocking",
            "full test suite",
        ],
    }
