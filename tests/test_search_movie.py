import unittest

from ImdbDataExtraction.search_by_id.search_movie import format_movie_details


class CharacterCreditsTests(unittest.TestCase):
    def test_optional_characters_in_both_credit_outputs(self):
        for fields, expected in [
            ({}, []),
            ({"characters": None}, []),
            ({"characters": []}, []),
            ({"characters": [{"name": "Hero"}, {"name": "Narrator"}]},
             ["Hero", "Narrator"]),
        ]:
            with self.subTest(fields=fields):
                credit = {
                    "name": {"id": "nm0000001", "nameText": {"text": "Actor"}},
                    **fields,
                }
                result = format_movie_details({"data": {"title": {
                    "id": "tt39123235",
                    "principalCredits": [{
                        "category": {"text": "Stars"},
                        "credits": [credit],
                    }],
                }}})

                cast_credit = result["credits"]["Stars"][0]
                actor = result["enhanced_actors"][0]
                self.assertEqual(cast_credit["name"], "Actor")
                self.assertEqual(actor["name"], "Actor")
                self.assertEqual(cast_credit.get("characters", []), expected)
                self.assertEqual(actor["characters"], expected)
                if not expected:
                    self.assertNotIn("characters", cast_credit)


class RequestFailureTests(unittest.TestCase):
    def test_forbidden_response_has_actionable_error_and_timeout(self):
        import requests
        from unittest.mock import Mock, patch
        from ImdbDataExtraction.search_by_id import search_movie

        response = Mock(status_code=403)
        with patch.object(search_movie.requests, 'post', return_value=response) as post:
            with self.assertRaisesRegex(requests.HTTPError, 'HTTP 403 Forbidden') as error:
                search_movie.get_movie_details('tt39123235')
        self.assertIs(error.exception.response, response)
        self.assertEqual(post.call_args.kwargs['timeout'], 30)

    def test_cli_request_failure_returns_nonzero_without_saving(self):
        import io
        import requests
        from unittest.mock import patch
        from ImdbDataExtraction.search_by_id import search_movie

        with patch('sys.argv', ['search_movie.py', 'tt39123235']), \
             patch.object(search_movie, 'get_movie_details', side_effect=requests.HTTPError('HTTP 403 Forbidden')), \
             patch.object(search_movie, 'save_movie_data') as save, \
             patch('sys.stderr', new_callable=io.StringIO) as stderr, \
             patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(search_movie.main(), 1)
        save.assert_not_called()
        self.assertIn('HTTP 403 Forbidden', stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
