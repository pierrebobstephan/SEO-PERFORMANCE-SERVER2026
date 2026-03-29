from __future__ import annotations

from pathlib import Path

from electri_city_ops.config import AppConfig
from electri_city_ops.models import ValidationCheck


def validate_cycle(
    config: AppConfig,
    database_path: Path,
    json_state_path: Path,
    latest_json_path: Path | None,
    latest_markdown_path: Path | None,
) -> list[ValidationCheck]:
    checks: list[ValidationCheck] = [
        ValidationCheck(
            name="database_exists",
            success=database_path.exists() and database_path.stat().st_size > 0,
            detail=f"Database path: {database_path}",
        ),
        ValidationCheck(
            name="json_state_exists",
            success=json_state_path.exists() and json_state_path.stat().st_size > 0,
            detail=f"JSON state path: {json_state_path}",
        ),
    ]

    if "json" in config.report_formats and latest_json_path is not None:
        checks.append(
            ValidationCheck(
                name="latest_json_report_exists",
                success=latest_json_path.exists() and latest_json_path.stat().st_size > 0,
                detail=f"Latest JSON report path: {latest_json_path}",
            )
        )
    if "markdown" in config.report_formats and latest_markdown_path is not None:
        checks.append(
            ValidationCheck(
                name="latest_markdown_report_exists",
                success=latest_markdown_path.exists() and latest_markdown_path.stat().st_size > 0,
                detail=f"Latest Markdown report path: {latest_markdown_path}",
            )
        )
    return checks

