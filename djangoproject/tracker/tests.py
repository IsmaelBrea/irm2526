from django.test import TestCase
from unittest.mock import patch, Mock
from .services import fetch_competitions, fetch_teams


class ServiceBasicTests(TestCase):

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.requests.get")
    def test_fetch_competitions_returns_data(self, mock_get, mock_token):
        mock_response = Mock()
        mock_response.json.return_value = {
            "competitions": [{"id": 1, "name": "Test League"}]
        }
        mock_get.return_value = mock_response

        result = fetch_competitions()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test League")

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.requests.get")
    def test_fetch_teams_returns_data(self, mock_get, mock_token):
        mock_response = Mock()
        mock_response.json.return_value = {
            "teams": [{"id": 1, "name": "Team A"}]
        }
        mock_get.return_value = mock_response

        result = fetch_teams(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Team A")