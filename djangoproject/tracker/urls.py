from django.urls import path

from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("test-api/", views.test_api, name="test_api"),
    path("leagues/", views.LeaguesView.as_view(), name="leagues"),
]
