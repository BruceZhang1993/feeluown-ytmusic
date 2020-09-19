import re
from datetime import timedelta
from enum import Enum
from typing import List, Optional, Any

from pydantic import BaseModel as PydanticBaseSchema, Field

from fuo_ytmusic.service import YtMusicExtractor


class BaseSchema(PydanticBaseSchema):
    @property
    def model(self):
        return None


class YtItemReturnType(Enum):
    song = 'song'
    video = 'video'
    album = 'album'
    artist = 'artist'
    playlist = 'playlist'


class YtMusicSearchNestedArtistSchema(BaseSchema):
    id: Optional[str]
    name: str

    @property
    def model(self):
        return YtMusicArtistModel(identifier=self.id, name=self.name)


class YtMusicSearchNestedAlbumSchema(BaseSchema):
    id: str = Field(default='')
    name: str

    @property
    def model(self):
        return YtMusicAlbumModel(identifier=self.id, name=self.name)


class YtMusicSearchNestedThumbnailSchema(BaseSchema):
    url: str
    width: int
    height: int


class YtMusicSearchSongSchema(BaseSchema):
    videoId: str
    title: str
    artists: List[YtMusicSearchNestedArtistSchema]
    album: YtMusicSearchNestedAlbumSchema
    duration: Optional[timedelta]
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: Optional[YtItemReturnType]

    @property
    def model(self):
        return YtMusicSongModel(identifier=self.videoId, duration=self.duration.total_seconds() * 1000 if self.duration else None,
                                title=self.title, artists=list(map(lambda a: a.model, self.artists)),
                                album=self.album.model)


class YtMusicSearchAlbumSchema(BaseSchema):
    browseId: str
    title: str
    type: Optional[str]
    artist: Optional[str]
    year: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: Optional[YtItemReturnType]

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicAlbumModel(identifier=self.browseId, name=self.title, cover=self.cover)


class YtMusicSearchArtistSchema(BaseSchema):
    browseId: str
    artist: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicArtistModel(identifier=self.browseId, name=self.artist, cover=self.cover)


class YtMusicSearchPlaylistSchema(BaseSchema):
    browseId: str
    title: str
    author: str
    itemCount: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType

    @property
    def count(self):
        if self.itemCount.endswith('+'):
            return int(self.itemCount.rstrip('+'))
        return int(self.itemCount)

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicPlaylistModel(identifier=self.browseId, name=self.title, cover=self.cover, desc=self.author)


class YtMusicStreamingAdaptiveFormat(BaseSchema):
    itag: int
    mimeType: str
    bitrate: int
    width: Optional[int]
    height: Optional[int]
    initRange: dict
    indexRange: dict
    lastModified: int
    contentLength: int
    quality: str
    fps: Optional[int]
    qualityLabel: Optional[str]
    projectionType: str
    averageBitrate: int
    approxDurationMs: int
    signatureCipher: Optional[str]


class YtMusicStreamingFormat(BaseSchema):
    itag: int
    mimeType: str
    bitrate: int
    width: int
    height: int
    lastModified: int
    contentLength: int
    quality: str
    fps: int
    qualityLabel: str
    projectionType: str
    averageBitrate: int
    audioQuality: str
    approxDurationMs: int
    audioSampleRate: int
    audioChannels: int
    signatureCipher: Optional[str]


class YtMusicStreamingData(BaseSchema):
    expiresInSeconds: int
    formats: List[YtMusicStreamingFormat]  # 音频格式
    adaptiveFormats: List[YtMusicStreamingAdaptiveFormat]  # 视频格式
    probeUrl: Optional[str]


class _YtMusicArtistSongsSchema(BaseSchema):
    browseId: Optional[str]
    results: List[YtMusicSearchSongSchema]


class _YtMusicArtistAlbumsSchema(BaseSchema):
    browseId: Optional[str]
    results: List[YtMusicSearchAlbumSchema]


class YtMusicArtistSchema(BaseSchema):
    channelId: str
    name: str
    description: Optional[str]
    views: Optional[str]
    subscribers: str
    subscribed: Optional[bool]
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    songs: Optional[_YtMusicArtistSongsSchema]
    albums: Optional[_YtMusicArtistAlbumsSchema]
    singles: Optional[_YtMusicArtistAlbumsSchema]
    videos: Any

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicArtistModel(identifier=self.channelId, name=self.name, desc=self.description, cover=self.cover,
                                  songs_browse_id=self.songs.browseId if self.songs else None,
                                  albums_browse_id=self.albums.browseId if self.albums else None,
                                  singles_browse_id=self.singles.browseId if self.singles else None,
                                  _songs=[r.model for r in self.songs.results] if self.songs else [],
                                  _albums=[r.model for r in self.albums.results] if self.albums else [])


