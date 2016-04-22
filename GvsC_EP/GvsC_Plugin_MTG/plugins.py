from __future__ import absolute_import
from django.template.loader import render_to_string
from random import randint
from itertools import tee, zip_longest, groupby

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

from GvsC_EP.plugins import GamePluginPoint
from GvsC_Main.models import Seating

class MTG_GamePlugin(GamePluginPoint):
    name = 'MTG'
    title = 'Magic: The Gathering'
    player_stats_cache = {}
    
    def _CalculatePlayerMatchWinPercentage(self, pPlayer, pTournament):
        # Byes are not included in your match win or game percentages.
        matches_played = 0
        real_wins = 0
        games_played = 0
        real_games = 0
        
        for seating in Seating.objects.filter(singleplayerseating__player=pPlayer,match__tournament=pTournament):                
            if seating.result_option == 1:
                real_wins += 1                
            matches_played +=1
        
        if matches_played > 0:
            return 100 * float(real_wins)/float(matches_played)
        else:
            return 0.0
        
    def _CalculatePlayerGameWinPercentage(self, pPlayer, pTournament):
        # Byes are not included in your match win or game percentages.
        matches_played = 0
        real_wins = 0
        games_played = 0
        real_games = 0
        
        for seating in Seating.objects.filter(singleplayerseating__player=pPlayer,match__tournament=pTournament):                
            if seating.result_option == 1:
                real_wins += 1                
            matches_played +=1
        
        if matches_played > 0:
            return 100 * float(real_wins)/float(matches_played)
        else:
            return 0.0
    
    def _CalcualtePlayerStats(self, pPlayer, pTournament):
        
        player = {}
        
        player['name'] = pPlayer.name
        player['wins'] = 0
        player['draws'] = 0
        player['losses'] = 0
        player['byes'] = 0
        player['match_points'] = 0
        player['match_win_percent'] = 0.0
        player['opp_match_win_percent'] = 0
        player['game_win_percent'] = 0
        player['opp_game_win_percent'] = 0
        player['player'] = pPlayer
        
        # Byes are not included in your match win or game percentages.
        matches_played = 0
        real_wins = 0
        games_played = 0
        real_games = 0
        
        opponents = []
        
        for seating in Seating.objects.filter(singleplayerseating__player=pPlayer,match__tournament=pTournament):
            for opponent_seating in Seating.objects.filter(match=seating.match).exclude(singleplayerseating__player=pPlayer):
                opponents.append(opponent_seating.player)
                
            if seating.match.is_bye == True:
                player['byes'] += 1
                player['wins'] += 1
            elif seating.result_option == 1:
                player['wins'] += 1
                real_wins += 1
            elif seating.result_option == 2:
                player['losses'] += 1
            elif seating.result_option == 3:
                player['draws'] += 1

            matches_played +=1
        
        if matches_played > 0:
            player['match_win_percent'] = 100 * float(real_wins)/float(matches_played)
        
        opponents_match_win = []
        opponents_game_win = []
        for opponent in opponents:
            opponents_match_win.append(self._CalculatePlayerMatchWinPercentage(opponent, pTournament))
            opponents_game_win.append(self._CalculatePlayerGameWinPercentage(opponent, pTournament))
            
        if len(opponents_match_win) > 0:
            player['opp_match_win_percent'] = sum(opponents_match_win)/float(len(opponents_match_win))
            
        if len(opponents_game_win) > 0:
            player['opp_game_win_percent'] = sum(opponents_game_win)/float(len(opponents_game_win))
                
        return player

    def GenerateStandingsTable(self, pTournament):
        single_player_tournament = hasattr(pTournament, 'players')
        players = []
        if single_player_tournament:
            for i, player in enumerate(pTournament.players.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                players.append(self._CalcualtePlayerStats(player, pTournament))
                
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
            for i, player in enumerate(pTournament.players.all()):
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
        if pSeat0.result_option == "1":
            pSeat0.winner = True
        elif pSeat1.result_option == "1":
            pSeat1.winner = True
            
    def GetByeResult(self):
        return 1
    def GetByeScore(self):
        return 2