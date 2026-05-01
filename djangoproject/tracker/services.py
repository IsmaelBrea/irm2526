import requests
import threading
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import http.client
import json

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

            results = df.head(5).apply(calc_pts, axis=1)
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

            last5 = df.tail(5).reset_index(drop=True)

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
                "metrica": "Goles Favor (Total)",
                "val_a": int(df_a["gf"].sum()) if df_a is not None else 0,
                "val_b": int(df_b["gf"].sum()) if df_b is not None else 0,
            },
            {
                "metrica": "Goles Contra (Total)",
                "val_a": int(df_a["gc"].sum()) if df_a is not None else 0,
                "val_b": int(df_b["gc"].sum()) if df_b is not None else 0,
            },
            {"metrica": "Porterías a cero", "val_a": m_a["cs"], "val_b": m_b["cs"]},
            {"metrica": "Efectividad (%)", "val_a": m_a["eff"], "val_b": m_b["eff"]},
        ]

        # ── DATOS H2H: últimos encuentros directos entre ambos equipos ──
        def build_h2h(matches, ta_id, tb_id):
            if not matches:
                return []

            result = []
            for m in reversed(matches):  # más recientes primero
                try:
                    home_id = m["homeTeam"]["id"]
                    away_id = m["awayTeam"]["id"]

                    # Solo partidos entre EXACTAMENTE estos dos equipos
                    if {home_id, away_id} != {ta_id, tb_id}:
                        continue

                    home_name = m["homeTeam"]["name"]
                    away_name = m["awayTeam"]["name"]
                    score_h = m["score"]["fullTime"]["home"]
                    score_av = m["score"]["fullTime"]["away"]
                    winner = m["score"]["winner"]
                    date = m.get("utcDate", "")[:10]

                    res_status = "draw"
                    if winner == "HOME_TEAM":
                        res_status = "home"
                    elif winner == "AWAY_TEAM":
                        res_status = "away"

                    result.append(
                        {
                            "date": date,
                            "home": home_name,
                            "away": away_name,
                            "score": (
                                f"{score_h}-{score_av}"
                                if score_h is not None
                                else "?-?"
                            ),
                            "result": res_status,
                            "local_won": (winner == "HOME_TEAM" and home_id == ta_id)
                            or (winner == "AWAY_TEAM" and away_id == ta_id),
                        }
                    )

                    if len(result) >= 5:
                        break

                except KeyError:
                    continue

            return result

        h2h_matches = build_h2h(raw_data["h2h"], t_a_id, t_b_id)

        # Construcción de la tabla con Suma + (Media)
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
            "h2h_matches": h2h_matches,
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
            "h2h_matches": [],
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
            print(f"Error obteniendo equipo {team_id}: {e}")

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
        print(f"Error obteniendo jugador {player_id}: {e}")
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


def fetch_matches_besoccer(league_id, round_num=None, year=None):
    """Obtiene partidos de una liga desde besoccerapps API"""
    besoccer_league_id = LEAGUE_ID_MAP.get(league_id)

    if not besoccer_league_id:
        return []

    api_key = os.getenv("BESOCCER_API_KEY")

    url = f"http://apiclient.besoccerapps.com/scripts/api/api.php?format=json&req=matchs&tz=Europe/Madrid&key={api_key}&league={besoccer_league_id}"

    if year:
        url += f"&year={year}"

    if round_num:
        url += f"&round={round_num}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("match", [])
    except Exception as e:
        print(f"Error obteniendo partidos de besoccer: {e}")
        return []


LEAGUE_ID_MAPPING = {
    2001: 2,  # Champions League
    2014: 140,  # Primera División
    2019: 135,  # Serie A
    2021: 39,  # Premier League
    2000: 1,  # Mundial
    2002: 218,  # Bundesliga
    2015: 102,  # Ligue 1
}


def fetch_assists(league_id_football_data, season):
    """
    Obtiene los máximos asistentes usando API-Sports
    """
    league_id_apisports = LEAGUE_ID_MAPPING.get(league_id_football_data)

    if not league_id_apisports:
        return []

    api_key = os.getenv("APISPORTS_KEY", "")

    if not api_key:
        return []

    url = "https://v3.football.api-sports.io/players/topassists"
    headers = {"x-apisports-key": api_key}
    # El plan gratuito solo permite 2022-2024, así que usamos 2024
    params = {"season": "2024", "league": league_id_apisports}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        assists = data.get("response", [])
        return assists
    except Exception as e:
        print(f"Error fetching assists: {e}")
        return []


def fetch_red_cards(league_id_football_data, season):
    """
    Obtiene los máximos infractores (tarjetas rojas) usando API-Sports
    """
    league_id_apisports = LEAGUE_ID_MAPPING.get(league_id_football_data)

    if not league_id_apisports:
        return []

    api_key = os.getenv("APISPORTS_KEY", "")

    if not api_key:
        return []

    url = "https://v3.football.api-sports.io/players/topredcards"
    headers = {"x-apisports-key": api_key}
    params = {"season": "2024", "league": league_id_apisports}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        print(f"Error fetching red cards: {e}")
        return []


