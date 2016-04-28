from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_tag
def render_standings_table( tournament, request ):
    plugin = tournament.game_plugin.get_plugin()
    return mark_safe(plugin.generate_standings_table( tournament, request ))
    
@register.simple_tag
def render_pairings_table( tournament, round_number, request ):
    plugin = tournament.game_plugin.get_plugin()
    return mark_safe(plugin.GeneratePairingsTable( tournament, round_number, request ))
    
@register.filter    
def get_matches_in_round(tournament, round):    
    return tournament.match_set.filter(round_number__iexact=round)