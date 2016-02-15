from __future__ import absolute_import

from GvsC_EP.plugins import GamePluginPoint

class MTG_GamePlugin(GamePluginPoint):
    name = 'MTG'
    title = 'Magic: The Gathering'

    def GenerateStandingsTable(self, pTournament):
        table_string = ''
        table_string += '<table class="ui celled padded table">\r\n'
        table_string += '\t<thead>\r\n'
        table_string += '\t\t<tr>\r\n'
        table_string += '\t\t\t<th>Place</th>\r\n'
        table_string += '\t\t\t<th>Name</th>\r\n'
        table_string += '\t\t\t<th>Match Points</th>\r\n'
        table_string += '\t\t<tr>\r\n'
        table_string += '\t</thead>\r\n'
        table_string += '\t<tbody>\r\n'
        if hasattr(pTournament, 'players'):
            for i, player in enumerate(pTournament.players.all()):
                table_string += '\t\t<tr>\r\n'
                table_string += '\t\t\t<td>' + str(i+1) + '</td>\r\n'
                table_string += '\t\t\t<td>' + player.name + '</td>\r\n'
                table_string += '\t\t\t<td>' + str(0) + '</td>\r\n'
                table_string += '\t\t</tr>\r\n'

        table_string += '\t</tbody>\r\n'
        table_string += '</table>\r\n'
        return table_string