import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from app import category_for, organize_folder, unique_destination


class SorterTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(category_for(Path("holiday.JPG")), "Photos")
        self.assertEqual(category_for(Path("Screenshot from today.png")), "Screenshots")
        self.assertEqual(category_for(Path("report.pdf")), "Documents")
        self.assertEqual(category_for(Path("unknown.xyz")), "Others")

    def test_unique_destination(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            (folder / "photo.jpg").touch()
            (folder / "photo (1).jpg").touch()
            self.assertEqual(unique_destination(folder / "photo.jpg").name, "photo (2).jpg")

    def test_organize_folder_moves_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "Downloads"
            destination = source
            source.mkdir()
            (source / "photo.jpg").write_text("new")
            (source / "notes.txt").write_text("notes")
            (source / "photo 2.jpg").write_text("second")
            photos = source / "Photos"
            photos.mkdir()
            (photos / "photo.jpg").write_text("old")
            moved, _, errors = organize_folder(source, destination)
            self.assertFalse(errors)
            self.assertEqual(len(moved), 3)
            self.assertEqual((photos / "photo.jpg").read_text(), "old")
            self.assertTrue((photos / "photo (1).jpg").exists())
            self.assertTrue((source / "Documents" / "notes.txt").exists())


if __name__ == "__main__":
    unittest.main()
