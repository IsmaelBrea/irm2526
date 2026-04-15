from django.views import generic
from .services import fetch_competitions

class LeaguesView(generic.TemplateView):
    template_name = "tracker/leagues.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Obtenemos todas las competiciones de la API [cite: 16, 17]
        all_leagues = fetch_competitions()
        
        # 2. Definimos los IDs de las competiciones según el anteproyecto 
        # Champions (2001), Mundial (2000), Premier (2021), LaLiga (2014), 
        # Serie A (2019), Bundesliga (2002), Ligue 1 (2015)
        target_ids = [2001, 2000, 2021, 2014, 2019, 2002, 2015]
        
        # 3. Filtramos para quedarnos solo con las elegidas [cite: 17, 18]
        leagues = [league for league in all_leagues if league['id'] in target_ids]
        context['leagues'] = leagues
        
        # 4. Gestionamos la liga seleccionada por el usuario 
        selected_league_id = self.request.GET.get('league')
        selected_league = None
        
        if selected_league_id:
            for league in leagues:
                if str(league['id']) == selected_league_id:
                    selected_league = league
                    break
        
        context['selected_league'] = selected_league
        return context