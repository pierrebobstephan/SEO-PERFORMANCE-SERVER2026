from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from electri_city_ops.models import CycleResult
from electri_city_ops.storage import Storage


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _display(value: str) -> str:
    return value if value else "(not present)"


def _render_target_results_markdown(result: CycleResult) -> list[str]:
    lines = ["## Domain Results", ""]
    if not result.target_results:
        lines.append("- No domain results recorded in this cycle.")
        return lines

    for snapshot in result.target_results:
        lines.extend(
            [
                f"### {snapshot.domain}",
                "",
                f"- Final URL: `{_display(snapshot.final_url)}`",
                f"- HTTP status code: `{snapshot.homepage_status_code}`",
                f"- Response time: `{snapshot.response_ms} ms`",
                f"- HTML size: `{snapshot.html_bytes} bytes`",
                f"- Content-Encoding: `{_display(snapshot.content_encoding)}`",
                f"- Cache-Control: `{_display(snapshot.cache_control)}`",
                f"- Title: `{_display(snapshot.title)}`",
                f"- Meta Description: `{_display(snapshot.meta_description)}`",
                f"- Canonical: `{_display(snapshot.canonical)}`",
                f"- H1 count: `{snapshot.h1_count}`",
                f"- HTML lang: `{_display(snapshot.html_lang)}`",
                f"- Viewport present: `{snapshot.viewport_present}`",
                f"- Robots meta: `{_display(snapshot.robots_meta)}`",
                f"- Sitemap status code: `{snapshot.sitemap_status_code}`",
            ]
        )
        if snapshot.fetch_error:
            lines.append(f"- Fetch error: `{snapshot.fetch_error}`")
        lines.append("")
    return lines


def _render_markdown(result: CycleResult) -> str:
    lines = [
        "# Electri City Ops Report",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Status: `{result.status}`",
        f"- Mode: `{result.mode}`",
        f"- Started: `{result.started_at}`",
        f"- Finished: `{result.finished_at}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in sorted(result.summary.items()):
        lines.append(f"- {key}: `{value}`")

    lines.extend([""] + _render_target_results_markdown(result) + [""])

    lines.extend(["", "## Findings", ""])
    if result.findings:
        for finding in result.findings[:15]:
            lines.append(
                f"- [{finding.severity}] {finding.title} ({finding.target}) score={finding.priority_score:.0f}"
            )
            lines.append(f"  detail: {finding.detail}")
            lines.append(f"  recommendation: {finding.recommendation}")
    else:
        lines.append("- No findings recorded.")

    lines.extend(["", "## Actions", ""])
    if result.actions:
        for action in result.actions[:15]:
            lines.append(f"- [{action.status}] {action.description} ({action.target})")
    else:
        lines.append("- No actions recorded.")

    lines.extend(["", "## Learning", ""])
    if result.learning_notes:
        for note in result.learning_notes:
            lines.append(f"- {note.title}: {note.detail}")
    else:
        lines.append("- No learning notes recorded.")

    return "\n".join(lines) + "\n"


def _render_rollup_markdown(rollup: dict[str, Any]) -> str:
    lines = [
        f"# Rollup {rollup['days']}d",
        "",
        f"- Generated: `{rollup['generated_at']}`",
        f"- Runs: `{rollup['run_count']}`",
        "",
        "## Status counts",
        "",
    ]
    if rollup["status_counts"]:
        for key, value in sorted(rollup["status_counts"].items()):
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- No runs in this window.")

    lines.extend(["", "## Findings", ""])
    if rollup["finding_counts"]:
        for key, value in sorted(rollup["finding_counts"].items()):
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- No findings in this window.")

    lines.extend(["", "## Top recurring findings", ""])
    if rollup["top_recurring_findings"]:
        for item in rollup["top_recurring_findings"][:10]:
            lines.append(f"- {item['title']}: `{item['count']}`")
    else:
        lines.append("- No recurring findings in this window.")

    lines.extend(["", "## Domain trends", ""])
    if rollup.get("domain_trends"):
        for domain, trend_map in sorted(rollup["domain_trends"].items()):
            lines.append(f"### {domain}")
            lines.append("")
            for metric_name, trend in sorted(trend_map.items()):
                lines.append(
                    f"- {metric_name}: `{trend['direction']}` latest=`{trend['latest']}` "
                    f"previous=`{trend['previous']}` delta=`{trend['delta']}` samples=`{trend['samples']}`"
                )
            lines.append("")
    else:
        lines.append("- No domain trend data in this window.")

    legacy_runs = rollup.get("legacy_observe_only_runs_without_targets", 0)
    if legacy_runs:
        lines.extend(
            [
                "## Historical context",
                "",
                (
                    f"- `{legacy_runs}` observe_only run(s) in this window had no target domain configured. "
                    "Their learning notes and baselines are system-level only."
                ),
            ]
        )

    return "\n".join(lines) + "\n"


def write_reports(
    reports_dir: Path,
    json_state_dir: Path,
    result: CycleResult,
    storage: Storage,
    formats: tuple[str, ...],
) -> tuple[Path, Path | None, Path | None]:
    run_date = result.finished_at[:10].split("-")
    dated_dir = reports_dir / "runs" / run_date[0] / run_date[1] / run_date[2]
    json_state_path = json_state_dir / f"{result.run_id}.json"
    latest_json_path: Path | None = None
    latest_markdown_path: Path | None = None

    _write_json(json_state_path, result.to_dict())

    if "json" in formats:
        latest_json_path = reports_dir / "latest.json"
        _write_json(dated_dir / f"{result.run_id}.json", result.to_dict())
        _write_json(latest_json_path, result.to_dict())

    if "markdown" in formats:
        latest_markdown_path = reports_dir / "latest.md"
        dated_markdown_path = dated_dir / f"{result.run_id}.md"
        markdown = _render_markdown(result)
        dated_markdown_path.parent.mkdir(parents=True, exist_ok=True)
        dated_markdown_path.write_text(markdown, encoding="utf-8")
        latest_markdown_path.write_text(markdown, encoding="utf-8")

    for days in (1, 7, 30, 365):
        rollup = storage.build_rollup(days)
        rollup_dir = reports_dir / "rollups"
        _write_json(rollup_dir / f"{days}d.json", rollup)
        (rollup_dir / f"{days}d.md").write_text(_render_rollup_markdown(rollup), encoding="utf-8")

    return json_state_path, latest_json_path, latest_markdown_path
