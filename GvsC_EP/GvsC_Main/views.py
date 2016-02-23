from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.db.models import Max
import json

from .models import Event, Tournament, Match, SinglePlayerSeating

def index(request):
    upcoming_events = Event.objects.order_by('-start_date')
    context = {'upcoming_events': upcoming_events}
    return render(request, 'index.html', context)

def profile(request):
    #upcoming_events = Event.objects.order_by('-start_date')
    context = {}#{'upcoming_events': upcoming_events}
    return render(request, 'profile.html', context)

def events_index(request):
    upcoming_events = Event.objects.order_by('-start_date')
    context = {'upcoming_events': upcoming_events}
    return render(request, 'events/index.html', context)
    
def events_details(request, event_id):
    event = get_object_or_404(Event, pk = event_id)
    return render(request, 'events/details.html', {'event': event})

def tournaments_index(request):
    upcoming_tournaments = Tournament.objects.order_by('+id')
    context = {'upcoming_tournaments': upcoming_tournaments}
    return render(request, 'tournaments/index.html', context)
    
def tournaments_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk = tournament_id)
    num_rounds = tournament.match_set.all().aggregate(Max('round_number'))
    return render(request, 'tournaments/details.html', {'tournament': tournament, 'num_rounds': num_rounds['round_number__max'] })
    
def tournaments_next_round(request, tournament_id):
    if request.is_ajax():
        tournament = get_object_or_404(Tournament, pk = tournament_id)
        player_count = tournament.players.count()
        needs_a_bye = player_count % 2 == 1
        num_matches = int(player_count * 0.5)
        num_rounds = tournament.match_set.all().aggregate(Max('round_number'))
        
        next_round_number = 1 if num_rounds['round_number__max'] == None else num_rounds['round_number__max'] + 1
        
        plugin = tournament.game_plugin.get_plugin()
        pairings = plugin.PairRound(tournament)
        
        for i in range(num_matches):
            new_match = Match.objects.create(round_number=next_round_number, tournament=tournament, table_number=i, match_completed=False)
            SinglePlayerSeating.objects.create(seat_number=0, place=0, score=0, match=new_match, player=pairings[i][0]['player'])
            SinglePlayerSeating.objects.create(seat_number=1, place=0, score=0, match=new_match, player=pairings[i][1]['player'])
            

        html = render_to_string('tournaments/round_table.html', {'tournament': tournament, 'num_rounds': next_round_number, "needs_a_bye": needs_a_bye, "num_matches":num_matches})
        return HttpResponse(json.dumps({'html': mark_safe(html)}), content_type="application/json")