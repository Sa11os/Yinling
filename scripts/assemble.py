"""Rebuild the exact RGBA atlas from final cells. SPDX-License-Identifier: MIT."""
import argparse
from pathlib import Path

from petlib import ROOT, assemble, load_manifest, validate_atlas


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble final frames into a Pets v2 atlas")
    parser.add_argument("--frames", type=Path, default=ROOT / "source" / "frames")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "rebuilt-spritesheet.png")
    args = parser.parse_args()
    manifest = load_manifest()
    atlas = assemble(args.frames, manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(args.output, format="PNG")
    report = validate_atlas(args.output, manifest)
    if not report["ok"]:
        raise ValueError(report["errors"])
    print(f"Rebuilt {report['used_frames']} frames: {args.output.name}")


if __name__ == "__main__":
    main()
