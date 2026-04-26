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

from electri_city_ops.productization import (
    build_reference_pilot_runtime_input,
    validate_reference_pilot_runtime_input,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a normalized reference-pilot runtime input from an installed bridge export."
    )
    parser.add_argument("--input", required=True, help="JSON export from the installed bridge runtime.")
    parser.add_argument("--output", required=True, help="Target JSON file for config/reference-pilot-runtime-input.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = (WORKSPACE_ROOT / args.input).resolve()
    output_path = (WORKSPACE_ROOT / args.output).resolve()

    export_payload = json.loads(input_path.read_text(encoding="utf-8"))
    runtime_input = build_reference_pilot_runtime_input(export_payload)
    issues = validate_reference_pilot_runtime_input(runtime_input)
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2))
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(runtime_input, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output_path.relative_to(WORKSPACE_ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