def fetch_yellow_cards(league_id_football_data, season):
    """
    Obtiene los máximos amonestados (tarjetas amarillas) usando API-Sports
    """
    league_id_apisports = LEAGUE_ID_MAPPING.get(league_id_football_data)

    if not league_id_apisports:
        return []

    api_key = os.getenv("APISPORTS_KEY", "")

    if not api_key:
        return []

    url = "https://v3.football.api-sports.io/players/topyellowcards"
    headers = {"x-apisports-key": api_key}
    params = {"season": "2024", "league": league_id_apisports}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        print(f"Error fetching yellow cards: {e}")
        return []


def merge_and_sort_infractions(red_cards_data, yellow_cards_data):
    """
    Merges red and yellow cards data and sorts by combined total (amarillas + rojas)
    """
    import pandas as pd

    if not red_cards_data or not yellow_cards_data:
        return red_cards_data if red_cards_data else []

    try:
        red_df = pd.DataFrame(
            [
                {
                    "player_id": card["player"]["id"],
                    "player": card["player"],
                    "statistics": card["statistics"],
                    "red": (
                        card["statistics"][0]["cards"]["red"]
                        if card.get("statistics")
                        else 0
                    ),
                    "yellow": (
                        card["statistics"][0]["cards"]["yellow"]
                        if card.get("statistics")
                        else 0
                    ),
                }
                for card in red_cards_data
            ]
        )

        yellow_df = pd.DataFrame(
            [
                {
                    "player_id": card["player"]["id"],
                    "yellow": (
                        card["statistics"][0]["cards"]["yellow"]
                        if card.get("statistics")
                        else 0
                    ),
                }
                for card in yellow_cards_data
            ]
        )

        merged = red_df.merge(
            yellow_df[["player_id", "yellow"]],
            on="player_id",
            how="left",
            suffixes=("_red", "_yellow"),
        )

        merged["yellow"] = merged["yellow_yellow"].fillna(merged["yellow_red"])

        merged["total_infractions"] = merged["red"] + merged["yellow"]

        merged = merged.sort_values("total_infractions", ascending=False).reset_index(
            drop=True
        )

        result = []
        for _, row in merged.iterrows():
            card_obj = {
                "player": row["player"],
                "statistics": row["statistics"],
            }
            # Update the cards data with the merged values
            if card_obj["statistics"]:
                card_obj["statistics"][0]["cards"]["yellow"] = int(row["yellow"])
                card_obj["statistics"][0]["cards"]["red"] = int(row["red"])
            result.append(card_obj)

        return result
    except Exception as e:
        print(f"Error merging infractions: {e}")
        return red_cards_data


def fetch_team_detail(team_id):
    """
    Obtiene la información detallada de un equipo usando el Pool de Tokens.
    """
    url = f"{BASE_URL}teams/{team_id}"

    headers = {"X-Auth-Token": token_pool.get_token()}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error IRM Engine - Detalle Equipo: {e}")
        return None


def fetch_team_matches(team_id):
    """Obtiene los últimos partidos del equipo para el análisis de forma (F4)"""
    url = f"{BASE_URL}teams/{team_id}/matches?status=FINISHED"
    headers = {"X-Auth-Token": token_pool.get_token()}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("matches", [])
        return []
    except Exception as e:
        print(f"Error al obtener partidos del equipo: {e}")
        return []


def fetch_matches_football_data(league_id, matchday=None, season=None):
    """Obtiene partidos de una liga desde football-data.org API"""

    url = f"{BASE_URL}competitions/{league_id}/matches"
    headers = {"X-Auth-Token": token_pool.get_token()}

    params = {}
    if season:
        params["season"] = season
    if matchday:
        params["matchday"] = matchday

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Transformar matches al formato esperado
        matches = []
        for match in data.get("matches", []):
            transformed_match = {
                "id": match.get("id"),
                "date": match.get("utcDate", "")[:10],
                "hour": (
                    match.get("utcDate", "")[11:13]
                    if "T" in match.get("utcDate", "")
                    else "00"
                ),
                "minute": (
                    match.get("utcDate", "")[14:16]
                    if "T" in match.get("utcDate", "")
                    else "00"
                ),
                "round": match.get("matchday"),
                "year": (
                    int(match.get("season", {}).get("startDate", "")[:4])
                    if match.get("season", {}).get("startDate")
                    else None
                ),
                "total_rounds": match.get("season", {}).get("currentMatchday", 0),
                "local": match.get("homeTeam", {}).get("name"),
                "visitor": match.get("awayTeam", {}).get("name"),
                "local_shield": match.get("homeTeam", {}).get("crest"),
                "visitor_shield": match.get("awayTeam", {}).get("crest"),
                "local_goals": match.get("score", {}).get("fullTime", {}).get("home"),
                "visitor_goals": match.get("score", {}).get("fullTime", {}).get("away"),
                "status": match.get("status"),
                "odds": {},  # Inicializar vacío
            }
            if transformed_match["local_goals"] is None:
                transformed_match["local_goals"] = "x"
            if transformed_match["visitor_goals"] is None:
                transformed_match["visitor_goals"] = "x"

            matches.append(transformed_match)

        # Enriquecer con odds
        odds_list = fetch_odds(league_id)
        matches = match_odds_to_matches(matches, odds_list)

        return matches

    except Exception as e:
        print(f"Error fetching matches from football-data: {e}")
        return []


