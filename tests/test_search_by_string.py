import unittest

from ImdbDataExtraction.search_by_string.search_by_string import format_results


class SuggestionSearchTests(unittest.TestCase):
    def test_skips_editorial_item_and_finds_limit_valid_results(self):
        data = {
            "d": [
                {"id": "/family-entertainment-guide/", "l": "Holiday Watch Guide"},
                {"id": "tt1877830", "l": "The Batman", "y": 2022, "s": "Stars", "rank": 101},
                {"id": "nm0000558", "l": "Leslie Nielsen", "s": "Actor", "rank": 1677},
                {"id": "tt0096895", "l": "Batman", "y": 1989, "s": "Stars", "rank": 1910},
            ]
        }

        results = format_results(data, limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "tt1877830")

    def test_returns_multiple_valid_result_types_until_limit(self):
        data = {
            "d": [
                {"id": "tt1877830", "l": "The Batman", "y": 2022},
                {"id": "nm0000558", "l": "Leslie Nielsen"},
            ]
        }

        results = format_results(data, limit=2)

        self.assertEqual([result["id"] for result in results], ["tt1877830", "nm0000558"])


if __name__ == "__main__":
    unittest.main()
