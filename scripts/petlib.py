"""Shared, portable asset maintenance helpers. SPDX-License-Identifier: MIT."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets" / "yinling" / "pet.json"
WIDTH, HEIGHT, CELL_WIDTH, CELL_HEIGHT = 1536, 2288, 192, 208
COUNTS = (6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)
NAMES = (
    "idle", "running-right", "running-left", "waving", "jumping",
    "failed", "waiting", "running", "review", "look-row-9", "look-row-10",
)
PUBLIC_ROOT_FILES = (
    ".gitignore", ".gitattributes", "README.md", "README.en.md", "INSTALL.md",
    "LICENSE", "LICENSE-ASSETS.txt", "CREDITS.md", "CONTRIBUTING.md",
    "CHANGELOG.md", "requirements.txt",
)
PUBLIC_DIRECTORIES = ("assets", "source", "docs", "scripts", "tests", ".github")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes its declared root: {relative}")
    return path


def load_manifest(path: Path = MANIFEST) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "yinling-pet/1":
        raise ValueError("Expected manifest schema yinling-pet/1")
    atlas = data["atlas"]
    expected = {
        "width": WIDTH, "height": HEIGHT, "columns": 8, "rows": 11,
        "cell_width": CELL_WIDTH, "cell_height": CELL_HEIGHT, "mode": "RGBA",
        "sprite_version": 2, "used_frames": sum(COUNTS),
    }
    if any(atlas.get(key) != value for key, value in expected.items()):
        raise ValueError("Manifest layout differs from the Pets v2 asset contract")
    if not re.fullmatch(r"[0-9a-f]{64}", atlas.get("sha256", "")):
        raise ValueError("Expected a SHA-256 digest")
    if not re.fullmatch(r"\d+\.\d+\.\d+", data.get("version", "")):
        raise ValueError("Expected a numeric three-part version")
    rows = data["animations"]
    if len(rows) != len(COUNTS):
        raise ValueError("Expected eleven atlas rows")
    for index, (row, count, name) in enumerate(zip(rows, COUNTS, NAMES)):
        if row.get("row") != index or row.get("frames") != count or row.get("name") != name:
            raise ValueError(f"Unexpected animation contract at row {index}")
        durations = row.get("durations_ms", [])
        if len(durations) != count or any(type(ms) is not int or ms <= 0 for ms in durations):
            raise ValueError(f"Invalid frame timing at row {index}")
        inside(ROOT, row["source_directory"])
        if index >= 9:
            angles = [((index - 9) * 8 + column) * 22.5 for column in range(8)]
            if row.get("directions_degrees") != angles:
                raise ValueError(f"Unexpected clockwise directions at row {index}")
    inside(path.parent, atlas["file"])
    return data


def cell(atlas: Image.Image, row: int, column: int) -> Image.Image:
    x, y = column * CELL_WIDTH, row * CELL_HEIGHT
    return atlas.crop((x, y, x + CELL_WIDTH, y + CELL_HEIGHT))


def validate_atlas(path: Path, manifest: dict, verify_hash: bool = False) -> dict:
    errors: list[str] = []
    report = {"ok": False, "errors": errors, "used_frames": 0, "empty_cells": 0}
    if verify_hash and sha256(path) != manifest["atlas"]["sha256"]:
        errors.append("Atlas SHA-256 differs from the declared release")
    with Image.open(path) as atlas:
        if atlas.format != "PNG":
            errors.append("Expected PNG encoding")
        if atlas.size != (WIDTH, HEIGHT) or atlas.mode != "RGBA":
            errors.append(f"Expected {WIDTH}x{HEIGHT} RGBA, received {atlas.size} {atlas.mode}")
            return report
        frames = {}
        for row, count in enumerate(COUNTS):
            for column in range(8):
                frame = cell(atlas, row, column)
                alpha = frame.getchannel("A")
                hist = alpha.histogram()
                pixels = sum(hist[1:])
                if column >= count:
                    if pixels:
                        errors.append(f"Unused cell {row}/{column} contains visible pixels")
                    report["empty_cells"] += 1
                    continue
                report["used_frames"] += 1
                if pixels < 400:
                    errors.append(f"Required cell {row}/{column} is empty or undersized")
                bbox = alpha.getbbox()
                if bbox and (bbox[0] == 0 or bbox[1] == 0 or
                             bbox[2] == CELL_WIDTH or bbox[3] == CELL_HEIGHT):
                    errors.append(f"Foreground touches boundary of cell {row}/{column}")
                frames[row, column] = bbox
        idle = frames.get((0, 0))
        jump = [frames.get((4, col)) for col in range(COUNTS[4])]
        if idle and all(jump):
            baseline = idle[3] - 1
            bottoms = [box[3] - 1 for box in jump]
            lift = baseline - min(bottoms)
            landing = abs(bottoms[-1] - baseline)
            report["jump"] = {
                "idle_baseline": baseline, "jump_baselines": bottoms,
                "airborne_lift_pixels": lift, "landing_delta_pixels": landing,
            }
            if lift < 16:
                errors.append("Jump needs a visible airborne lift of at least 16 pixels")
            if landing > 3:
                errors.append("Jump landing drifts more than 3 pixels from idle")
    report["ok"] = not errors
    return report


def assemble(frames_root: Path, manifest: dict) -> Image.Image:
    atlas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    for row in manifest["animations"]:
        folder = inside(frames_root, row["name"])
        expected = {f"{col:02d}.png" for col in range(row["frames"])}
        actual = {file.name for file in folder.glob("*.png")}
        if actual != expected:
            raise ValueError(f"Source frame set differs at {row['name']}")
        for column in range(row["frames"]):
            frame_path = inside(folder, f"{column:02d}.png")
            with Image.open(frame_path) as frame:
                if frame.size != (CELL_WIDTH, CELL_HEIGHT) or frame.mode != "RGBA":
                    raise ValueError(f"Expected a complete RGBA cell: {frame_path.name}")
                atlas.paste(frame, (column * CELL_WIDTH, row["row"] * CELL_HEIGHT))
    return atlas


def public_files(root: Path = ROOT) -> list[Path]:
    files = [root / name for name in PUBLIC_ROOT_FILES]
    for directory in PUBLIC_DIRECTORIES:
        folder = root / directory
        if not folder.is_dir():
            raise ValueError(f"Missing public directory: {directory}")
        files.extend(path for path in folder.rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts
                     and path.suffix not in {".pyc", ".pyo"})
    for path in files:
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Missing or external public file: {path.name}")
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def privacy_findings(value: str) -> list[str]:
    patterns = {
        "machine absolute path": r"\b[A-Za-z]:[\\/]|/(?:Users|home)/[^/\s]+",
        "private account object identifier": r"\b(?:pet|page|file|sharepet)_[0-9a-f]{24,}\b",
        "credential": r"\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]{20,}",
    }
    return [label for label, pattern in patterns.items() if re.search(pattern, value)]


def verify_public_files(root: Path = ROOT) -> list[Path]:
    files = public_files(root)
    text_extensions = {".md", ".py", ".json", ".txt", ".yml", ".yaml"}
    for path in files:
        if path.suffix in text_extensions or path.name.startswith("LICENSE"):
            findings = privacy_findings(path.read_text(encoding="utf-8"))
            if findings:
                raise ValueError(f"Public text needs review: {path.relative_to(root)}: {findings}")
    return files
