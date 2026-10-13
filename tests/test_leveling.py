import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/backend"))
from user_xp_management.leveling import get_xp_progress


class LevelingTests(unittest.TestCase):
    def test_threshold_boundaries(self):
        for level, threshold in enumerate([0, 30, 100, 200, 350, 550, 800], start=1):
            with self.subTest(level=level):
                progress = get_xp_progress(threshold)
                self.assertEqual(progress["level"], level)
                self.assertEqual(progress["current"], 0)
                if threshold:
                    before = get_xp_progress(threshold - 1)
                    self.assertEqual(before["level"], level - 1)
                    self.assertEqual(before["current"], before["required"] - 1)

    def test_partial_progress(self):
        self.assertEqual(
            get_xp_progress(65),
            {
                "total": 65,
                "level": 2,
                "current": 35,
                "required": 70,
                "next_level_xp": 100,
            },
        )

    def test_legacy_xp(self):
        for xp in (None, -10):
            self.assertEqual(get_xp_progress(xp), get_xp_progress(0))

    def test_large_integer_xp(self):
        progress = get_xp_progress(2_147_483_647)
        self.assertGreaterEqual(progress["current"], 0)
        self.assertLess(progress["current"], progress["required"])
        self.assertGreater(progress["next_level_xp"], progress["total"])
