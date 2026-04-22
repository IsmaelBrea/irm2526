import requests
import threading
import pandas as pd
import numpy as np


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


# Obtiene datos de ambos equipos
def fetch_performance_data(team_a_id, team_b_id, league_id):
    """
    Recopila los datos numéricos y deportivos para la comparativa de Pandas
    """
    headers = {"X-Auth-Token": token_pool.get_token()}

    # CLASIFICACIÓN (Para comparar posición, puntos y diferencia de goles actual)
    url_standings = f"{BASE_URL}competitions/{league_id}/standings"

    # PARTIDOS (Para calcular medias de goles y rachas)
    url_matches_a = f"{BASE_URL}teams/{team_a_id}/matches?status=FINISHED"
    url_matches_b = f"{BASE_URL}teams/{team_b_id}/matches?status=FINISHED"

    # DUELOS DIRECTOS (H2H)
    url_h2h = (
        f"{BASE_URL}teams/{team_a_id}/matches?competitors={team_b_id}&status=FINISHED"
    )

    raw_data = {"standings": [], "matches_a": [], "matches_b": [], "h2h": []}

    try:
        # Peticiones en paralelo o secuenciales usando el pool de tokens
        res_s = requests.get(url_standings, headers=headers)
        res_ma = requests.get(url_matches_a, headers=headers)
        res_mb = requests.get(url_matches_b, headers=headers)
        res_h2h = requests.get(url_h2h, headers=headers)

        if res_s.status_code == 200:
            # Extraemos solo la tabla general
            raw_data["standings"] = (
                res_s.json().get("standings", [{}])[0].get("table", [])
            )

        if res_ma.status_code == 200:
            raw_data["matches_a"] = res_ma.json().get("matches", [])

        if res_mb.status_code == 200:
            raw_data["matches_b"] = res_mb.json().get("matches", [])

        if res_h2h.status_code == 200:
            raw_data["h2h"] = res_h2h.json().get("matches", [])

    except Exception as e:
        print(f"Error en IRM Engine - Data Fetch: {e}")

    return raw_data


# Usar pandas para análisis de datos
def calculate_irm_probability(raw_data, team_a_id, team_b_id):
    """
    Procesa los datos con Pandas para calcular porcentajes de victoria
    """
    try:
        # Clasificación
        df_standings = pd.DataFrame(raw_data["standings"])
        stats_a = df_standings[
            df_standings["team"].apply(lambda x: x["id"]) == int(team_a_id)
        ].iloc[0]
        stats_b = df_standings[
            df_standings["team"].apply(lambda x: x["id"]) == int(team_b_id)
        ].iloc[0]

        # Goles (Últimos partidos)
        def get_avg_goals(matches):
            if not matches:
                return 0
            df = pd.DataFrame(matches)
            # Extraer goles totales del partido
            df["total_goals"] = df["score"].apply(
                lambda x: x["fullTime"]["home"] + x["fullTime"]["away"]
            )
            return df["total_goals"].mean()

        avg_a = get_avg_goals(raw_data["matches_a"])
        avg_b = get_avg_goals(raw_data["matches_b"])

        # Pesos del Algoritmo IRM (F17)
        # Puntos (40%) + Goles (40%) + Factor Campo/Azar (20%)
        score_a = (stats_a["points"] * 0.4) + (avg_a * 10 * 0.4) + 10  # Base neutral
        score_b = (stats_b["points"] * 0.4) + (avg_b * 10 * 0.4) + 10

        total = score_a + score_b
        return {
            "team_a": round((score_a / total) * 100, 1),
            "team_b": round((score_b / total) * 100, 1),
            "raw_stats": {
                "points_a": int(stats_a["points"]),
                "points_b": int(stats_b["points"]),
                "goals_avg_a": round(avg_a, 2),
                "goals_avg_b": round(avg_b, 2),
            },
        }
    except Exception as e:
        print(f"Error Analytics: {e}")
        return {"team_a": 50, "team_b": 50}


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
