"""Validate a release atlas. SPDX-License-Identifier: MIT."""
import argparse
import json
from pathlib import Path

from petlib import MANIFEST, inside, load_manifest, validate_atlas


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Yinling's Pets v2 PNG")
    parser.add_argument("--atlas", type=Path, help="Alternate PNG to check")
    parser.add_argument("--verify-hash", action="store_true", help="Check the release digest")
    args = parser.parse_args()
    manifest = load_manifest()
    atlas = args.atlas or inside(MANIFEST.parent, manifest["atlas"]["file"])
    report = validate_atlas(atlas, manifest, args.verify_hash)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
