from fuocore.models import BaseModel, SearchModel, SearchType, SongModel, ArtistModel, AlbumModel, MvModel, UserModel, \
    cached_field, PlaylistModel
from fuocore.reader import SequentialReader

from .provider import provider
from .service import YtMusicService


def create_g(func, identifier, schema, list_key='tracks', limit=20):
    data = func(identifier, page=1, limit=limit).get(list_key, None)
    total = data.get('trackCount', None)

    def g():
        nonlocal data
        if data is None:
            yield from ()
        else:
            page = 1
            while data:
                for obj_data in data:
                    obj = schema(**obj_data).model
                    yield obj
                page += 1
                data = func(identifier, page=page, limit=limit).get(list_key, None)

    return SequentialReader(g(), total)


class YtMusicBaseModel(BaseModel):
    api: YtMusicService = provider.api

    class Meta:
        provider = provider


class YtMusicMvModel(MvModel, YtMusicBaseModel):
    pass


class YtMusicSongModel(SongModel, YtMusicBaseModel):
    class Meta:
        fields = ['schema_model']

    @classmethod
    def get(cls, identifier):
        data = cls.api.detail(identifier)
        return YtMusicSongSchema(**data).model

    @property
    def url(self):
        return self.schema_model.url()

    @url.setter
    def url(self, _):
        pass

    @property
    def mv(self):
        return self.schema_model.mv()

    @mv.setter
    def mv(self, _):
        pass


class YtMusicArtistModel(ArtistModel, YtMusicBaseModel):
    class Meta:
        fields = ['songs_browse_id', 'albums_browse_id', 'singles_browse_id', '_songs', '_albums']
        allow_create_songs_g = False
        allow_create_albums_g = True

    @classmethod
    def get(cls, identifier):
        artist = cls.api.artist_detail(identifier)
        return YtMusicArtistSchema(**artist).model

    @property
    def songs(self):
        if self._songs is None:
            data_playlist = self.api.get_playlist(self.songs_browse_id)
            return YtMusicPlaylistSchema(**data_playlist).songs
        return self._songs

    @songs.setter
    def songs(self, _):
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
        data_search = provider.api.search(keyword, YtItemType.songs)
        songs = []
        for i in data_search:
            songs.append(YtMusicSearchSongSchema(**i).model)
        return YtMusicSearchModel(songs=songs)
    if type_ == SearchType.ar:
        data_search = provider.api.search(keyword, YtItemType.artists)
        artists = []
        for i in data_search:
            artists.append(YtMusicSearchArtistSchema(**i).model)
        return YtMusicSearchModel(artists=artists)
    if type_ == SearchType.al:
        data_search = provider.api.search(keyword, YtItemType.albums)
        albums = []
        for i in data_search:
            albums.append(YtMusicSearchAlbumSchema(**i).model)
        return YtMusicSearchModel(albums=albums)
    if type_ == SearchType.pl:
        data_search = provider.api.search(keyword, YtItemType.playlists)
        playlists = []
        for i in data_search:
            playlists.append(YtMusicSearchPlaylistSchema(**i).model)
        return YtMusicSearchModel(playlists=playlists)


from .service import YtItemType
from .schemas import (
    YtMusicSearchSongSchema, YtMusicSongSchema, YtMusicUserSchema, YtMusicUserPlaylistSchema, YtMusicPlaylistSchema,
    YtMusicSearchArtistSchema, YtMusicSearchAlbumSchema, YtMusicSearchPlaylistSchema, YtMusicArtistSchema
)
