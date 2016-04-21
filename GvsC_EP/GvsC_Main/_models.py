from django.db import models
from django.contrib.auth.models import User
from polymorphic.models import PolymorphicModel
from djangoplugins.fields import PluginField
from GvsC_Main.plugins import GamePluginPoint, PairingPluginPoint

class Tournament(PolymorphicModel):
    event = models.ForeignKey(Event, models.SET_NULL, on_delete=models.CASCADE, null=True blank=True)
    game_plugin = PluginField(GamePluginPoint)
    #pairing_system = PluginField(PairingPluginPoint)
    title = models.CharField(max_length=200)
    registration_start = models.TimeField()
    regestration_close = models.TimeField()
    first_round_begins = models.TimeField()
    player_limit = models.PositiveSmallIntegerField()
    description = models.TextField()
    
    #participants = models.ForeignKey('TournamentParticipant', blank=True)
    #rounds = models.ForeignKey('TournamentRound', blank=True)
    
    def __str__(self):
        return self.title
        
class TournamentParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    num_byes = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.user.name
        
class TournamentRound(models.Model):
    round_number = models.PositiveSmallIntegerField()
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.round_number
        
class TournamentMatch(models.Model):
    round = models.ForeignKey('TournamentRound', on_delete=models.CASCADE)
    player_1 = models.ForeignKey('TournamentParticipant', on_delete=models.CASCADE)
    player_2 = models.ForeignKey('TournamentParticipant', on_delete=models.CASCADE)
    number_of_games = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return player_1 + " vs " + player_2
        
class TournamentMatchResult(models.Model):
    match = models.OneToOneField('TournamentMatch', on_delete=models.CASCADE)
    round = models.ForeignKey('TournamentRound', on_delete=models.CASCADE)
    player_1_result = models.SmallIntegerField()
    player_1_score = models.SmallIntegerField()
    player_2_result = models.SmallIntegerField()
    player_2_score = models.SmallIntegerField()
    was_draw = models.BooleanField(default=False)
    
    def __str__(self):
        return player_1 + " vs " + player_2