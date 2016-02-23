from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_tag
def render_standings_table( tournament ):
    plugin = tournament.game_plugin.get_plugin()
    return mark_safe(plugin.GenerateStandingsTable( tournament ))
    
@register.filter    
def get_matches_in_round(tournament, round):    
    return tournament.match_set.filter(round_number__iexact=round)