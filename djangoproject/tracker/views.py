from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import JsonResponse
from .services import fetch_team_stats
from .services import fetch_competitions


from .models import Choice, League, Question


class IndexView(generic.ListView):
    template_name = "tracker/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]

class DetailView(generic.DetailView):
    model = Question
    template_name = "tracker/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "tracker/results.html"
    
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "tracker/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("tracker:results", args=(question.id,)))


def test_api(request):
    """
    Función exacta para comprobar el Requisito F13 (Conexión API).
    """
    # Probamos con el ID 33 (Manchester United)
    data = fetch_team_stats(team_id=33)
    
    if data:
        # Esto imprimirá en la consola de tu terminal qué token se usó
        return JsonResponse({
            "status": "success",
            "message": "Conexión establecida correctamente",
            "data": data
        })
    else:
        return JsonResponse({
            "status": "error", 
            "message": "Error al conectar con API-Football. Revisa tus Keys."
        }, status=500)
    
class LeaguesView(generic.TemplateView):
    template_name = "tracker/leagues.html"
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        leagues = fetch_competitions()
        context['leagues'] = fetch_competitions()
        selected_league_id = self.request.GET.get('league')
        selected_league = None
        
        if selected_league_id:
            for league in leagues:
                if str(league['id']) == selected_league_id:
                    selected_league = league
                    break
        
        context['selected_league'] = selected_league
        return context