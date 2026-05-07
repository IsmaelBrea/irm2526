from django.db import models
from django.contrib.auth.models import User


class League(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FavoriteTeam(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite_teams"
    )
    team_id = models.IntegerField()
    team_name = models.CharField(max_length=255)
    team_crest = models.URLField(blank=True, null=True)  # Agregar
    league_id = models.IntegerField(blank=True, null=True)  # Agregar
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "team_id")

    def __str__(self):
        return f"{self.user.username} - {self.team_name}"
