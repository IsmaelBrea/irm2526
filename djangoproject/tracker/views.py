
from django.views import generic

from .services import fetch_competitions, fetch_scorers

class LeaguesView(generic.TemplateView):
    template_name = "tracker/leagues.html"
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        leagues = fetch_competitions()
        context['leagues'] = fetch_competitions()
        selected_league_id = self.request.GET.get('league')
        selected_league = None
        scorers = []
        
        if selected_league_id:
            for league in leagues:
                if str(league['id']) == selected_league_id:
                    selected_league = league
                    season = selected_league['currentSeason']['startDate'][:4]

                    scorers = fetch_scorers(league['code'], season)

                    break



        context['selected_league'] = selected_league
        context['scorers'] = scorers
        return context