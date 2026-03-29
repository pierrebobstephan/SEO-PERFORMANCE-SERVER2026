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

from electri_city_ops.manifest_builder import build_plugin_package_metadata, validate_plugin_package_metadata
from electri_city_ops.product_core import load_release_channels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local preview-only plugin package metadata.")
    parser.add_argument("--plugin-root", default="packages/wp-plugin/hetzner-seo-ops")
    parser.add_argument("--plugin-slug", default="hetzner-seo-ops")
    parser.add_argument("--version", required=True)
    parser.add_argument("--channel", default="pilot")
    parser.add_argument("--built-at", required=True)
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    channels = load_release_channels(WORKSPACE_ROOT).channels
    metadata = build_plugin_package_metadata(
        WORKSPACE_ROOT / args.plugin_root,
        plugin_slug=args.plugin_slug,
        plugin_version=args.version,
        release_channel=args.channel,
        built_at=args.built_at,
    )
    validation = validate_plugin_package_metadata(metadata, channels)
    payload = {"valid": validation.valid, "issues": list(validation.issues), "metadata": metadata}

    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2))

    return 0 if validation.valid else 1


if __name__ == "__main__":
    sys.exit(main())
