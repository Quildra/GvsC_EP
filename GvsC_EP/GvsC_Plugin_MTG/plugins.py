from __future__ import absolute_import
from django.template.loader import render_to_string
from random import randint
from itertools import groupby

from GvsC_Main.plugins import GamePluginPoint
from GvsC_Main.models import Seating, TournamentParticipantOpponent


class MTG_GamePlugin(GamePluginPoint):
    name = 'MTG'
    title = 'Magic: The Gathering'
    RESULT_WIN = 1
    RESULT_LOSS = 2
    RESULT_DRAW = 3
    SCORE_WIN = 2
    SCORE_LOSS = 0
    SCORE_DRAW = 1

    def _calculate_player_match_win_percentage(self, participant, tournament):
        # Byes are not included in your match win or game percentages.
        matches_played = 0
        matches_won = 0
        
        for seating in Seating.objects.filter(singleplayerseating__player=participant, match__tournament=tournament):
            if seating.result_option == self.RESULT_WIN:
                matches_won += 1
            matches_played += 1
        
        if matches_played > 0:
            return 100 * float(matches_won) / float(matches_played)
        else:
            return 0.0

    def _calculate_player_game_win_percentage(self, participant, tournament):
        # Byes are not included in your match win or game percentages.
        games_played = 0
        games_won = 0
        
        for my_seating in Seating.objects.filter(singleplayerseating__player=participant, match__tournament=tournament):
            match = my_seating.match
            if match.is_bye:
                continue

            for seating in match.seating_set.all():
                if seating == my_seating:
                    games_won += seating.score
                games_played += seating.score
        
        if games_played > 0:
            return 100 * float(games_won) / float(games_played)
        else:
            return 0.0
    
    def _calcualte_player_stats(self, participant, tournament):

        participant_stats = {}
        participant_stats['name'] = participant.name()
        participant_stats['wins'] = 0
        participant_stats['draws'] = 0
        participant_stats['losses'] = 0
        participant_stats['byes'] = 0
        participant_stats['match_points'] = 0
        participant_stats['match_win_percent'] = 0.0
        participant_stats['opp_match_win_percent'] = 0
        participant_stats['game_win_percent'] = 0
        participant_stats['opp_game_win_percent'] = 0
        participant_stats['player'] = participant

        opponents = []
        for match_up in TournamentParticipantOpponent.objects.filter(current_player=participant_stats['player']):
            opponents.append(match_up.opponent_player)

        for seating in Seating.objects.filter(singleplayerseating__player=participant, match__tournament=tournament):
            if seating.match.is_bye:
                participant_stats['byes'] += 1
                participant_stats['wins'] += 1
            elif seating.result_option == self.RESULT_WIN:
                participant_stats['wins'] += 1
            elif seating.result_option == self.RESULT_LOSS:
                participant_stats['losses'] += 1
            elif seating.result_option == self.RESULT_DRAW:
                participant_stats['draws'] += 1

        participant_stats['match_win_percent'] = self._calculate_player_match_win_percentage(participant, tournament)
        participant_stats['game_win_percent'] = self._calculate_player_game_win_percentage(participant, tournament)
        
        opponents_match_win = []
        opponents_game_win = []
        for opponent in opponents:
            opponents_match_win.append(self._calculate_player_match_win_percentage(opponent, tournament))
            opponents_game_win.append(self._calculate_player_game_win_percentage(opponent, tournament))
            
        if len(opponents_match_win) > 0:
            participant_stats['opp_match_win_percent'] = sum(opponents_match_win) / float(len(opponents_match_win))
            
        if len(opponents_game_win) > 0:
            participant_stats['opp_game_win_percent'] = sum(opponents_game_win) / float(len(opponents_game_win))
                
        return participant_stats

    def generate_standings_table(self, tournament, request):
        single_player_tournament = hasattr(tournament, 'players')
        participants = []
        if single_player_tournament:
            for i, participant in enumerate(tournament.tournamentparticipant_set.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                participants.append(self._calcualte_player_stats(participant, tournament))
                
        # Sort the players
        participants.sort(key = lambda participant: (participant['wins'], participant['draws'], participant['losses'], participant['match_points'], participant['opp_match_win_percent'], participant['game_win_percent'], participant['opp_game_win_percent'], participant['byes']), reverse=True)
        
        #for player in players:
        #    print(player['name'] + " Wins: " + str(player['wins']) + " Draws: " + str(player['draws']) + " Losses: " + str(player['losses']))

        html = render_to_string('MTG_Standings_Table.html', {'participants': participants}, request=request)
        return html
        
    def PairRound(self, pTournament):
        single_player_tournament = hasattr(pTournament, 'players')
        participants = []
        if single_player_tournament:
            for i, participant in enumerate(pTournament.tournamentparticipant_set.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                if not participant.dropped:
                    participants.append(self._calcualte_player_stats(participant, pTournament))
                
        # Sort the players
        pairings = []        
        groups = []
        uniquekeys = []
        data = sorted(participants, key=lambda participant: (participant['wins'], participant['draws'], participant['losses'], participant['byes']), reverse=True)
        for k, g in groupby(data, lambda participant: (participant['wins'], participant['draws'], participant['losses'])):
            groups.append(list(g))
            uniquekeys.append(k)
            
        print(groups)
        
        for i, group in enumerate(groups):
            while len(group) > 1:
                participant_1_index = 0
                participant_1 = group[participant_1_index]
                group.remove(participant_1)
                # Make a group of possible opponents from the current group of players
                possible_opponents = list(group)
                possible_opponent_group = i
                while True:
                    # Loop through the list
                    for possible in possible_opponents:
                        # See if they are in my opponents list.
                        if TournamentParticipantOpponent.objects.filter(current_player=participant_1['player'], opponent_player=possible['player']).count() > 0:
                            possible_opponents.remove(possible)

                    if len(possible_opponents) > 0:
                        break;
                    else:
                        possible_opponent_group += 1
                        possible_opponents = list(groups[possible_opponent_group])

                participant_2_index = randint(0,len(possible_opponents)-1)
                participant_2 = groups[possible_opponent_group][participant_2_index]

                output = str(participant_1) + " Vs " + str(participant_2)

                pairings.append([participant_1, participant_2])
                

                groups[possible_opponent_group].remove(participant_2)
            
            if len(group) == 1 and i+1 < len(groups):
                groups[i+1].insert(0, group[0])
                group.remove(group[0])
            elif len(group) == 1:
                pairings.append([group[0], None])
                
        return pairings
        
    def GeneratePairingsTable(self, pTournament, pRoundNumber, pRequest):
        single_player_tournament = hasattr(pTournament, 'players')
        
        html = render_to_string('MTG_Pairings_Table.html', {'tournament': pTournament, 'matches':pTournament.match_set.filter(round_number__iexact=pRoundNumber)}, request=pRequest)
        return html
        
    def DetermineWinner(self, pSeat0, pSeat1):
        # Result Options:
        # 0 - No Result, 1 - Win, 2 - Loss, 3 - Draw
        if int(pSeat0.result_option) == self.RESULT_WIN:
            pSeat0.winner = True
        elif int(pSeat1.result_option) == self.RESULT_WIN:
            pSeat1.winner = True
            
    def get_bye_result(self):
        return self.RESULT_WIN
    def get_bye_score(self):
        return self.SCORE_WIN

    def get_win_result(self):
        return self.RESULT_WIN
    def get_win_score(self):
        return self.SCORE_WIN

    def get_loss_result(self):
        return self.RESULT_LOSS
    def get_loss_score(self):
        return self.SCORE_LOSS

    def get_draw_result(self):
        return self.RESULT_DRAW
    def get_draw_score(self):
        return self.SCORE_DRAW
