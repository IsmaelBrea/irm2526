import requests
import threading


class APITokenPool:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.lock = threading.Lock()

    def get_token(self):
        with self.lock:
            token = self.tokens[self.index]
            self.index = (self.index + 1) % len(self.tokens)
            return token


# API Keys
TOKEN_LIST = ["0ba4247e00a64c0cab971f5c657d831f", "ff76024905da41f48054d031227c3804"]
token_pool = APITokenPool(TOKEN_LIST)
BASE_URL = "https://api.football-data.org/v4/"


# Obtener ligas
def fetch_competitions():
    url = f"{BASE_URL}competitions/"
    headers = {"X-Auth-Token": token_pool.get_token()}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get("competitions", [])
    except Exception as e:
        print(f"Error en competiciones: {e}")
        return []


# Obtener equipos de la liga seleccionada
def fetch_teams(league_id):
    url = f"{BASE_URL}competitions/{league_id}/teams"
    headers = {"X-Auth-Token": token_pool.get_token()}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("teams", [])
    except Exception as e:
        print(f"Error al consultar equipos: {e}")
        return []


def fetch_scorers(league_code, season=None):
    """
    Obtiene los máximos goleadores de una competición
    """
    url = f"https://api.football-data.org/v4/competitions/{league_code}/scorers"
    headers = {"X-Auth-Token": token_pool.get_token()}

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if "scorers" in data:
            return data["scorers"]
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def fetch_standings(league_code, season):
    """
    Obtiene la clasificación actual de una competición
    """
    url = f"https://api.football-data.org/v4/competitions/{league_code}/standings"
    headers = {"X-Auth-Token": token_pool.get_token()}
    params = {"season": season}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Obtener la tabla del primer stage (REGULAR_SEASON)
        if "standings" in data and len(data["standings"]) > 0:
            return data["standings"][0].get("table", [])
        return []
    except Exception as e:
        print(f"Error al consultar clasificación: {e}")
        return []


def fetch_players_by_league(league_id):
    """Obtiene todos los jugadores de todos los equipos de una liga"""
    teams = fetch_teams(league_id)
    players = []

    for team in teams:
        team_id = team.get("id")
        url = f"{BASE_URL}teams/{team_id}"
        headers = {"X-Auth-Token": token_pool.get_token()}

        try:
            response = requests.get(url, headers=headers)
            team_data = response.json()
            squad = team_data.get("squad", [])

            for player in squad:
                player["team_name"] = team.get("name")
                player["team_crest"] = team.get("crest")
                players.append(player)
        except Exception as e:
            print(f"Error fetching team {team_id}: {e}")

    return players
