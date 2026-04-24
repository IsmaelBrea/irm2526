import requests
import threading
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()


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
API_TOKENS_ENV = os.getenv("API_TOKENS", "")
TOKEN_LIST = API_TOKENS_ENV.split(",") if API_TOKENS_ENV else []
token_pool = APITokenPool(TOKEN_LIST)
BASE_URL = os.getenv("BASE_URL", "https://api.football-data.org/v4/")


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
    try:
        t_a_id, t_b_id = int(team_a_id), int(team_b_id)
        df_standings = pd.DataFrame(raw_data["standings"])

        # Selección de filas en la clasificación
        stats_a = df_standings[
            df_standings["team"].apply(lambda x: x["id"]) == t_a_id
        ].iloc[0]
        stats_b = df_standings[
            df_standings["team"].apply(lambda x: x["id"]) == t_b_id
        ].iloc[0]

        # Función auxiliar mejorada para obtener estadísticas y el DataFrame procesado
        def process_team_matches(matches, target_id):
            if not matches:
                return None, {
                    "avg_f": 0,
                    "avg_c": 0,
                    "cs": 0,
                    "form_pts": 0,
                    "form_str": "",
                    "eff": 0,
                }

            df = pd.DataFrame(matches)
            df["is_home"] = df["homeTeam"].apply(lambda x: x["id"] == target_id)

            # Goles Favor y Contra
            df["gf"] = df.apply(
                lambda r: (
                    r["score"]["fullTime"]["home"]
                    if r["is_home"]
                    else r["score"]["fullTime"]["away"]
                ),
                axis=1,
            )
            df["gc"] = df.apply(
                lambda r: (
                    r["score"]["fullTime"]["away"]
                    if r["is_home"]
                    else r["score"]["fullTime"]["home"]
                ),
                axis=1,
            )

            # Porterías a cero
            cs = int(df[df["gc"] == 0].shape[0])

            # Estado de forma (últimos 5)
            def calc_pts(r):
                win = r["score"]["winner"]
                if win == "DRAW":
                    return (1, "D")
                if (r["is_home"] and win == "HOME_TEAM") or (
                    not r["is_home"] and win == "AWAY_TEAM"
                ):
                    return (3, "W")
                return (0, "L")

            # Tomamos los 5 últimos partidos (los más recientes)
            last_5_matches = df.head(5)
            results = last_5_matches.apply(calc_pts, axis=1)
            pts_5 = sum([x[0] for x in results])
            str_5 = "".join([x[1] for x in results])

            # Efectividad
            if len(df) > 0:
                wins = df.apply(
                    lambda r: (
                        1
                        if (r["is_home"] and r["score"]["winner"] == "HOME_TEAM")
                        or (not r["is_home"] and r["score"]["winner"] == "AWAY_TEAM")
                        else 0
                    ),
                    axis=1,
                ).sum()
                eff = round((wins / len(df)) * 100, 1)
            else:
                eff = 0

            stats = {
                "avg_f": round(df["gf"].mean(), 2),
                "avg_c": round(df["gc"].mean(), 2),
                "cs": cs,
                "form_pts": pts_5,
                "form_str": str_5,
                "eff": eff,
            }
            return df, stats

        # Procesamos ambos equipos
        df_a, m_a = process_team_matches(raw_data["matches_a"], t_a_id)
        df_b, m_b = process_team_matches(raw_data["matches_b"], t_b_id)

        # ALGORITMO DE PROBABILIDAD: 35% puntos liga + 25% ataque + 15% defensa + 15% forma reciente + 5% porterías a cero + 5% efectividad
        def team_score(stats, m):
            return (
                (stats["points"] * 0.35)
                + (m["avg_f"] * 12 * 0.25)
                + ((3 - m["avg_c"]) * 10 * 0.15)
                + (m["form_pts"] * 0.15)
                + (m["cs"] * 0.05)
                + (m["eff"] * 0.05)
            )

        score_a = team_score(stats_a, m_a)
        score_b = team_score(stats_b, m_b)

        # Bonus por posición (mejora real del modelo)
        score_a += (20 - stats_a["position"]) * 0.2
        score_b += (20 - stats_b["position"]) * 0.2

        total = score_a + score_b

        # Evitar división rara
        if total <= 0:
            prob_a = 50
            prob_b = 50
        else:
            prob_a = round((score_a / total) * 100, 1)
            prob_b = round((score_b / total) * 100, 1)

        # ── DATOS PARA GRÁFICO DE LÍNEAS ──
        def build_form_chart(df, target_id):
            if df is None or df.empty:
                return []

            df["utcDate"] = pd.to_datetime(df["utcDate"])
            last5 = (
                df.sort_values("utcDate", ascending=False)
                .head(5)
                .iloc[::-1]
                .reset_index(drop=True)
            )

            result = []
            for i, row in last5.iterrows():
                home = row["homeTeam"]["name"]
                away = row["awayTeam"]["name"]
                gf = row["gf"]
                gc = row["gc"]
                win = row["score"]["winner"]
                is_home = row["is_home"]

                if win == "DRAW":
                    pts = 1
                elif (is_home and win == "HOME_TEAM") or (
                    not is_home and win == "AWAY_TEAM"
                ):
                    pts = 3
                else:
                    pts = 0

                result.append(
                    {
                        "jornada": f"J{i + 1}",
                        "rival": away if is_home else home,
                        "score": f"{int(gf)}-{int(gc)}",
                        "pts": pts,
                    }
                )

            return result

        form_a = build_form_chart(df_a, t_a_id)
        form_b = build_form_chart(df_b, t_b_id)

        # ── DATOS PARA GRÁFICO DE BARRAS ──
        bar_metrics = [
            {
                "metrica": "Puntos Liga",
                "val_a": int(stats_a["points"]),
                "val_b": int(stats_b["points"]),
            },
            {
                "metrica": "Goles Favor (AVG)",
                "val_a": m_a["avg_f"],
                "val_b": m_b["avg_f"],
            },
            {
                "metrica": "Goles Contra (AVG)",
                "val_a": m_a["avg_c"],
                "val_b": m_b["avg_c"],
            },
            {"metrica": "Porterías a cero", "val_a": m_a["cs"], "val_b": m_b["cs"]},
            {"metrica": "Efectividad (%)", "val_a": m_a["eff"], "val_b": m_b["eff"]},
        ]

        # Construcción de la tabla comparativa
        return {
            "team_a_prob": prob_a,
            "team_b_prob": prob_b,
            "comparison_table": [
                {
                    "metrica": "Posición",
                    "val_a": f"{stats_a['position']}º",
                    "val_b": f"{stats_b['position']}º",
                },
                {
                    "metrica": "Puntos Liga",
                    "val_a": int(stats_a["points"]),
                    "val_b": int(stats_b["points"]),
                },
                {
                    "metrica": "Goles a Favor (AVG)",
                    "val_a": f"{int(df_a['gf'].sum()) if df_a is not None else 0} ({m_a['avg_f']})",
                    "val_b": f"{int(df_b['gf'].sum()) if df_b is not None else 0} ({m_b['avg_f']})",
                },
                {
                    "metrica": "Goles en Contra (AVG)",
                    "val_a": f"{int(df_a['gc'].sum()) if df_a is not None else 0} ({m_a['avg_c']})",
                    "val_b": f"{int(df_b['gc'].sum()) if df_b is not None else 0} ({m_b['avg_c']})",
                },
                {
                    "metrica": "Porterías a cero",
                    "val_a": m_a["cs"],
                    "val_b": m_b["cs"],
                },
                {
                    "metrica": "Forma (Últimos 5P)",
                    "val_a": f"{m_a['form_pts']}pts",
                    "val_b": f"{m_b['form_pts']}pts",
                },
                {
                    "metrica": "Efectividad",
                    "val_a": f"{m_a['eff']}%",
                    "val_b": f"{m_b['eff']}%",
                },
            ],
            "form_a": form_a,
            "form_b": form_b,
            "bar_metrics": bar_metrics,
        }

    except Exception as e:
        print(f"Error Analytics: {e}")
        return {
            "team_a_prob": 50,
            "team_b_prob": 50,
            "comparison_table": [],
            "form_a": [],
            "form_b": [],
            "bar_metrics": [],
        }


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


def fetch_player_person(player_id):
    """Obtiene datos del jugador incluyendo competiciones actuales"""
    url = f"{BASE_URL}persons/{player_id}"
    headers = {"X-Auth-Token": token_pool.get_token()}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching player: {e}")
        return None


LEAGUE_ID_MAP = {
    2001: 107,  # Champions League
    2014: 1,  # Primera División
    2019: 7,  # Serie A
    2021: 10,  # Premier League
    2000: 136,  # Mundial
    2002: 8,  # Bundesliga
    2015: 16,  # Ligue 1
}


def fetch_matches_besoccer(league_id, round_num=None):
    """Obtiene partidos de una liga desde besoccerapps API"""
    besoccer_league_id = LEAGUE_ID_MAP.get(league_id)

    if not besoccer_league_id:
        return []

    api_key = os.getenv("BESOCCER_API_KEY")

    # Construir URL sin extra=png
    url = f"http://apiclient.besoccerapps.com/scripts/api/api.php?format=json&req=matchs&tz=Europe/Madrid&key={api_key}&league={besoccer_league_id}"

    if round_num:
        url += f"&round={round_num}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("match", [])
    except Exception as e:
        print(f"Error fetching matches from besoccer: {e}")
        return []
