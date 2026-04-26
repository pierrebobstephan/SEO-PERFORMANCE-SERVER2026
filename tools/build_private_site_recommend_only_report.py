#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.private_site_report import build_and_write_private_site_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a private recommend-only SEO/performance report for approved public pages.")
    parser.add_argument("--config", required=True, help="JSON profile for the private site recommend-only report.")
    parser.add_argument("--settings", default="config/settings.toml", help="Main suite settings TOML.")
    parser.add_argument("--send-email", action="store_true", help="Send the generated report via SMTP if env refs are complete.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = logging.getLogger("electri_city_ops.private_site_report")
    logging.basicConfig(level=logging.INFO)
    report, json_path, markdown_path, sent = build_and_write_private_site_report(
        profile_path=args.config,
        config_path=args.settings,
        workspace_root=WORKSPACE_ROOT,
        send_email=args.send_email,
        logger=logger,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "report_id": report.get("report_id"),
                "json_path": str(json_path.relative_to(WORKSPACE_ROOT)),
                "markdown_path": str(markdown_path.relative_to(WORKSPACE_ROOT)),
                "email_sent": sent,
                "email_delivery_state": report.get("email_delivery_state", {}),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
