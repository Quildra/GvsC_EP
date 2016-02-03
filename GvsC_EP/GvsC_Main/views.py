from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Event, SinglePlayerTournament

def index(request):
    upcoming_events = Event.objects.order_by('-start_date')
    context = {'upcoming_events': upcoming_events}
    return render(request, 'index.html', context)
