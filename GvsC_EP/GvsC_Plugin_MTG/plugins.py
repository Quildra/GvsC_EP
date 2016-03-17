from __future__ import absolute_import
from django.template.loader import render_to_string
from random import randint
from itertools import tee, zip_longest

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

from GvsC_EP.plugins import GamePluginPoint

class MTG_GamePlugin(GamePluginPoint):
    name = 'MTG'
    title = 'Magic: The Gathering'
    
    def _CalcualtePlayerStats(self, pPlayer):
        player = {}
        
        player['name'] = pPlayer.name
        player['match_points'] = randint(0,10)
        player['opp_match_win_percent'] = 0
        player['game_win_percent'] = 0
        player['opp_game_win_percent'] = 0
        player['byes'] = 0
        player['player'] = pPlayer
        
        return player

    def GenerateStandingsTable(self, pTournament):
        single_player_tournament = hasattr(pTournament, 'players')
        players = []
        if single_player_tournament:
            for i, player in enumerate(pTournament.players.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                players.append(self._CalcualtePlayerStats(player))
                
        # Sort the players
        players.sort(key = lambda player: (player['match_points'], player['opp_match_win_percent'], player['game_win_percent'],player['opp_game_win_percent'], player['byes'], player['name']), reverse=True)

        html = render_to_string('MTG_Standings_Table.html', {'players': players})
        return html
        
    def PairRound(self, pTournament):
        single_player_tournament = hasattr(pTournament, 'players')
        players = []
        if single_player_tournament:
            for i, player in enumerate(pTournament.players.all()):
                # Calculate the points and tie breakers for each player
                # store them locally to be sorted.
                players.append(self._CalcualtePlayerStats(player))
                
        # Sort the players
        players.sort(key = lambda player: (player['match_points'], player['opp_match_win_percent'], player['game_win_percent'],player['opp_game_win_percent'], player['byes'], player['name']), reverse=True)
        pairings = list(grouper(players, 2))
        return pairings
        
    def GeneratePairingsTable(self, pTournament, pRoundNumber):
        single_player_tournament = hasattr(pTournament, 'players')

        table_string = ''
        table_string += '<table class="ui celled padded table">\r\n'
        table_string += '\t<thead>\r\n'
        table_string += '\t\t<tr>\r\n'
        table_string += '\t\t\t<th>Player 1</th>\r\n'
        table_string += '\t\t\t<th>Player 1 Games Won</th>\r\n'
        table_string += '\t\t\t<th>Player 2</th>\r\n'
        table_string += '\t\t\t<th>Player 2 Games Won</th>\r\n'
        table_string += '\t\t\t<th>Report Result</th>\r\n'
        table_string += '\t\t</tr>\r\n'
        table_string += '\t</thead>\r\n'
        table_string += '\t<tbody>\r\n'
        if single_player_tournament:
            for match in pTournament.match_set.filter(round_number__iexact=pRoundNumber):
                if match.is_bye == True:
                    continue
                table_string += '\t\t<tr>\r\n'
                table_string += '\t\t\t<td>' + match.seating_set.first().player.name + '</td>\r\n'
                table_string += '\t\t\t<td>' + str(2) + '</td>\r\n'
                table_string += '\t\t\t<td>' + match.seating_set.last().player.name + '</td>\r\n'
                table_string += '\t\t\t<td>' + str(1) + '</td>\r\n'
                table_string += '\t\t\t<td>' + 'Edit' + '</td>\r\n'
                table_string += '\t\t</tr>\r\n'
        
        table_string += '\t</tbody>\r\n'
        table_string += '</table>\r\n'
        return table_string
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        