from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.db.models import Max
import json
import urllib.parse

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
    data = request.GET
    pairings_active = data.get('pa', False)
    
    return render(request, 'tournaments/details.html', {'tournament': tournament, 'num_rounds': num_rounds['round_number__max'], 'request':request, 'pairings_active':pairings_active})
    
def tournaments_next_round(request, tournament_id):
    if request.is_ajax():
        tournament = get_object_or_404(Tournament, pk = tournament_id)
        
        if not request.user.is_authenticated or not request.user.is_staff:
            html = render_to_string('tournaments/round_table.html', {'tournament': tournament})
            return HttpResponse(json.dumps({'html': mark_safe(html)}), content_type="application/json")
        
        player_count = tournament.players.count()
        needs_a_bye = player_count % 2 == 1
        num_matches = int(player_count * 0.5)
        num_rounds = tournament.match_set.all().aggregate(Max('round_number'))
        
        next_round_number = 1 if num_rounds['round_number__max'] == None else num_rounds['round_number__max'] + 1
        
        plugin = tournament.game_plugin.get_plugin()
        pairings = plugin.PairRound(tournament)
        
        for i in range(num_matches):
            new_match = Match.objects.create(round_number=next_round_number, tournament=tournament, table_number=i, match_completed=False)
            SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match, player=pairings[i][0]['player'])
            SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match, player=pairings[i][1]['player'])
            
        if needs_a_bye == True:
            new_match = Match.objects.create(round_number=next_round_number, tournament=tournament, table_number=num_matches, match_completed=True, is_bye=True)
            SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match, player=pairings[num_matches][0]['player'])            

        html = render_to_string('tournaments/round_table.html', {'tournament': tournament, 'num_rounds': next_round_number, "needs_a_bye": needs_a_bye, "num_matches":num_matches, 'request':request})
        print(html)
        return HttpResponse(json.dumps({'html': mark_safe(html)}), content_type="application/json")
    print("Not AJAX")
        
def tournaments_report_match_result(request, tournament_id):
    # Match PK
    # Seat 0 ID
    # Seat 0 Result
    # Seat 0 Score
    # Seat 1 ID
    # Seat 1 Result
    # Seat 1 Score
    data = request.POST
    match_id = data.get('match_id', 0)
    match = get_object_or_404(Match, pk = match_id)
    print(match)
    
    seat_0_id = data.get('seat_0_ID', 0)
    seat_0_result = data.get('seat_0_result', 0)
    seat_0_score = data.get('seat_0_score', 0)
    
    seat_1_id = data.get('seat_1_ID', 0)
    seat_1_result = data.get('seat_1_result', 0)
    seat_1_score = data.get('seat_1_score', 0)
    
    seat_0 = match.seating_set.filter(id=seat_0_id)
    print(seat_0)
    
    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'pa':True})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    print(full_redirect_url)
    return HttpResponseRedirect( full_redirect_url )