SPORT_KEY_MAPPING = {
    2001: "soccer_uefa_champs_league",
    2014: "soccer_spain_la_liga",
    2019: "soccer_italy_serie_a",
    2021: "soccer_epl",
    2000: "soccer_fifa_world_cup",
    2002: "soccer_germany_bundesliga",
    2015: "soccer_france_ligue_one",
}


def fetch_odds(league_id):
    """Obtiene odds de partidos desde The Odds API"""
    sport_key = SPORT_KEY_MAPPING.get(league_id)
    if not sport_key:
        return []

    api_key = os.getenv("ODDS_API_KEY", "")
    if not api_key:
        print("Warning: ODDS_API_KEY no está configurada")
        return []

    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {"regions": "eu", "markets": "h2h", "apiKey": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # La API devuelve un diccionario con key "events"
        if isinstance(data, dict):
            events = data.get("events", [])
        elif isinstance(data, list):
            events = data  # Si es una lista directa
        else:
            events = []

        return events
    except Exception as e:
        print(f"Error fetching odds: {e}")
        import traceback

        traceback.print_exc()
        return []


def get_team_keywords(name):
    """Extrae palabras clave del nombre eliminando ruido"""
    name = name.lower().strip()

    # Palabras a ignorar (prefijos/sufijos)
    stop_words = {"rcd", "ca", "ad", "ud", "cf", "fc", "bsc", "sd", "de", "the"}

    # Dividir en palabras y filtrar
    words = [w for w in name.split() if w not in stop_words]

    return set(words)  # Retornar como conjunto para comparar fácil


def match_odds_to_matches(matches, odds_list):
    """Matchea odds con fuzzy matching por palabras clave"""

    for match in matches:
        match_date = match.get("date")
        local = match.get("local", "").lower().strip()
        visitor = match.get("visitor", "").lower().strip()

        local_keywords = get_team_keywords(local)
        visitor_keywords = get_team_keywords(visitor)

        best_odd = None

        for odd in odds_list:
            odd_date = odd.get("commence_time", "")[:10]
            home = odd.get("home_team", "").lower().strip()
            away = odd.get("away_team", "").lower().strip()

            if match_date == odd_date:
                home_keywords = get_team_keywords(home)
                away_keywords = get_team_keywords(away)

                # Buscar si comparten palabras clave significativas
                local_match = len(local_keywords & home_keywords) > 0
                visitor_match = len(visitor_keywords & away_keywords) > 0

                if local_match and visitor_match:

                    best_odd = odd
                    break

        if best_odd:
            all_odds = []
            for bookmaker in best_odd.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market.get("key") == "h2h":
                        outcomes = market.get("outcomes", [])
                        odds_dict = {o.get("name"): o.get("price") for o in outcomes}

                        # Buscar outcomes por palabras clave
                        home_odd = next(
                            (
                                v
                                for k, v in odds_dict.items()
                                if len(get_team_keywords(k) & home_keywords) > 0
                            ),
                            None,
                        )
                        draw_odd = odds_dict.get("Draw")
                        away_odd = next(
                            (
                                v
                                for k, v in odds_dict.items()
                                if len(get_team_keywords(k) & away_keywords) > 0
                            ),
                            None,
                        )

                        if home_odd and draw_odd and away_odd:
                            all_odds.append(
                                {
                                    "home": home_odd,
                                    "draw": draw_odd,
                                    "away": away_odd,
                                    "bookmaker": bookmaker.get("title", "N/A"),
                                }
                            )

            if all_odds:
                match["odds"] = all_odds

    return matches


def get_coords_from_address(address):
    if not address or address == "—":
        return None

    # Limpiamos un poco la dirección quitando códigos postales raros si fuera necesario
    api_key = os.getenv("GEOCODING_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(address)}&key={api_key}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data["status"] == "OK":
            return data["results"][0]["geometry"]["location"]
        else:
            print(
                f"DEBUG MAPA: Google respondió {data['status']} para la dirección: {address}"
            )
    except Exception as e:
        print(f"DEBUG MAPA: Error de conexión: {e}")
    return None
