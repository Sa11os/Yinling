"""Render portable GIF/contact previews with Pillow. SPDX-License-Identifier: MIT."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

from petlib import MANIFEST, ROOT, cell, inside, load_manifest


def card(frame: Image.Image, label: str) -> Image.Image:
    canvas = Image.new("RGBA", (256, 264), "#f5f3f8")
    canvas.alpha_composite(frame, (32, 30))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), label, fill="#51445e")
    return canvas.convert("RGB")


def save_gif(path: Path, frames: list[Image.Image], durations: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)


def render(atlas_path: Path, output: Path, manifest: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    all_frames, all_durations, looks, look_durations = [], [], [], []
    with Image.open(atlas_path) as atlas:
        contact = Image.new("RGB", (8 * 256, 11 * 264), "#f5f3f8")
        for row in manifest["animations"]:
            frames = []
            for column in range(row["frames"]):
                label = f"{row['name']} / {column}"
                if "directions_degrees" in row:
                    label = f"look / {row['directions_degrees'][column]:g} deg"
                preview = card(cell(atlas, row["row"], column), label)
                frames.append(preview)
                contact.paste(preview, (column * 256, row["row"] * 264))
            if row["row"] < 9:
                save_gif(output / "states" / f"{row['name']}.gif", frames, row["durations_ms"])
                all_frames.extend(frames)
                all_durations.extend(row["durations_ms"])
            else:
                looks.extend(frames)
                look_durations.extend(row["durations_ms"])
        save_gif(output / "all-states.gif", all_frames, all_durations)
        save_gif(output / "look-loop.gif", looks, look_durations)
        contact.save(output / "contact-sheet.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render GIF and PNG previews from the atlas")
    parser.add_argument("--atlas", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "previews")
    args = parser.parse_args()
    manifest = load_manifest()
    atlas_path = args.atlas or inside(MANIFEST.parent, manifest["atlas"]["file"])
    render(atlas_path, args.output, manifest)
    print("Rendered nine state GIFs, all states, look loop and contact sheet")


if __name__ == "__main__":
    main()
