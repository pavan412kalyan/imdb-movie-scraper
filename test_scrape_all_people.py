import unittest

from ImdbDataExtraction.people_downloader.scrape_all_people import (
    extract_people,
    format_partial_date,
)


def _person_with_dates(birth_components=None, death_components=None):
    name = {
        "id": "nm0000001",
        "nameText": {"text": "Example Person"},
    }
    if birth_components is not None:
        name["birthDate"] = {"dateComponents": birth_components}
    if death_components is not None:
        name["deathDate"] = {"dateComponents": death_components}

    return {
        "data": {
            "advancedNameSearch": {
                "edges": [
                    {
                        "node": {
                            "name": name,
                        }
                    }
                ]
            }
        }
    }


class PartialDateTests(unittest.TestCase):
    def test_formats_full_date(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": 1980, "month": 7, "day": 4}}),
            "1980-07-04",
        )

    def test_formats_year_and_month_only(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": 1980, "month": 7, "day": None}}),
            "1980-07",
        )

    def test_formats_year_only(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": 1980, "month": None, "day": None}}),
            "1980",
        )

    def test_missing_year_preserves_month_and_day(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": None, "month": 7, "day": 4}}),
            "--07-04",
        )

    def test_missing_year_and_day_preserves_month(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": None, "month": 7, "day": None}}),
            "--07",
        )

    def test_day_without_month_is_ignored(self):
        self.assertEqual(
            format_partial_date({"dateComponents": {"year": 1980, "month": None, "day": 4}}),
            "1980",
        )

    def test_extract_people_handles_null_birth_and_death_components(self):
        people = extract_people(
            _person_with_dates(
                birth_components={"year": None, "month": 7, "day": 4},
                death_components={"year": 2024, "month": None, "day": None},
            )
        )

        self.assertEqual(len(people), 1)
        self.assertEqual(people[0]["birthDate"], "--07-04")
        self.assertEqual(people[0]["deathDate"], "2024")


if __name__ == "__main__":
    unittest.main()
