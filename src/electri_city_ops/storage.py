from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from electri_city_ops.models import CycleResult


class Storage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    source TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS target_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    final_url TEXT NOT NULL,
                    homepage_status_code INTEGER NOT NULL,
                    response_ms REAL NOT NULL,
                    html_bytes INTEGER NOT NULL,
                    content_encoding TEXT NOT NULL,
                    cache_control TEXT NOT NULL,
                    title TEXT NOT NULL,
                    meta_description TEXT NOT NULL,
                    canonical TEXT NOT NULL,
                    h1_count INTEGER NOT NULL,
                    html_lang TEXT NOT NULL,
                    viewport_present INTEGER NOT NULL,
                    robots_meta TEXT NOT NULL,
                    sitemap_status_code INTEGER NOT NULL,
                    fetch_error TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    identifier TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT NOT NULL,
                    target TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    reversible INTEGER NOT NULL,
                    requires_approval INTEGER NOT NULL,
                    rollback TEXT NOT NULL,
                    validation TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    detail TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    source TEXT NOT NULL
                )
                """
            )

    def upsert_cycle(self, result: CycleResult) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO runs (run_id, started_at, finished_at, mode, status, summary_json)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    started_at=excluded.started_at,
                    finished_at=excluded.finished_at,
                    mode=excluded.mode,
                    status=excluded.status,
                    summary_json=excluded.summary_json
                """,
                (
                    result.run_id,
                    result.started_at,
                    result.finished_at,
                    result.mode,
                    result.status,
                    json.dumps(result.summary, sort_keys=True),
                ),
            )
            for table in ("metrics", "target_snapshots", "findings", "actions", "validations", "learning_notes"):
                connection.execute(f"DELETE FROM {table} WHERE run_id = ?", (result.run_id,))

            connection.executemany(
                """
                INSERT INTO target_snapshots (
                    run_id, domain, final_url, homepage_status_code, response_ms, html_bytes,
                    content_encoding, cache_control, title, meta_description, canonical,
                    h1_count, html_lang, viewport_present, robots_meta, sitemap_status_code, fetch_error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        result.run_id,
                        item.domain,
                        item.final_url,
                        item.homepage_status_code,
                        item.response_ms,
                        item.html_bytes,
                        item.content_encoding,
                        item.cache_control,
                        item.title,
                        item.meta_description,
                        item.canonical,
                        item.h1_count,
                        item.html_lang,
                        int(item.viewport_present),
                        item.robots_meta,
                        item.sitemap_status_code,
                        item.fetch_error,
                    )
                    for item in result.target_results
                ],
            )
            connection.executemany(
                """
                INSERT INTO metrics (run_id, name, value, unit, scope, source)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (result.run_id, item.name, item.value, item.unit, item.scope, item.source)
                    for item in result.metrics
                ],
            )
            connection.executemany(
                """
                INSERT INTO findings (
                    run_id, fingerprint, category, severity, title, detail, risk,
                    confidence, source, target, recommendation, created_at, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        result.run_id,
                        item.fingerprint,
                        item.category,
                        item.severity,
                        item.title,
                        item.detail,
                        item.risk,
                        item.confidence,
                        item.source,
                        item.target,
                        item.recommendation,
                        result.finished_at,
                        json.dumps(item.metadata, sort_keys=True),
                    )
                    for item in result.findings
                ],
            )
            connection.executemany(
                """
                INSERT INTO actions (
                    run_id, identifier, phase, scope, status, description, target,
                    risk, reversible, requires_approval, rollback, validation, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        result.run_id,
                        item.identifier,
                        item.phase,
                        item.scope,
                        item.status,
                        item.description,
                        item.target,
                        item.risk,
                        int(item.reversible),
                        int(item.requires_approval),
                        item.rollback,
                        item.validation,
                        json.dumps(item.metadata, sort_keys=True),
                    )
                    for item in result.actions
                ],
            )
            connection.executemany(
                """
                INSERT INTO validations (run_id, name, success, detail)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (result.run_id, item.name, int(item.success), item.detail)
                    for item in result.validations
                ],
            )
            connection.executemany(
                """
                INSERT INTO learning_notes (run_id, title, detail, source)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (result.run_id, item.title, item.detail, item.source)
                    for item in result.learning_notes
                ],
            )

    def recurrence_map(self, days: int) -> dict[str, int]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT fingerprint, COUNT(*)
                FROM findings
                WHERE created_at >= ?
                GROUP BY fingerprint
                """,
                (cutoff,),
            ).fetchall()
        return {fingerprint: count for fingerprint, count in rows}

    def count_observe_only_runs_without_targets(self, exclude_run_id: str | None = None) -> int:
        query = (
            """
            SELECT COUNT(DISTINCT runs.run_id)
            FROM runs
            JOIN metrics ON metrics.run_id = runs.run_id
            WHERE runs.mode = 'observe_only'
              AND metrics.name = 'configured_domains'
              AND metrics.value = 0
            """
        )
        params: list[Any] = []
        if exclude_run_id:
            query += " AND runs.run_id != ?"
            params.append(exclude_run_id)
        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(query, params).fetchone()
        return int(row[0] or 0)

    def build_rollup(self, days: int) -> dict[str, Any]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.database_path) as connection:
            run_rows = connection.execute(
                "SELECT run_id, status FROM runs WHERE finished_at >= ? ORDER BY finished_at DESC",
                (cutoff,),
            ).fetchall()
            finding_rows = connection.execute(
                """
                SELECT severity, category, fingerprint, title
                FROM findings
                WHERE created_at >= ?
                """,
                (cutoff,),
            ).fetchall()
            metric_rows = connection.execute(
                """
                SELECT metrics.scope, metrics.name, metrics.value, runs.finished_at
                FROM metrics
                JOIN runs ON runs.run_id = metrics.run_id
                WHERE runs.finished_at >= ?
                ORDER BY runs.finished_at ASC
                """,
                (cutoff,),
            ).fetchall()
            legacy_runs = connection.execute(
                """
                SELECT COUNT(DISTINCT runs.run_id)
                FROM runs
                JOIN metrics ON metrics.run_id = runs.run_id
                WHERE runs.finished_at >= ?
                  AND runs.mode = 'observe_only'
                  AND metrics.name = 'configured_domains'
                  AND metrics.value = 0
                """,
                (cutoff,),
            ).fetchone()

        status_counts = Counter(status for _, status in run_rows)
        severity_counts = Counter(severity for severity, _, _, _ in finding_rows)
        category_counts = Counter(category for _, category, _, _ in finding_rows)
        recurring = Counter((fingerprint, title) for _, _, fingerprint, title in finding_rows)
        metric_buckets: dict[str, list[float]] = defaultdict(list)
        trend_buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        for scope, name, value, _finished_at in metric_rows:
            metric_buckets[name].append(float(value))
            if scope != "system" and name in {"response_ms", "html_bytes"}:
                trend_buckets[scope][name].append(float(value))

        metrics_summary = {
            name: {
                "count": len(values),
                "avg": round(sum(values) / len(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }
            for name, values in metric_buckets.items()
            if values
        }

        top_recurring = [
            {"fingerprint": fingerprint, "title": title, "count": count}
            for (fingerprint, title), count in recurring.most_common(10)
        ]

        domain_trends: dict[str, dict[str, Any]] = {}
        for scope, metric_map in trend_buckets.items():
            domain_trends[scope] = {}
            for name, values in metric_map.items():
                latest = round(values[-1], 2)
                previous = round(values[-2], 2) if len(values) >= 2 else None
                delta = round(latest - previous, 2) if previous is not None else None
                if previous is None:
                    direction = "insufficient_data"
                elif abs(delta or 0) < 1:
                    direction = "flat"
                else:
                    direction = "improving" if (delta or 0) < 0 else "worsening"
                domain_trends[scope][name] = {
                    "samples": len(values),
                    "latest": latest,
                    "previous": previous,
                    "delta": delta,
                    "direction": direction,
                    "avg": round(sum(values) / len(values), 2),
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                }

        return {
            "days": days,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "run_count": len(run_rows),
            "status_counts": dict(status_counts),
            "finding_counts": dict(severity_counts),
            "category_counts": dict(category_counts),
            "top_recurring_findings": top_recurring,
            "metric_summary": metrics_summary,
            "domain_trends": domain_trends,
            "legacy_observe_only_runs_without_targets": int(legacy_runs[0] or 0),
        }
