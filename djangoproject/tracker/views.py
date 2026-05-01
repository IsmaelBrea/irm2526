from multiprocessing import context
import os
from django.views import generic
from django.http import JsonResponse
from urllib3 import request
from .services import (
    fetch_competitions,
    fetch_player_person,
    fetch_teams,
    fetch_scorers,
    fetch_competitions,
    fetch_teams,
    fetch_scorers,
    fetch_standings,
    fetch_performance_data,
    fetch_standings,
    fetch_players_by_league,
    calculate_irm_probability,
    fetch_matches_football_data,
    fetch_assists,
    fetch_red_cards,
    fetch_yellow_cards,
    merge_and_sort_infractions,
    fetch_team_detail,
    fetch_team_matches,
    get_coords_from_address,
)
import pandas as pd
from datetime import datetime

NATIONALITY_TO_ISO = {
    "Germany": "de",
    "Spain": "es",
    "France": "fr",
    "England": "gb-eng",
    "Italy": "it",
    "Portugal": "pt",
    "Netherlands": "nl",
    "Belgium": "be",
    "Brazil": "br",
    "Argentina": "ar",
    "Uruguay": "uy",
    "Colombia": "co",
    "Croatia": "hr",
    "Poland": "pl",
    "Denmark": "dk",
    "Sweden": "se",
    "Norway": "no",
    "Austria": "at",
    "Switzerland": "ch",
    "Morocco": "ma",
    "Senegal": "sn",
    "Nigeria": "ng",
    "Ghana": "gh",
    "Ivory Coast": "ci",
    "Japan": "jp",
    "South Korea": "kr",
    "USA": "us",
    "Mexico": "mx",
    "Chile": "cl",
    "Ecuador": "ec",
    "Paraguay": "py",
    "Serbia": "rs",
    "Czech Republic": "cz",
    "Slovakia": "sk",
    "Hungary": "hu",
    "Romania": "ro",
    "Turkey": "tr",
    "Greece": "gr",
    "Ukraine": "ua",
    "Russia": "ru",
    "Wales": "gb-wls",
    "Scotland": "gb-sct",
    "Ireland": "ie",
    "Algeria": "dz",
    "Tunisia": "tn",
    "Cameroon": "cm",
    "Australia": "au",
    "New Zealand": "nz",
    "Costa Rica": "cr",
    "Panama": "pa",
    "Senegal": "sn",
    "Morocco": "ma",
    "Angola": "ao",
    "Gabon": "ga",
    "DR Congo": "cd",
    "Ivory Coast": "ci",
    "Ghana": "gh",
    "Cameroon": "cm",
    "Nigeria": "ng",
    "Japan": "jp",
    "South Korea": "kr",
    "Czech Republic": "cz",
    "Burkina Faso": "bf",
    "Mali": "ml",
    "Kosovo": "xk",
    "Iceland": "is",
    "Bosnia-Herzegovina": "ba",
    "Ivory Coast": "ci",
    "Turkey": "tr",
    "Togo": "tg",
    "Estonia": "ee",
    "Bulgaria": "bg",
    "Serbia": "rs",
    "Slovakia": "sk",
    "Hungary": "hu",
    "Romania": "ro",
}


class HomeView(generic.TemplateView):
    template_name = "tracker/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenemos competiciones
        all_leagues = fetch_competitions()

        # IDs del anteproyecto
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league["id"] in target_ids]
        context["leagues"] = leagues

        # Gestionamos selección (Funcionalidad F1)
        selected_league_id = self.request.GET.get("league")
        selected_league = None
        scorers = []

        if selected_league_id:
            for league in leagues:
                if str(league["id"]) == selected_league_id:
                    selected_league = league
                    season = selected_league["currentSeason"]["startDate"][:4]

                    scorers = fetch_scorers(league["code"], season)

                    break

            # Si hay liga, traemos equipos (Funcionalidad F2)
            context["teams"] = fetch_teams(selected_league_id)

        context["selected_league"] = selected_league
        context["scorers"] = scorers
        return context


def compare_teams(request, league_id, team_a_id, team_b_id):
    """
    Vista que une el Service (API) con el Analytics (Pandas)
    Responde en formato JSON para que el JS actualice la interfaz sin recargar.
    """
    try:
        # Obtenemos datos masivos de la API
        raw_data = fetch_performance_data(team_a_id, team_b_id, league_id)

        # Procesa con Pandas
        analysis_results = calculate_irm_probability(raw_data, team_a_id, team_b_id)

        # Respuesta de éxito
        return JsonResponse({"status": "success", "data": analysis_results})

    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Error en el motor IRM Engine: {str(e)}"},
            status=500,
        )


class RendIndividualView(generic.TemplateView):
    template_name = "tracker/rend_indiv.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtenemos competiciones
        all_leagues = fetch_competitions()

        # IDs del anteproyecto
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league["id"] in target_ids]
        context["leagues"] = leagues

        # Gestionamos selección (Funcionalidad F1)
        selected_league_id = self.request.GET.get("league")
        selected_league = None
        scorers = []
        standings = []
        assists = []
        total_cards = []

        if selected_league_id:
            for league in leagues:
                if str(league["id"]) == selected_league_id:
                    selected_league = league
                    season = selected_league["currentSeason"]["startDate"][:4]

                    scorers = fetch_scorers(league["code"], season)

                    assists = fetch_assists(int(selected_league_id), season)

                    standings = fetch_standings(league["code"], season)

                    yellow_cards = fetch_yellow_cards(int(selected_league_id), season)
                    red_cards_raw = fetch_red_cards(int(selected_league_id), season)
                    total_cards = merge_and_sort_infractions(
                        red_cards_raw, yellow_cards
                    )

                    break

            context["teams"] = fetch_teams(selected_league_id)

        context["selected_league"] = selected_league
        context["scorers"] = scorers
        context["assists"] = assists
        context["standings"] = standings
        context["total_cards"] = total_cards
        return context


