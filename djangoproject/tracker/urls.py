from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("rend-individual", views.RendIndividualView.as_view(), name="league-detail"),
]
