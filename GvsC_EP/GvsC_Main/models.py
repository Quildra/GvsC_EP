from django.db import models
from polymorphic.models import PolymorphicModel
from djangoplugins.fields import PluginField
from GvsC_Main.plugins import GamePluginPoint

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(default="")
    
    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

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
        
class SinglePlayerTournament(Tournament):
    players = models.ManyToManyField(Player, blank=True)
    
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
    
class SinglePlayerSeating(Seating):
    player = models.ForeignKey(Player, blank=True)

class TeamSeating(Seating):
    team = models.ForeignKey(Team, blank=True)
    
    
    