class DatosJugadorView(generic.TemplateView):
    template_name = "tracker/datos_jugador.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_leagues = fetch_competitions()
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league["id"] in target_ids]
        context["leagues"] = leagues

        selected_league_id = self.request.GET.get("league")
        selected_league = None
        players = []

        if selected_league_id:
            for league in leagues:
                if str(league["id"]) == selected_league_id:
                    selected_league = league
                    context["teams"] = fetch_teams(selected_league_id)
                    players = fetch_players_by_league(selected_league_id)
                    break

        context["selected_league"] = selected_league
        context["players"] = players
        return context


def get_player_stats(request):
    """Retorna competiciones del jugador"""
    player_id = request.GET.get("player_id")

    if not player_id:
        return JsonResponse(
            {"status": "error", "message": "player_id required"}, status=400
        )

    try:
        data = fetch_player_person(player_id)

        if data is None:
            return JsonResponse(
                {"status": "error", "message": "No se pudieron obtener los datos"},
                status=500,
            )

        return JsonResponse({"status": "success", "data": data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def get_league_matches(request):
    """Retorna partidos de una liga"""
    league_id = request.GET.get("league_id")
    round_num = request.GET.get("round")
    year = request.GET.get("year")

    if not league_id:
        return JsonResponse(
            {"status": "error", "message": "league_id required"}, status=400
        )

    try:
        league_id = int(league_id)
        matches = fetch_matches_football_data(
            league_id, matchday=round_num, season=year
        )
        return JsonResponse({"status": "success", "data": matches})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


class PartidosView(generic.TemplateView):
    template_name = "tracker/partidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_leagues = fetch_competitions()
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league["id"] in target_ids]
        context["leagues"] = leagues

        selected_league_id = self.request.GET.get("league")
        selected_league = None

        if selected_league_id:
            for league in leagues:
                if str(league["id"]) == selected_league_id:
                    selected_league = league
                    break

        context["selected_league"] = selected_league
        return context


# tracker/views.py


class AnalisisAvanzadoView(generic.TemplateView):
    template_name = "tracker/analisis_avanzado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_leagues = fetch_competitions()
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        context["leagues"] = [l for l in all_leagues if l["id"] in target_ids]

        league_id = self.request.GET.get("league")
        team_id = self.request.GET.get("team")

        if league_id:
            context["teams"] = fetch_teams(league_id)
            context["selected_league_id"] = league_id
            # Recuperar objeto de la liga seleccionada para la cabecera
            for l in all_leagues:
                if str(l["id"]) == str(league_id):
                    context["selected_league"] = l
                    break

        if team_id:
            team_detail = fetch_team_detail(team_id)
            matches_raw = fetch_team_matches(team_id)

            if team_detail and matches_raw:
                # 1. LOCALIZACIÓN
                address = team_detail.get("address")
                context["team_coords"] = get_coords_from_address(address)
                context["maps_js_key"] = os.getenv("MAPS_JS_API_KEY")

                # 2. PROCESAMIENTO DE PARTIDOS (PANDAS)
                df_matches = pd.DataFrame(matches_raw)
                df_matches["goals_for"] = df_matches.apply(
                    lambda x: (
                        x["score"]["fullTime"]["home"]
                        if str(x["homeTeam"]["id"]) == str(team_id)
                        else x["score"]["fullTime"]["away"]
                    ),
                    axis=1,
                )
                df_matches["goals_against"] = df_matches.apply(
                    lambda x: (
                        x["score"]["fullTime"]["away"]
                        if str(x["homeTeam"]["id"]) == str(team_id)
                        else x["score"]["fullTime"]["home"]
                    ),
                    axis=1,
                )

                context["stats"] = {
                    "avg_goals_for": round(df_matches["goals_for"].tail(5).mean(), 2),
                    "avg_goals_against": round(
                        df_matches["goals_against"].tail(5).mean(), 2
                    ),
                    "total_matches": len(df_matches),
                }
                context["recent_matches"] = matches_raw[-10:]

                # 3. PROCESAMIENTO DE PLANTILLA Y BANDERAS (CRÍTICO)
                squad_data = team_detail.get("squad", [])
                if squad_data:
                    df_squad = pd.DataFrame(squad_data)

                    # Mapear códigos de banderas
                    df_squad["flag_code"] = (
                        df_squad["nationality"]
                        .fillna("")
                        .map(lambda n: NATIONALITY_TO_ISO.get(n, "").lower())
                    )

                    # Ordenar posiciones
                    pos_order = {
                        "Goalkeeper": 0,
                        "Defence": 1,
                        "Midfield": 2,
                        "Offence": 3,
                    }
                    df_squad["pos_idx"] = df_squad["position"].map(pos_order).fillna(4)
                    df_squad = df_squad.sort_values("pos_idx")

                    context["squad"] = df_squad.to_dict("records")

                context["team"] = team_detail

        return context
