from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.db.models import Max
import json
import urllib.parse

from .models import Event, Tournament, Match, SinglePlayerSeating, Player, TournamentParticipant, TournamentParticipantOpponent
import GvsC_Main.errors


def index(request):
    upcoming_events = Event.objects.order_by('-start_date')
    context = {'upcoming_events': upcoming_events}
    return render(request, 'index.html', context)


def profile(request):
    # upcoming_events = Event.objects.order_by('-start_date')
    context = {}  # {'upcoming_events': upcoming_events}
    return render(request, 'profile.html', context)


def events_index(request):
    upcoming_events = Event.objects.order_by('-start_date')
    context = {'upcoming_events': upcoming_events}
    return render(request, 'events/index.html', context)


def events_details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'events/details.html', {'event': event})


def tournaments_index(request):
    upcoming_tournaments = Tournament.objects.order_by('+id')
    context = {'upcoming_tournaments': upcoming_tournaments}
    return render(request, 'tournaments/index.html', context)


def tournaments_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    num_rounds = tournament.match_set.all().aggregate(Max('round_number'))
    enrolled_players = []
    for participant in tournament.tournamentparticipant_set.all():
        enrolled_players.append(participant.player.pk)
    not_enrolled_players = Player.objects.exclude(pk__in=enrolled_players)
    data = request.GET
    tab = data.get('tab', "standings")

    return render(request, 'tournaments/details.html',
                  {'tournament': tournament, 'num_rounds': num_rounds['round_number__max'], 'request': request,
                   'active_tab': tab, 'not_enrolled_players': not_enrolled_players})


def record_match_result(match_pk, seat_0_pk, seat_0_result, seat_0_score, seat_1_pk, seat_1_result, seat_1_score,
                        was_a_bye):
    match = get_object_or_404(Match, pk=match_pk)

    if was_a_bye:
        plugin = match.tournament.game_plugin.get_plugin()
        seat_0 = match.seating_set.get(pk=seat_0_pk)
        seat_0.result_option = plugin.get_bye_result()
        seat_0.score = plugin.get_bye_score()
        seat_0.save()
    else:
        seat_0 = match.seating_set.get(pk=seat_0_pk)
        seat_1 = match.seating_set.get(pk=seat_1_pk)

        seat_0.result_option = seat_0_result
        seat_0.score = seat_0_score

        seat_1.result_option = seat_1_result
        seat_1.score = seat_1_score

        plugin = match.tournament.game_plugin.get_plugin()
        plugin.DetermineWinner(seat_0, seat_1)

        seat_0.save()
        seat_1.save()

    match.match_completed = True
    match.save()


