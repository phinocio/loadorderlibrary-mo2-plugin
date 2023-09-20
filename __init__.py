import mobase
from typing import List
from .plugins.upload import LolMo2Upload
from .plugins.api_token import LolMo2ApiToken
from .plugins.slug import LolMo2Slug


def createPlugins() -> List[mobase.IPlugin]:
    return [LolMo2Upload(), LolMo2ApiToken(), LolMo2Slug()]
