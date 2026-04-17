from django.views import generic
from .services import fetch_competitions, fetch_teams, fetch_scorers

class HomeView(generic.TemplateView):
    template_name = "tracker/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos competiciones
        all_leagues = fetch_competitions()
        
        # IDs del anteproyecto 
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league['id'] in target_ids]
        context['leagues'] = leagues
        
        # Gestionamos selección (Funcionalidad F1) 
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
            
            # Si hay liga, traemos equipos (Funcionalidad F2) 
            context['teams'] = fetch_teams(selected_league_id)
        
        context['selected_league'] = selected_league
        context['scorers'] = scorers
        return context
    

class RendIndividualView(generic.TemplateView):
    template_name = "tracker/rend_indiv.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtenemos competiciones
        all_leagues = fetch_competitions()
        
        # IDs del anteproyecto 
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        leagues = [league for league in all_leagues if league['id'] in target_ids]
        context['leagues'] = leagues
        
        # Gestionamos selección (Funcionalidad F1) 
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
            
            # Si hay liga, traemos equipos (Funcionalidad F2) 
            context['teams'] = fetch_teams(selected_league_id)
        
        context['selected_league'] = selected_league
        context['scorers'] = scorers

        return context