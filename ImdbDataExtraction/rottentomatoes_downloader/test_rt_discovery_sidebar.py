#!/usr/bin/env python3
"""
Unit tests for rt_discovery_sidebar.py
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to sys.path to import the module
sys.path.insert(0, os.path.dirname(__file__))

import rt_discovery_sidebar


class TestRtDiscoverySidebar(unittest.TestCase):

    def test_first_value(self):
        data = {"a": "value", "b": "", "c": None, "d": []}
        self.assertEqual(rt_discovery_sidebar.first_value(data, ["a"]), "value")
        self.assertEqual(rt_discovery_sidebar.first_value(data, ["b", "a"]), "value")
        self.assertIsNone(rt_discovery_sidebar.first_value(data, ["b", "c", "d"]))

    def test_score_value(self):
        self.assertEqual(rt_discovery_sidebar.score_value(85), 85)
        self.assertEqual(rt_discovery_sidebar.score_value({"scorePercent": 90}), 90)
        self.assertEqual(rt_discovery_sidebar.score_value({"score": 75}), 75)
        self.assertEqual(rt_discovery_sidebar.score_value({"value": 80}), 80)
        self.assertIsNone(rt_discovery_sidebar.score_value({}))

    def test_normalize_item(self):
        item = {
            "id": "123",
            "title": "Test Movie",
            "year": 2023,
            "tomatometerScore": 85,
            "audienceScore": 90,
            "synopsis": "A test movie",
            "url": "/m/test_movie",
            "posterUrl": "https://example.com/poster.jpg",
            "_section_title": "Popular",
            "_list_title": "Top Movies",
            "_details_url": "/details"
        }
        normalized = rt_discovery_sidebar.normalize_item(item)
        self.assertEqual(normalized["id"], "123")
        self.assertEqual(normalized["title"], "Test Movie")
        self.assertEqual(normalized["year"], 2023)
        self.assertEqual(normalized["tomatometer_score"], 85)
        self.assertEqual(normalized["audience_score"], 90)
        self.assertEqual(normalized["synopsis"], "A test movie")
        self.assertEqual(normalized["url"], "https://www.rottentomatoes.com/m/test_movie")
        self.assertEqual(normalized["poster_url"], "https://example.com/poster.jpg")
        self.assertEqual(normalized["section"], "Popular")
        self.assertEqual(normalized["list"], "Top Movies")
        self.assertEqual(normalized["details_url"], "https://www.rottentomatoes.com/details")

    @patch('rt_discovery_sidebar.requests.get')
    def test_fetch_discovery_sidebar_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        result = rt_discovery_sidebar.fetch_discovery_sidebar("tvSeries", "AIRING")
        self.assertEqual(result, {"data": "test"})
        mock_get.assert_called_once()

    @patch('rt_discovery_sidebar.requests.get')
    def test_fetch_discovery_sidebar_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError):
            rt_discovery_sidebar.fetch_discovery_sidebar("tvSeries", "AIRING")

    def test_iter_items_with_items(self):
        data = {"items": [{"title": "Item1"}, {"title": "Item2"}]}
        items = list(rt_discovery_sidebar.iter_items(data))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Item1")

    def test_iter_items_with_dict_items(self):
        data = {"items": [{"title": "Item1"}, {"title": "Item2"}]}
        items = list(rt_discovery_sidebar.iter_items(data))
        self.assertEqual(len(items), 2)

    def test_extract_titles(self):
        data = {"items": [{"title": "Test Title", "year": 2023}]}
        titles = rt_discovery_sidebar.extract_titles(data)
        self.assertEqual(len(titles), 1)
        self.assertEqual(titles[0]["title"], "Test Title")


if __name__ == '__main__':
    unittest.main()