from __future__ import annotations

import argparse
import json
from pathlib import Path

from electri_city_ops.ai_governance import collect_ai_governance_status
from electri_city_ops.config import load_config
from electri_city_ops.doctrine import load_doctrine_policy, validate_policy_schema
from electri_city_ops.orchestrator import run_cycle, run_loop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Electri City Ops")
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Explicit workspace root. Defaults to the directory above the config folder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("run-cycle", "run-loop", "validate-config"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--config", default="config/settings.toml")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else None

    if args.command == "validate-config":
        config, notes = load_config(args.config, workspace_root)
        doctrine = load_doctrine_policy(config.workspace_root)
        ai_governance = collect_ai_governance_status(config.workspace_root, doctrine.policy)
        payload = {
            "mode": config.mode,
            "workspace_root": str(config.workspace_root),
            "domains": list(config.domains),
            "allow_remote_fetch": config.allow_remote_fetch,
            "allow_external_changes": config.allow_external_changes,
            "report_formats": list(config.report_formats),
            "doctrine_policy_source": doctrine.source,
            "doctrine_policy_path": str(doctrine.path) if doctrine.path else "",
            "doctrine_policy_schema_issues": validate_policy_schema(doctrine.policy),
            "ai_governance_status": ai_governance["status"],
            "ai_governance_issues": ai_governance["issues"],
            "notes": notes,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    if args.command == "run-cycle":
        result = run_cycle(args.config, workspace_root)
        print(json.dumps(result.summary, indent=2, sort_keys=True))
        return 0

    if args.command == "run-loop":
        return run_loop(args.config, workspace_root)

    parser.error(f"unknown command: {args.command}")
    return 2
