from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from .models import Player, Event, Tournament, SinglePlayerTournament, TeamTournament

class SinglePlayerTournamentAdmin(PolymorphicChildModelAdmin):
    base_model = SinglePlayerTournament
    
class TeamTournamentAdmin(PolymorphicChildModelAdmin):
    base_model = TeamTournament
    
class TournamentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = Tournament
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (SinglePlayerTournament, SinglePlayerTournamentAdmin),
        (TeamTournament, TeamTournamentAdmin),
    )

admin.site.register(Event)
admin.site.register(Player)
admin.site.register(Tournament, TournamentAdmin)

