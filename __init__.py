import mobase

from .lolmo2plugin import LolMo2Plugin


def createPlugin() -> mobase.IPlugin:
    return LolMo2Plugin()
