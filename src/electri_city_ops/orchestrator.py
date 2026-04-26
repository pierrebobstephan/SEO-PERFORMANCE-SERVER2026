from __future__ import annotations

import json
import logging
from pathlib import Path
from time import sleep
from uuid import uuid4

from electri_city_ops.analyzers import (
    collect_target_snapshots,
    run_audit_analysis,
    run_error_analysis,
    run_performance_analysis,
    run_seo_analysis,
)
from electri_city_ops.applier import apply_actions
from electri_city_ops.config import AppConfig, load_config
from electri_city_ops.decision import prioritize_findings
from electri_city_ops.doctrine import enforce_runtime_guardrails
from electri_city_ops.http_probe import HttpProbe
from electri_city_ops.learning import build_learning_notes
from electri_city_ops.logging_utils import configure_logging
from electri_city_ops.models import CycleResult, utc_now
from electri_city_ops.notifier import send_email_summary
from electri_city_ops.planner import plan_actions
from electri_city_ops.reporting import write_reports
from electri_city_ops.storage import Storage
from electri_city_ops.validator import validate_cycle
from electri_city_ops.workspace import WorkspaceGuard


def _build_summary(result: CycleResult, config: AppConfig) -> dict[str, object]:
    severities = {"critical": 0, "high": 0, "warning": 0, "info": 0}
    for finding in result.findings:
        severities[finding.severity] = severities.get(finding.severity, 0) + 1

    action_counts: dict[str, int] = {}
    for action in result.actions:
        action_counts[action.status] = action_counts.get(action.status, 0) + 1

    successful_target_probes = sum(
        1 for item in result.target_results if not item.fetch_error and 200 <= item.homepage_status_code < 400
    )

    return {
        "mode": config.mode,
        "configured_domains": len(config.domains),
        "domain_results": len(result.target_results),
        "successful_target_probes": successful_target_probes,
        "critical_findings": severities.get("critical", 0),
        "high_findings": severities.get("high", 0),
        "warning_findings": severities.get("warning", 0),
        "info_findings": severities.get("info", 0),
        "total_findings": len(result.findings),
        "total_metrics": len(result.metrics),
        "total_actions": len(result.actions),
        "action_status_counts": action_counts,
    }


def run_cycle(config_path: str | Path, workspace_root: str | Path | None = None) -> CycleResult:
    config, config_notes = load_config(config_path, workspace_root)
    guard = WorkspaceGuard(config.workspace_root)
    workspace_paths, bootstrap_actions = guard.ensure_layout(
        database=config.database_path,
        json_state_dir=config.json_state_dir,
        reports_dir=config.reports_dir,
        logs_dir=config.logs_dir,
        allow_create_dirs=config.allow_workspace_self_healing,
    )

    logger = configure_logging(workspace_paths.logs_dir)
    logger.info("starting cycle in mode=%s", config.mode)

    storage = Storage(workspace_paths.database)
    storage.initialize()
    recurrence = storage.recurrence_map(days=30)

    started_at = utc_now().isoformat()
    run_id = f"{utc_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"

    probe = None
    if config.allow_remote_fetch and config.domains:
        probe = HttpProbe(
            user_agent=config.user_agent,
            timeout_seconds=config.request_timeout_seconds,
            max_response_bytes=config.max_response_bytes,
        )

    audit_findings, audit_metrics = run_audit_analysis(config, config_notes)
    target_results, target_findings, target_metrics = collect_target_snapshots(config, probe)
    seo_findings, seo_metrics = run_seo_analysis(target_results)
    perf_findings, perf_metrics = run_performance_analysis(config, target_results)
    error_findings, error_metrics = run_error_analysis(
        config,
        target_results,
        target_findings + seo_findings + perf_findings,
    )

    findings = prioritize_findings(
        audit_findings + target_findings + seo_findings + perf_findings + error_findings,
        recurrence_map=recurrence,
    )
    metrics = audit_metrics + target_metrics + seo_metrics + perf_metrics + error_metrics

    planned_actions = plan_actions(config, findings)
    applied_actions = bootstrap_actions + apply_actions(config, planned_actions)
    _, applied_actions, doctrine_validations = enforce_runtime_guardrails(
        workspace_root=config.workspace_root,
        mode=config.mode,
        allow_external_changes=config.allow_external_changes,
        email_enabled=config.email.enabled,
        actions=applied_actions,
    )

    result = CycleResult(
        run_id=run_id,
        started_at=started_at,
        finished_at=utc_now().isoformat(),
        mode=config.mode,
        status="running",
        target_results=target_results,
        findings=findings,
        metrics=metrics,
        actions=applied_actions,
    )
    result.summary = _build_summary(result, config)
    storage.upsert_cycle(result)

    result.learning_notes = build_learning_notes(storage, result)
    result.summary = _build_summary(result, config)
    storage.upsert_cycle(result)

    json_state_path, latest_json_path, latest_markdown_path = write_reports(
        reports_dir=workspace_paths.reports_dir,
        json_state_dir=workspace_paths.json_state_dir,
        result=result,
        storage=storage,
        formats=config.report_formats,
    )

    validations = doctrine_validations + validate_cycle(
        config=config,
        database_path=workspace_paths.database,
        json_state_path=json_state_path,
        latest_json_path=latest_json_path,
        latest_markdown_path=latest_markdown_path,
    )
    result.validations = validations
    result.status = "validated" if all(check.success for check in validations) else "degraded"
    result.finished_at = utc_now().isoformat()
    result.summary = _build_summary(result, config)
    storage.upsert_cycle(result)
    write_reports(
        reports_dir=workspace_paths.reports_dir,
        json_state_dir=workspace_paths.json_state_dir,
        result=result,
        storage=storage,
        formats=config.report_formats,
    )

    if config.email.enabled:
        try:
            send_email_summary(
                config.email,
                subject=f"[Electri City Ops] {result.status} {result.run_id}",
                body=json.dumps(result.summary, indent=2, sort_keys=True),
                logger=logger,
            )
        except Exception as error:  # pragma: no cover - defensive logging branch
            logger.exception("email notification failed: %s", error)

    logger.info("cycle finished with status=%s", result.status)
    return result


def run_loop(config_path: str | Path, workspace_root: str | Path | None = None) -> int:
    config, _ = load_config(config_path, workspace_root)
    logger = logging.getLogger("electri_city_ops")
    if not logger.handlers:
        logger = configure_logging(config.logs_dir)

    try:
        while True:
            run_cycle(config_path, workspace_root)
            sleep(config.cycle_interval_minutes * 60)
    except KeyboardInterrupt:
        logger.info("run loop interrupted by operator")
        return 130
