from fuocore.provider import AbstractProvider

from . import __identifier__, __alias__
from .service import YtMusicService


class YtMusicProvider(AbstractProvider):
    def __init__(self):
        super().__init__()
        self.api = YtMusicService()
        self.user = None

    @property
    def name(self):
        return __alias__

    @property
    def identifier(self):
        return __identifier__


provider = YtMusicProvider()
from .models import search
provider.search = search
