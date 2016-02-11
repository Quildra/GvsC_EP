from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Event, Tournament

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
    return render(request, 'tournaments/details.html', {'tournament': tournament})