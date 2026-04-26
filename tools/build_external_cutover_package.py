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

from electri_city_ops.external_cutover import build_external_cutover_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the external cutover package preview.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--built-at", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    package = build_external_cutover_package(WORKSPACE_ROOT)
    payload = {
        "built_at": args.built_at,
        "external_cutover_package": package,
    }
    output_path = (WORKSPACE_ROOT / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
