from __future__ import absolute_import
from django.template.loader import render_to_string
from random import randint
from itertools import groupby

from GvsC_Main.plugins import GamePluginPoint
from GvsC_Main.models import Seating, TournamentParticipantOpponent
import GvsC_Main.errors


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

        groups = []
        uniquekeys = []
        # Sort by wins then draws then losses then byes in decending order.
        data = sorted(participants, key=lambda participant: (participant['wins'], participant['draws'], participant['losses'], participant['byes']), reverse=True)
        # Groupby splits one list into a list of lists , grouping like for like.
        # For example if you had a list of players with wins and losses [{p['n']:'a', p['w']:2, p['l']:0}, {p['n']:'b', p['w']:1, p['l']:2}, {p['n']:'c', p['w']:2, p['l']:0}, {p['n']:'d', p['w']:2, p['l']:1}, {p['n']:'e', p['w']:1, p['l']:2}]
        # You would get this back [ [ {p['n']:'a', p['w']:2, p['l']:0}, {p['n']:'c', p['w']:2, p['l']:0} ], [ {p['n']:'d', p['w']:2, p['l']:1} ], [ {p['n']:'b', p['w']:1, p['l']:2}, {p['n']:'e', p['w']:1, p['l']:2} ] ]
        for k, g in groupby(data, lambda participant: (participant['wins'], participant['draws'], participant['losses'])):
            groups.append(list(g))
            uniquekeys.append(k)
            
        #print(groups)
        pairings = []

        # Now loop through each group of players on the same record and try to match them up as best you can.
        for i, group in enumerate(groups):
            # If the group has more than 1 player in it then we are good to try and match 2 players from that group
            while len(group) > 1:
                # Grab the first person in the list.
                # Seen as players with byes will be sorted before players without byes this lets us ensure that
                # A player recieves as few byes as possible.
                # Note this will need re-working for "first-round byes" and possibly over long tournaments, might need to identify byes first and remove them from the pool.
                participant_1_index = 0
                participant_1 = group[participant_1_index]
                group.remove(participant_1)
                # Make a group of remaining opponents from the current group of players excluding the player being paired.
                remaining_opponents = list(group)
                # Keep track of the group we are looping through as we might need to change groups is there is no viable match in it.
                # This can happen in later rounds.
                remaining_opponent_group = i
                possible_opponents = []
                while True:
                    # Loop through the list
                    for possible in remaining_opponents:
                        # See if they are in my opponents list. If they are then I have played them in a previous round and we ignore them, if i haven't then we add them to the list for consideration
                        if TournamentParticipantOpponent.objects.filter(current_player=participant_1['player'], opponent_player=possible['player']).count() == 0:
                            possible_opponents.append(possible)

                    # If I still have some possible opponents left in the current group, great!
                    # Lets break out of the loop and pick one of them
                    if len(possible_opponents) > 0:
                        break
                    # If I don't then we need to look at the next group of players and start again
                    else:
                        remaining_opponent_group += 1
                        if remaining_opponent_group >= len(groups):
                            return GvsC_Main.errors.ERROR_NO_VIABLE_MATCHES, None
                        remaining_opponents = list(groups[remaining_opponent_group])
                        possible_opponents = []

                # Randomly pick a player from the remaining players
                # This isn't true swiss at this point but true swiss needs to be played with a power of 2 number of people.
                participant_2_index = randint(0, len(possible_opponents) - 1)
                participant_2 = possible_opponents[participant_2_index]

                # Add this pairing to the list of pairings I've already made
                pairings.append([participant_1, participant_2])

                # Remove the matched player from the group they belong to.
                # Pythong will see to objects as the same if they have the same data in them so I can use the object from a differnt list to do this.
                groups[remaining_opponent_group].remove(participant_2)

            # If i have 1 player left in my list and we still have atleast 1 more group of players move the last player to the front of the next group
            # They will get matched first this way, although they might mess-up the byes like this.
            if len(group) == 1 and i + 1 < len(groups):
                groups[i + 1].insert(0, group[0])
                group.remove(group[0])
            # If we are in the last group and have 1 player left over then give them the bye by pairing them with "None"
            elif len(group) == 1:
                pairings.append([group[0], None])
                
        return GvsC_Main.errors.ERROR_OK, pairings
        
    def generate_pairings_table(self, pTournament, pRoundNumber, pRequest):
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
