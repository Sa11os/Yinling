"""Regression coverage for image reconstruction and publication. SPDX-License-Identifier: MIT."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_release import build
from petlib import (
    MANIFEST, assemble, cell, inside, load_manifest, privacy_findings,
    sha256, validate_atlas, verify_public_files,
)


class PetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()
        cls.atlas = inside(MANIFEST.parent, cls.manifest["atlas"]["file"])
        cls.temp_root = inside(ROOT, ".verify/tests")
        cls.temp_root.mkdir(parents=True, exist_ok=True)

    def test_canonical_layout_and_digest(self):
        report = validate_atlas(self.atlas, self.manifest, verify_hash=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual((report["used_frames"], report["empty_cells"]), (73, 15))
        self.assertGreaterEqual(report["jump"]["airborne_lift_pixels"], 16)
        self.assertLessEqual(report["jump"]["landing_delta_pixels"], 3)

    def test_source_reconstruction_matches_every_pixel(self):
        rebuilt = assemble(ROOT / "source" / "frames", self.manifest)
        with Image.open(self.atlas) as canonical:
            self.assertEqual(rebuilt.mode, canonical.mode)
            self.assertEqual(rebuilt.size, canonical.size)
            self.assertEqual(rebuilt.tobytes(), canonical.tobytes())

    def test_missing_source_frames_are_reported(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            with self.assertRaisesRegex(ValueError, "Source frame set"):
                assemble(Path(temporary), self.manifest)

    def mutated_report(self, mutate):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            path = Path(temporary) / "mutated.png"
            with Image.open(self.atlas) as original:
                image = original.copy()
                mutate(image)
                image.save(path)
            return validate_atlas(path, self.manifest)

    def test_erased_required_cell_is_rejected(self):
        report = self.mutated_report(lambda image: image.paste((0, 0, 0, 0), (0, 0, 192, 208)))
        self.assertFalse(report["ok"])
        self.assertTrue(any("Required cell 0/0" in error for error in report["errors"]))

    def test_visible_pixels_in_unused_cell_are_rejected(self):
        report = self.mutated_report(lambda image: image.putpixel((7 * 192 + 20, 20), (0, 0, 0, 255)))
        self.assertFalse(report["ok"])
        self.assertTrue(any("Unused cell 0/7" in error for error in report["errors"]))

    def test_stationary_jump_is_rejected(self):
        def stationary(image):
            idle = cell(image, 0, 0)
            for column in range(5):
                image.paste(idle, (column * 192, 4 * 208))
        report = self.mutated_report(stationary)
        self.assertFalse(report["ok"])
        self.assertTrue(any("airborne" in error for error in report["errors"]))

    def test_wrong_dimensions_and_missing_alpha_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            path = Path(temporary) / "wrong.png"
            for mode, size in [("RGB", (1536, 2288)), ("RGBA", (192, 208))]:
                Image.new(mode, size).save(path)
                self.assertFalse(validate_atlas(path, self.manifest)["ok"])

    def test_digest_detects_an_otherwise_valid_changed_image(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            path = Path(temporary) / "changed.png"
            with Image.open(self.atlas) as image:
                copy = image.copy()
                x, y = next((x, y) for y in range(208) for x in range(192)
                            if copy.getpixel((x, y))[3] == 255)
                r, g, b, a = copy.getpixel((x, y))
                copy.putpixel((x, y), ((r + 1) % 256, g, b, a))
                copy.save(path)
            self.assertTrue(validate_atlas(path, self.manifest)["ok"])
            report = validate_atlas(path, self.manifest, verify_hash=True)
            self.assertFalse(report["ok"])
            self.assertTrue(any("SHA-256" in error for error in report["errors"]))

    def test_private_values_are_flagged(self):
        samples = [
            "Z" + ":/" + "private/person/file.png",
            "pet_" + "a" * 32,
            "github_pat_" + "Q" * 40,
        ]
        for sample in samples:
            self.assertTrue(privacy_findings(sample))
        self.assertFalse(privacy_findings("assets/yinling/spritesheet.png"))

    def test_manifest_rejects_reversed_gaze_angles(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            data = json.loads(MANIFEST.read_text(encoding="utf-8"))
            data["animations"][9]["directions_degrees"].reverse()
            path = Path(temporary) / "pet.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "clockwise"):
                load_manifest(path)

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            with self.assertRaisesRegex(ValueError, "escapes"):
                inside(Path(temporary), "../outside.png")

    def test_version_tag_must_match_manifest(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary:
            with self.assertRaisesRegex(ValueError, "Release tag"):
                build(Path(temporary), "v999.0.0")

    def test_public_release_is_complete_private_free_and_reproducible(self):
        public = {path.relative_to(ROOT).as_posix() for path in verify_public_files()}
        with tempfile.TemporaryDirectory(dir=self.temp_root) as first, tempfile.TemporaryDirectory(dir=self.temp_root) as second:
            outputs = build(Path(first), "v" + self.manifest["version"])
            repeated = build(Path(second), "v" + self.manifest["version"])
            self.assertEqual({path.name: sha256(path) for path in outputs},
                             {path.name: sha256(path) for path in repeated})
            standalone = next(path for path in outputs if path.suffix == ".json")
            download_manifest = json.loads(standalone.read_text(encoding="utf-8"))
            download_png = inside(standalone.parent, download_manifest["atlas"]["file"])
            self.assertEqual(sha256(download_png), download_manifest["atlas"]["sha256"])
            source = next(path for path in outputs if path.name.startswith("yinling-source"))
            with zipfile.ZipFile(source) as archive:
                self.assertEqual(set(archive.namelist()), public)
                self.assertEqual(len([name for name in archive.namelist()
                                     if name.startswith("source/frames/") and name.endswith(".png")]), 73)
                self.assertEqual(archive.read("assets/yinling/spritesheet.png"), self.atlas.read_bytes())
            ready = next(path for path in outputs if path.suffix == ".zip" and path != source)
            with zipfile.ZipFile(ready) as archive:
                names = set(archive.namelist())
                self.assertEqual(archive.read("spritesheet.png"), self.atlas.read_bytes())
                for required in ("README.md", "INSTALL.md", "LICENSE-ASSETS.txt", "CREDITS.md", "pet.json"):
                    self.assertIn(required, names)
                # Validate every relative Markdown destination inside the asset package.
                for name in names:
                    if name.endswith(".md"):
                        text = archive.read(name).decode("utf-8")
                        for link in re.findall(r"\]\(([^)]+)\)", text):
                            if "://" in link or link.startswith("#"):
                                continue
                            destination = (Path(name).parent / link.split("#")[0]).as_posix()
                            self.assertIn(destination, names, (name, link))
            sums = Path(first).joinpath("SHA256SUMS.txt").read_text(encoding="ascii")
            for line in sums.splitlines():
                digest, filename = line.split("  ", 1)
                self.assertEqual(digest, sha256(Path(first) / filename))


if __name__ == "__main__":
    unittest.main()
