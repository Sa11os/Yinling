"""Build public-only, deterministic release downloads. SPDX-License-Identifier: MIT."""
from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path

from petlib import MANIFEST, ROOT, inside, load_manifest, sha256, validate_atlas, verify_public_files, write_json

ZIP_TIMESTAMP = (2026, 10, 7, 0, 0, 0)


def zip_files(path: Path, entries: dict[str, Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, source in sorted(entries.items()):
            entry = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, source.read_bytes(), compresslevel=9)


def build(output: Path, tag: str | None = None) -> list[Path]:
    manifest = load_manifest()
    version_tag = "v" + manifest["version"]
    if tag is not None and tag != version_tag:
        raise ValueError(f"Release tag must match the manifest: {version_tag}")
    atlas = inside(MANIFEST.parent, manifest["atlas"]["file"])
    report = validate_atlas(atlas, manifest, verify_hash=True)
    if not report["ok"]:
        raise ValueError(report["errors"])
    public = verify_public_files()
    output = output.resolve()
    public_roots = (ROOT / name for name in ("assets", "source", "docs", "scripts", "tests", ".github"))
    if output == ROOT or any(output.is_relative_to(folder) for folder in public_roots):
        raise ValueError("Choose a dedicated build output directory")
    output.mkdir(parents=True, exist_ok=True)
    source_archive = output / f"yinling-source-{version_tag}.zip"
    zip_files(source_archive, {path.relative_to(ROOT).as_posix(): path for path in public})
    asset_entries = {
        "README.md": ROOT / "docs" / "DOWNLOAD_README.md",
        "spritesheet.png": atlas, "pet.json": MANIFEST,
    }
    for name in ("INSTALL.md", "LICENSE", "LICENSE-ASSETS.txt", "CREDITS.md"):
        asset_entries[name] = ROOT / name
    for name in ("ATLAS_FORMAT.md", "QUALITY.md", "quality-summary.json"):
        asset_entries["docs/" + name] = ROOT / "docs" / name
    for path in ROOT.joinpath("docs", "previews").rglob("*"):
        if path.is_file():
            asset_entries[path.relative_to(ROOT).as_posix()] = path
    asset_archive = output / f"yinling-{version_tag}.zip"
    zip_files(asset_archive, asset_entries)
    png = output / f"yinling-{version_tag}.png"
    json_path = output / f"yinling-{version_tag}.manifest.json"
    shutil.copyfile(atlas, png)
    download_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    download_manifest["atlas"]["file"] = png.name
    write_json(json_path, download_manifest)
    downloads = [asset_archive, source_archive, png, json_path]
    checksum = output / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{sha256(path)}  {path.name}\n" for path in sorted(downloads)),
                        encoding="ascii")
    return downloads + [checksum]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Yinling public downloads")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--tag", help="GitHub tag; must match the manifest")
    args = parser.parse_args()
    for path in build(args.output, args.tag):
        print(f"{path.name}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
