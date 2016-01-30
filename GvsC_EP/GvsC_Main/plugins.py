from djangoplugins.point import PluginPoint

class GamePluginPoint(PluginPoint):
    """
    """
    pass
    
class MTG_GamePlugin(GamePluginPoint):
    name = 'MTG'
    title = 'Magic: The Gathering'
    
class ANR_GamePlugin(GamePluginPoint):
    name = 'ANR'
    title = 'Android: Netrunner'