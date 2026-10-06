"""Opt-in checks against IMDb: IMDB_LIVE_TESTS=1 python3 -m unittest discover -s tests -v."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ImdbDataExtraction.search_by_id.search_movie import (
    format_movie_details,
    get_movie_details,
)

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get("IMDB_LIVE_TESTS") == "1", "Set IMDB_LIVE_TESTS=1 to contact IMDb")
class LiveTitleLookupTests(unittest.TestCase):
    def check_title(self, movie_id):
        data = get_movie_details(movie_id)
        self.assertFalse(data.get("errors"), data.get("errors"))
        raw = data["data"]["title"]
        self.assertIsNotNone(raw)
        movie = format_movie_details(data)
        self.assertEqual(movie["id"], movie_id)
        self.assertEqual(movie["title"], raw["titleText"]["text"])
        self.assertTrue(movie["title"])
        self.assertIsInstance(movie["credits"], dict)
        self.assertIsInstance(movie["enhanced_actors"], list)
        # Compare with current data instead of assuming cast names or counts stay fixed.
        for group in raw.get("principalCredits") or []:
            category = (group.get("category") or {}).get("text", "Unknown")
            for credit in group.get("credits") or []:
                person = credit.get("name") or {}
                if not (person.get("nameText") or {}).get("text"):
                    continue
                matches = [entry for entry in movie["credits"].get(category, [])
                           if entry["id"] == person["id"]]
                self.assertTrue(matches, person["id"])
                expected = [character.get("name") for character in credit.get("characters") or []]
                self.assertEqual(matches[0].get("characters", []), expected)
                if category == "Stars":
                    actors = [actor for actor in movie["enhanced_actors"]
                              if actor["url"] == f"https://www.imdb.com/name/{person['id']}/"]
                    self.assertTrue(actors, person["id"])
                    self.assertEqual(actors[0]["characters"], [name for name in expected if name])

    def test_issue_32_title(self):
        self.check_title("tt39123235")

    def test_established_title(self):
        self.check_title("tt0111161")

    def test_cli_writes_valid_json(self):
        with tempfile.TemporaryDirectory(prefix="imdb-live-test-") as directory:
            output = Path(directory) / "movie.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "ImdbDataExtraction/search_by_id/search_movie.py"),
                 "tt39123235", "--output", str(output), "--json-only"],
                cwd=ROOT, capture_output=True, text=True, timeout=45,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file(), result.stdout + result.stderr)
            movie = json.loads(output.read_text())
            self.assertEqual(movie["id"], "tt39123235")
            self.assertTrue(movie["title"])
            self.assertIsInstance(movie["credits"], dict)
            self.assertIsInstance(movie["enhanced_actors"], list)


if __name__ == "__main__":
    unittest.main()
