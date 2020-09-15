from fuocore.models import BaseModel, SearchModel, SearchType, SongModel, ArtistModel, AlbumModel, MvModel

from .provider import provider
from .service import YtMusicService


class YtMusicBaseModel(BaseModel):
    api: YtMusicService = provider.api

    class Meta:
        provider = provider


class YtMusicMvModel(MvModel, YtMusicBaseModel):
    pass


class YtMusicSongModel(SongModel, YtMusicBaseModel):
    @classmethod
    def get(cls, identifier):
        data = cls.api.detail(identifier)
        return YtMusicSongSchema(**data).model


class YtMusicArtistModel(ArtistModel, YtMusicBaseModel):
    pass


class YtMusicAlbumModel(AlbumModel, YtMusicBaseModel):
    pass


class YtMusicSearchModel(SearchModel, YtMusicBaseModel):
    pass


def search(keyword, **kwargs) -> YtMusicSearchModel:
    type_ = SearchType.parse(kwargs.get('type_'))
    if type_ == SearchType.so:
        print(keyword)
        data_search = provider.api.search(keyword, YtItemType.songs)
        songs = []
        for i in data_search:
            songs.append(YtMusicSearchSongSchema(**i).model)
        return YtMusicSearchModel(songs=songs)


from .service import YtItemType
from .schemas import (
    YtMusicSearchSongSchema, YtMusicSongSchema
)
