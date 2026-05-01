from django.test import TestCase
from unittest.mock import patch, Mock
from .services import fetch_competitions, fetch_teams
from .services import fetch_scorers, fetch_standings
from django.urls import reverse
from .services import APITokenPool
from .services import fetch_players_by_league


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

class ViewTests(TestCase):

    @patch("tracker.views.fetch_competitions")
    def test_home_view_loads(self, mock_fetch):
        mock_fetch.return_value = []

        response = self.client.get(reverse("tracker:home"))

        self.assertEqual(response.status_code, 200)

    @patch("tracker.views.fetch_competitions")
    def test_rend_individual_view_loads(self, mock_fetch):
        mock_fetch.return_value = []

        response = self.client.get(reverse("tracker:league-detail"))

        self.assertEqual(response.status_code, 200)

    @patch("tracker.views.fetch_competitions")
    def test_datos_jugador_view_loads(self, mock_fetch):
        mock_fetch.return_value = []

        response = self.client.get(reverse("tracker:datos-jugador"))

        self.assertEqual(response.status_code, 200)

class ServiceErrorTests(TestCase):

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.requests.get")
    def test_fetch_competitions_error(self, mock_get, mock_token):
        mock_get.side_effect = Exception("API error")

        result = fetch_competitions()

        self.assertEqual(result, [])

class APITokenPoolTests(TestCase):

    def test_token_pool_rotates_tokens(self):
        pool = APITokenPool(["token1", "token2"])

        self.assertEqual(pool.get_token(), "token1")
        self.assertEqual(pool.get_token(), "token2")
        self.assertEqual(pool.get_token(), "token1")

class PlayerServiceTests(TestCase):

    @patch("tracker.services.token_pool.get_token", return_value="fake-token")
    @patch("tracker.services.fetch_teams")
    @patch("tracker.services.requests.get")
    def test_fetch_players_by_league(self, mock_get, mock_fetch_teams, mock_token):

        # Mock equipos
        mock_fetch_teams.return_value = [
            {"id": 1, "name": "Team A", "crest": "crest.png"}
        ]

        # Mock respuesta API jugadores
        mock_response = Mock()
        mock_response.json.return_value = {
            "squad": [
                {"id": 10, "name": "Player A"},
                {"id": 11, "name": "Player B"}
            ]
        }
        mock_get.return_value = mock_response

        players = fetch_players_by_league(2021)

        self.assertEqual(len(players), 2)
        self.assertEqual(players[0]["team_name"], "Team A")
        self.assertEqual(players[0]["team_crest"], "crest.png")

class ViewAdvancedTests(TestCase):

    @patch("tracker.views.fetch_teams")
    @patch("tracker.views.fetch_scorers")
    @patch("tracker.views.fetch_competitions")
    def test_home_view_with_league_parameter(
        self, mock_fetch_competitions, mock_fetch_scorers, mock_fetch_teams
    ):
        mock_fetch_competitions.return_value = [
            {
                "id": 2021,
                "name": "Premier League",
                "code": "PL",
                "currentSeason": {"startDate": "2025-08-01"},
            }
        ]

        mock_fetch_scorers.return_value = []
        mock_fetch_teams.return_value = []

        response = self.client.get("/tracker/home/?league=2021")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["selected_league"])