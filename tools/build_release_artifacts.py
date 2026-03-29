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

from electri_city_ops.manifest_builder import build_release_artifact
from electri_city_ops.product_core import load_release_channels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local preview-only release artifact metadata.")
    parser.add_argument("--package-metadata", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--entitlement", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--built-at", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    channels = load_release_channels(WORKSPACE_ROOT).channels
    artifact, issues = build_release_artifact(
        load_json(args.package_metadata),
        load_json(args.manifest),
        load_json(args.entitlement),
        channels,
        artifact_id=args.artifact_id,
        built_at=args.built_at,
    )
    payload = {"valid": not issues, "issues": list(issues), "artifact": artifact}

    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))

    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
