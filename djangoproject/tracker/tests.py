from django.test import TestCase
from unittest.mock import patch, Mock
from .services import fetch_competitions, fetch_teams
from .services import fetch_scorers, fetch_standings


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

class ServiceAdvancedTests(TestCase):

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.requests.get")
    def test_fetch_scorers(self, mock_get, mock_token):
        mock_response = Mock()
        mock_response.json.return_value = {
            "scorers": [
                {"player": {"name": "Player A"}, "goals": 10}
            ]
        }
        mock_get.return_value = mock_response

        result = fetch_scorers("PL")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["player"]["name"], "Player A")

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.requests.get")
    def test_fetch_standings(self, mock_get, mock_token):
        mock_response = Mock()
        mock_response.json.return_value = {
            "standings": [
                {
                    "table": [
                        {"position": 1},
                        {"position": 2}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response

        result = fetch_standings("PL", "2025")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["position"], 1)