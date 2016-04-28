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
            return max(100 * float(matches_won) / float(matches_played), 33.3)
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
            return max(100 * float(games_won) / float(games_played), 33.3)
        else:
            return 0.0
    
    def _calcualte_player_stats(self, participant, tournament):
        
        player = {}
        player['name'] = participant.name()
        player['wins'] = 0
        player['draws'] = 0
        player['losses'] = 0
        player['byes'] = 0
        player['match_points'] = 0
        player['match_win_percent'] = 0.0
        player['opp_match_win_percent'] = 0
        player['game_win_percent'] = 0
        player['opp_game_win_percent'] = 0
        player['player'] = participant

        opponents = []
        for match_up in TournamentParticipantOpponent.objects.filter(current_player=player['player']):
            opponents.append(match_up.opponent_player)

        for seating in Seating.objects.filter(singleplayerseating__player=participant, match__tournament=tournament):
            if seating.match.is_bye:
                player['byes'] += 1
                player['wins'] += 1
            elif seating.result_option == self.RESULT_WIN:
                player['wins'] += 1
            elif seating.result_option == self.RESULT_LOSS:
                player['losses'] += 1
            elif seating.result_option == self.RESULT_DRAW:
                player['draws'] += 1

        player['match_win_percent'] = self._calculate_player_match_win_percentage(participant, tournament)
        player['game_win_percent'] = self._calculate_player_game_win_percentage(participant, tournament)
        
        opponents_match_win = []
        opponents_game_win = []
        for opponent in opponents:
            opponents_match_win.append(self._calculate_player_match_win_percentage(opponent, tournament))
            opponents_game_win.append(self._calculate_player_game_win_percentage(opponent, tournament))
            
        if len(opponents_match_win) > 0:
            player['opp_match_win_percent'] = sum(opponents_match_win) / float(len(opponents_match_win))
            
        if len(opponents_game_win) > 0:
            player['opp_game_win_percent'] = sum(opponents_game_win) / float(len(opponents_game_win))
                
        return player

    def GenerateStandingsTable(self, tournament):
        single_player_tournament = hasattr(tournament, 'players')
        players = []
        if single_player_tournament:
            for i, player in enumerate(tournament.tournamentparticipant_set.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                players.append(self._calcualte_player_stats(player, tournament))
                
        # Sort the players
        players.sort(key = lambda player: (player['wins'], player['draws'], player['losses'],player['match_points'], player['opp_match_win_percent'], player['game_win_percent'], player['opp_game_win_percent'], player['byes']), reverse=True)
        
        #for player in players:
        #    print(player['name'] + " Wins: " + str(player['wins']) + " Draws: " + str(player['draws']) + " Losses: " + str(player['losses']))
        
        table_string = ''
        table_string += '<table class="ui celled padded table">\r\n'
        table_string += '\t<thead>\r\n'
        table_string += '\t\t<tr>\r\n'
        table_string += '\t\t\t<th>Place</th>\r\n'
        table_string += '\t\t\t<th>Name</th>\r\n'
        table_string += '\t\t\t<th>Match Points</th>\r\n'
        table_string += '\t\t</tr>\r\n'
        table_string += '\t</thead>\r\n'
        table_string += '\t<tbody>\r\n'
        if single_player_tournament:
            # Report the players in sorted order.
            for i, player in enumerate(players):
                table_string += '\t\t<tr>\r\n'
                table_string += '\t\t\t<td>' + str(i+1) + '</td>\r\n'
                table_string += '\t\t\t<td>' + player['name'] + '</td>\r\n'
                table_string += '\t\t\t<td>' + str(player['match_points']) + '</td>\r\n'
                table_string += '\t\t</tr>\r\n'

        table_string += '\t</tbody>\r\n'
        table_string += '</table>\r\n'
        return table_string
        
    def PairRound(self, pTournament):
        single_player_tournament = hasattr(pTournament, 'players')
        players = []
        if single_player_tournament:
            for i, player in enumerate(pTournament.tournamentparticipant_set.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                players.append(self._CalcualtePlayerStats(player, pTournament))
                
        # Sort the players
        pairings = []        
        groups = []
        uniquekeys = []
        data = sorted(players, key=lambda player: (player['wins'], player['draws'], player['losses'], player['byes']), reverse=True)
        for k, g in groupby(data, lambda player: (player['wins'], player['draws'], player['losses'])):
            groups.append(list(g))
            uniquekeys.append(k)
            
        print(groups)
        
        for i, group in enumerate(groups):
            while len(group) > 1:
                player_1_index = 0
                player_2_index = randint(1,len(group)-1)
                player_1 = group[player_1_index]
                player_2 = group[player_2_index]
                
                output = str(player_1) + " Vs " + str(player_2)

                pairings.append([player_1, player_2])
                
                group.remove(player_1)
                group.remove(player_2)
            
            if len(group) == 1 and i+1 > len(groups):
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
