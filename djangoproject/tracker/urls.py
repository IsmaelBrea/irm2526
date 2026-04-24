from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path(
        "compare/<int:league_id>/<int:team_a_id>/<int:team_b_id>/",
        views.compare_teams,
        name="compare_teams",
    ),
    path("rend-individual/", views.RendIndividualView.as_view(), name="league-detail"),
    path("datos-jugador/", views.DatosJugadorView.as_view(), name="datos-jugador"),
    path(
        "api/player-stats/",
        views.get_player_stats,
        name="get_player_stats",
    ),
]
