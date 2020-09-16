from fuocore.models import BaseModel, SearchModel, SearchType, SongModel, ArtistModel, AlbumModel, MvModel, UserModel, \
    cached_field, PlaylistModel

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
        print(identifier)
        data = cls.api.detail(identifier)
        return YtMusicSongSchema(**data).model


class YtMusicArtistModel(ArtistModel, YtMusicBaseModel):
    pass


class YtMusicAlbumModel(AlbumModel, YtMusicBaseModel):
    pass


class YtMusicSearchModel(SearchModel, YtMusicBaseModel):
    pass


class YtMusicPlaylistModel(PlaylistModel, YtMusicBaseModel):
    @classmethod
    def get(cls, identifier):
        playlist = cls.api.get_playlist(identifier)
        return YtMusicPlaylistSchema(**playlist).model


class YtMusicUserModel(UserModel, YtMusicBaseModel):
    class Meta:
        fields_no_get = ('playlists', 'fav_playlists', 'fav_songs',
                         'fav_albums', 'fav_artists', 'rec_songs', 'rec_playlists')

    @classmethod
    def get(cls, identifier):
        return YtMusicUserSchema(name='').model

    @cached_field(ttl=5)
    def playlists(self):
        playlists = self.api.playlists()
        return [YtMusicUserPlaylistSchema(**playlist).model for playlist in playlists]


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
    YtMusicSearchSongSchema, YtMusicSongSchema, YtMusicUserSchema, YtMusicUserPlaylistSchema, YtMusicPlaylistSchema
)
