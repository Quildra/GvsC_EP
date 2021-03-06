from django.db import models
from polymorphic.models import PolymorphicModel
from djangoplugins.fields import PluginField
from GvsC_Main.plugins import GamePluginPoint
from django.db.models import Max

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(default="")
    
    def __str__(self):
        return self.name

class Player(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email_address = models.EmailField();
    
    def __str__(self):
        return self.first_name + " " + self.last_name

    def name(self):
        return self.first_name + " " + self.last_name
        
class TournamentParticipant(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    dropped = models.BooleanField(default=False)
    dropped_in_round = models.PositiveSmallIntegerField()
    
    def __str__(self):
        return self.player.name()

    def name(self):
        return self.player.name()
        
class TournamentParticipantOpponent(models.Model):
    current_player = models.ForeignKey(TournamentParticipant, related_name='current_player', on_delete=models.CASCADE)
    opponent_player = models.ForeignKey(TournamentParticipant, related_name='opponent_player', on_delete=models.CASCADE)
    round_number = models.PositiveSmallIntegerField()

class Team(models.Model):
    players = models.ManyToManyField(Player)
    
class Tournament(PolymorphicModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    game_plugin = PluginField(GamePluginPoint)
    #pairing_system = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    registration_start = models.TimeField()
    regestration_close = models.TimeField()
    first_round_begins = models.TimeField()
    player_limit = models.PositiveSmallIntegerField()
    description = models.TextField()
    
    def __str__(self):
        return self.title

    def get_current_round(self):
        num_rounds = self.match_set.all().aggregate(Max('round_number'))
        current_round_number = 0 if num_rounds['round_number__max'] is None else num_rounds['round_number__max']
        return current_round_number

        
class SinglePlayerTournament(Tournament):
    players = models.ManyToManyField(TournamentParticipant, blank=True)
    
class TeamTournament(Tournament):
    team_size = models.SmallIntegerField()
    teams = models.ManyToManyField(Team)
    
class Match(models.Model):
    round_number = models.PositiveSmallIntegerField()
    table_number = models.PositiveSmallIntegerField()
    match_completed = models.BooleanField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    is_bye = models.BooleanField(default=False)
    
class Seating(PolymorphicModel):
    result_option = models.PositiveSmallIntegerField() #Win, Loss, Draw etc up to the plugin to decide meaning.
    score = models.PositiveSmallIntegerField() #Additional info; Games won for MTG, Points scored for CLix etc.
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.BooleanField(default=False)
    
class SinglePlayerSeating(Seating):
    player = models.ForeignKey(TournamentParticipant, blank=True)

class TeamSeating(Seating):
    team = models.ForeignKey(Team, blank=True)
    
    
    
