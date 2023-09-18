import mobase
from typing import List
from .plugins.upload import LolMo2Upload
from .plugins.api_token import LolMo2ApiToken


def createPlugins() -> List[mobase.IPlugin]:
    return [LolMo2Upload(), LolMo2ApiToken()]
