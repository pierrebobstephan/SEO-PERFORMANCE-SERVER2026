#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.manifest_builder import validate_plugin_package_metadata
from electri_city_ops.product_core import load_release_channels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local installable WordPress plugin zip for staging-only use.")
    parser.add_argument("--plugin-root", default="packages/wp-plugin/hetzner-seo-ops")
    parser.add_argument("--plugin-slug", default="hetzner-seo-ops")
    parser.add_argument("--version", required=True)
    parser.add_argument("--channel", default="pilot")
    parser.add_argument("--built-at", required=True)
    parser.add_argument("--output-dir", default="dist/staging-only")
    parser.add_argument("--package-basename", required=True)
    parser.add_argument("--raw-metadata-output", required=True)
    parser.add_argument("--metadata-output", required=True)
    return parser.parse_args()


def iter_files(plugin_root: Path) -> list[Path]:
    return sorted(path for path in plugin_root.rglob("*") if path.is_file())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(plugin_root: Path, plugin_slug: str, archive_path: Path) -> int:
    files = iter_files(plugin_root)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(plugin_root).as_posix()
            archive.write(path, arcname=f"{plugin_slug}/{relative}")
    return len(files)


def main() -> int:
    args = parse_args()
    channels = load_release_channels(WORKSPACE_ROOT).channels
    plugin_root = (WORKSPACE_ROOT / args.plugin_root).resolve()
    if not plugin_root.exists():
        raise SystemExit(f"plugin root not found: {plugin_root}")

    archive_path = (WORKSPACE_ROOT / args.output_dir / f"{args.package_basename}.zip").resolve()
    file_count = build_archive(plugin_root, args.plugin_slug, archive_path)
    metadata = {
        "plugin_slug": args.plugin_slug,
        "plugin_version": args.version,
        "release_channel": args.channel,
        "package_basename": args.package_basename,
        "package_filename": archive_path.name,
        "package_sha256": sha256_file(archive_path),
        "file_count": file_count,
        "build_mode": "local_preview_only",
        "built_at": args.built_at,
    }
    validation = validate_plugin_package_metadata(metadata, channels)
    payload = {
        "valid": validation.valid,
        "issues": list(validation.issues),
        "archive_path": archive_path.relative_to(WORKSPACE_ROOT).as_posix(),
        "metadata": metadata,
    }

    raw_metadata_path = (WORKSPACE_ROOT / args.raw_metadata_output).resolve()
    metadata_output_path = (WORKSPACE_ROOT / args.metadata_output).resolve()
    raw_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    metadata_output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if validation.valid else 1


if __name__ == "__main__":
    sys.exit(main())