def tournaments_next_round(request, tournament_id):
    if request.is_ajax():
        tournament = get_object_or_404(Tournament, pk=tournament_id)

        if not request.user.is_authenticated or not request.user.is_staff:
            html = render_to_string('tournaments/round_table.html', {'tournament': tournament})
            return HttpResponse(json.dumps({'html': mark_safe(html)}), content_type="application/json")

        current_round_number = tournament.get_current_round()
        next_round_number = current_round_number + 1

        # If we are not on the first round then make sure all the matches from the current round are complete.
        if current_round_number > 0:
            unfinished_matches = []
            all_matches_complete = True
            for match in Match.objects.filter(tournament=tournament, round_number=current_round_number):
                if not match.match_completed:
                    all_matches_complete = False
                    unfinished_matches.append(match)

            if not all_matches_complete:
                error = GvsC_Main.errors.error_lookup(GvsC_Main.errors.ERROR_NOT_ALL_RESULTS_IN)
                for match in unfinished_matches:
                    error += match.seating_set.first().player.player.name() + ' Vs ' + match.seating_set.last().player.player.name() + '<br>'

                return HttpResponse(json.dumps({'error': mark_safe(error)}), content_type="application/json")

        player_count = tournament.tournamentparticipant_set.filter(dropped=False).count()
        needs_a_bye = player_count % 2 == 1
        num_matches = int(player_count * 0.5)

        plugin = tournament.game_plugin.get_plugin()
        ret, pairings = plugin.PairRound(tournament)

        if ret != GvsC_Main.errors.ERROR_OK:
            return HttpResponse(json.dumps({'error': mark_safe(GvsC_Main.errors.error_lookup(ret))}), content_type="application/json")

        for i in range(num_matches):
            new_match = Match.objects.create(round_number=next_round_number, tournament=tournament, table_number=i,
                                             match_completed=False)
            SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match,
                                               player=pairings[i][0]['player'])
            SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match,
                                               player=pairings[i][1]['player'])
            TournamentParticipantOpponent.objects.create(current_player=pairings[i][0]['player'],
                                                         opponent_player=pairings[i][1]['player'],
                                                         round_number=next_round_number)
            TournamentParticipantOpponent.objects.create(current_player=pairings[i][1]['player'],
                                                         opponent_player=pairings[i][0]['player'],
                                                         round_number=next_round_number)

        if needs_a_bye:
            new_match = Match.objects.create(round_number=next_round_number, tournament=tournament,
                                             table_number=num_matches, match_completed=True, is_bye=True)
            seat = SinglePlayerSeating.objects.create(result_option=0, score=0, match=new_match,
                                                      player=pairings[num_matches][0]['player'])
            record_match_result(new_match.pk, seat.pk, 0, 0, 0, 0, 0, True)

        tournament.current_round_number = next_round_number

        html = render_to_string('tournaments/round_table.html',
                                {'tournament': tournament, 'num_rounds': next_round_number, "needs_a_bye": needs_a_bye,
                                 "num_matches": num_matches, 'request': request})
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

    seat_0_id = data.get('seat_0_id', 0)
    seat_0_result = data.get('seat_0_result', 0)
    seat_0_score = data.get('seat_0_score', 0)

    seat_1_id = data.get('seat_1_id', 0)
    seat_1_result = data.get('seat_1_result', 0)
    seat_1_score = data.get('seat_1_score', 0)

    record_match_result(match_id, seat_0_id, seat_0_result, seat_0_score, seat_1_id, seat_1_result, seat_1_score, False)

    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'tab': 'pairings'})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    return HttpResponseRedirect(full_redirect_url)


def tournaments_enroll_player(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    data = request.POST
    player_id = data.get('player_id', 0)
    player = get_object_or_404(Player, pk=player_id)
    already_enrolled = TournamentParticipant.objects.filter(tournament=tournament, player=player)
    if len(already_enrolled) == 0:
        TournamentParticipant.objects.create(tournament=tournament, player=player, dropped=False, dropped_in_round=0)

    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'tab': 'manage'})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    return HttpResponseRedirect(full_redirect_url)


def tournaments_enroll_new_player(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    data = request.POST
    first_name = data.get('first_name', "")
    last_name = data.get('last_name', "")
    email = data.get('email', "")

    new_player = Player.objects.create(first_name=first_name, last_name=last_name, email_address=email)
    TournamentParticipant.objects.create(tournament=tournament, player=new_player, dropped=False, dropped_in_round=0)

    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'tab': 'manage'})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    return HttpResponseRedirect(full_redirect_url)


def tournaments_remove_player(request, tournament_id):
    data = request.POST
    participant_id = data.get('participant_id', "")
    TournamentParticipant.objects.get(pk=participant_id).delete()

    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'tab': 'manage'})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    return HttpResponseRedirect(full_redirect_url)


def tournaments_drop_player(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    plugin = tournament.game_plugin.get_plugin()

    data = request.POST
    participant_id = data.get('participant_id', "")
    participant = TournamentParticipant.objects.get(pk=participant_id)
    participant.dropped = True
    participant.dropped_in_round = tournament.get_current_round()
    participant.save()

    current_round_number = tournament.get_current_round()
    seating = SinglePlayerSeating.objects.filter(player=participant, match__round_number__exact=current_round_number, match__match_completed=False).first()
    if seating:
        match_up = TournamentParticipantOpponent.objects.filter(current_player=participant, round_number=current_round_number).first()
        other_guy = SinglePlayerSeating.objects.filter(player=match_up.opponent_player, match__round_number__exact=current_round_number).first()
        record_match_result(seating.match.pk, seating.pk, plugin.get_loss_result(), plugin.get_loss_score(), other_guy.pk, plugin.get_win_result(), plugin.get_win_score(), False)

    redirect_url = reverse('tournament_details', kwargs={'tournament_id': tournament_id})
    extra_params = urllib.parse.urlencode({'tab': 'manage'})
    full_redirect_url = '%s?%s' % (redirect_url, extra_params)
    return HttpResponseRedirect(full_redirect_url)
