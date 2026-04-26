#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.onboarding import (
    transition_onboarding_state,
    validate_domain_onboarding_entry,
    validate_dry_run_onboarding_constraints,
)
from electri_city_ops.product_core import load_release_channels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local dry-run onboarding validation.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--target-state")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    channels = load_release_channels(WORKSPACE_ROOT).channels
    entry = json.loads(Path(args.input).read_text(encoding="utf-8"))

    validation = validate_domain_onboarding_entry(entry, channels)
    dry_run = validate_dry_run_onboarding_constraints(entry)
    transition_payload = None
    transition_issues: list[str] = []

    if args.target_state:
        transition = transition_onboarding_state(entry, args.target_state)
        transition_payload = transition.entry
        transition_issues.extend(list(transition.issues))

    payload = {
        "valid": validation.valid and dry_run.valid and not transition_issues,
        "validation_issues": list(validation.issues),
        "dry_run_issues": list(dry_run.issues),
        "transition_issues": transition_issues,
        "result": transition_payload or entry,
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