class YtMusicSongSchema(BaseSchema):
    class NestedThumbnail(BaseSchema):
        thumbnails: List[YtMusicSearchNestedThumbnailSchema]

    videoId: str
    title: str
    lengthSeconds: int
    keywords: List[str]
    channelId: str
    isOwnerViewing: bool
    shortDescription: str
    isCrawlable: bool
    thumbnail: NestedThumbnail
    averageRating: float
    allowRatings: bool
    viewCount: int
    author: str
    isPrivate: bool
    isUnpluggedCorpus: bool
    isLiveContent: bool
    provider: Optional[str]
    artists: Optional[List[str]]
    copyright: Optional[str]
    release: Optional[str]
    production: Optional[List[str]]
    streamingData: YtMusicStreamingData

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnail.thumbnails) > 0:
            cover = self.thumbnail.thumbnails[-1].url
        return cover

    def mv(self):
        mv = YtMusicExtractor().get_mv(self.videoId)
        return YtMusicMvModel(name=self.title, desc=self.shortDescription, cover=self.cover,
                              artist=','.join(self.artists), media=mv)

    def url(self):
        return YtMusicExtractor().get_url(self.videoId)

    @property
    def model(self):
        return YtMusicSongModel(title=self.title, duration=self.lengthSeconds * 1000, schema_model=self)


class YtdlExtension(Enum):
    webm = 'webm'
    m4a = 'm4a'
    mp4 = 'mp4'


class YtdlType(Enum):
    video = 'video'
    audio = 'audio'


class YtdlFormat(BaseSchema):
    code: int
    extension: YtdlExtension
    type: YtdlType
    resolution: str
    note: tuple
    quality: str
    bitrate: int

    @classmethod
    def parse_line(cls, line: str):
        m = re.match(r'(\d+)\s+(\w+)\s+([\dx]+|audio\sonly)\s+(\w+)\s+(\w+)\s+,\s+(.*)', line)
        return cls(code=int(m.group(1)), extension=YtdlExtension(m.group(2)),
                   type=YtdlType.audio if m.group(3) == 'audio only' else YtdlType.video, resolution=m.group(3),
                   note=m.group(4, 5, 6), quality=m.group(4), bitrate=int(m.group(5).rstrip('k')) * 1000)


class YtdlNestedFormat(BaseSchema):
    format_id: int
    code: int = Field(alias='format_id')
    url: str
    player_url: str
    extension: YtdlExtension = Field(alias='ext')
    format_note: str
    quality: str = Field(alias='format_note')
    acodec: str
    vcodec: str
    abr: Optional[float]
    tbr: Optional[float]
    format: str

    @property
    def type(self) -> YtdlType:
        return YtdlType.audio if 'audio only' in self.format else YtdlType.video


class YtdlExtract(BaseSchema):
    id: str
    creator: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    title: str
    formats: List[YtdlNestedFormat]
    requested_formats: Optional[List[YtdlNestedFormat]]
    url: Optional[str]


class YtMusicUserSchema(BaseSchema):
    name: str

    @property
    def model(self):
        return YtMusicUserModel(name=self.name)


class YtMusicPlaylistSongSchema(BaseSchema):
    videoId: Optional[str]
    title: str
    artists: List[YtMusicSearchNestedArtistSchema]
    album: Optional[YtMusicSearchNestedAlbumSchema]
    likeStatus: Optional[str]
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    duration: timedelta

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicSongModel(identifier=self.videoId, title=self.title, duration=self.duration.total_seconds() * 1000,
                                cover=self.cover, artists=list(map(lambda a: a.model, self.artists)),
                                album=self.album.model if self.album is not None
                                else YtMusicSearchNestedAlbumSchema(id='', name='').model)


class YtMusicPlaylistSchema(BaseSchema):
    id: str
    privacy: str
    title: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    description: str
    duration: str
    trackCount: int
    tracks: List[YtMusicPlaylistSongSchema]

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def songs(self):
        return [track.model for track in self.tracks]

    @property
    def model(self):
        return YtMusicPlaylistModel(identifier=self.id, name=self.title, cover=self.cover,
                                    desc=self.description, songs=self.songs)


class YtMusicUserPlaylistSchema(BaseSchema):
    title: str
    playlistId: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]

    @property
    def cover(self):
        cover = ''
        if len(self.thumbnails) > 0:
            cover = self.thumbnails[-1].url
        return cover

    @property
    def model(self):
        return YtMusicPlaylistModel(identifier=self.playlistId, name=self.title, cover=self.cover,
                                    desc='')


from fuo_ytmusic.models import YtMusicSongModel, YtMusicArtistModel, YtMusicAlbumModel, YtMusicMvModel, \
    YtMusicUserModel, YtMusicPlaylistModel
