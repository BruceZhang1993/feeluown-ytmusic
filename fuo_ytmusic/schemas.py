import re
from datetime import timedelta
from enum import Enum
from typing import List, Optional
from urllib.parse import unquote, parse_qs, urljoin

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
    id: str
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
    duration: timedelta
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType

    @property
    def model(self):
        return YtMusicSongModel(identifier=self.videoId, duration=self.duration.total_seconds() * 1000,
                                title=self.title, artists=list(map(lambda a: a.model, self.artists)),
                                album=self.album.model)


class YtMusicSearchAlbumSchema(BaseSchema):
    browseId: str
    title: str
    type: str
    artist: str
    year: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType


class YtMusicSearchArtistSchema(BaseSchema):
    browseId: str
    artist: str
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType


class YtMusicSearchPlaylistSchema(BaseSchema):
    browseId: str
    title: str
    author: str
    itemCount: int
    thumbnails: List[YtMusicSearchNestedThumbnailSchema]
    resultType: YtItemReturnType


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
    signatureCipher: str


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
    signatureCipher: str


class YtMusicStreamingData(BaseSchema):
    expiresInSeconds: int
    formats: List[YtMusicStreamingFormat]  # 音频格式
    adaptiveFormats: List[YtMusicStreamingAdaptiveFormat]  # 视频格式
    probeUrl: Optional[str]


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
    provider: str
    artists: List[str]
    copyright: str
    release: str
    production: Optional[List[str]]
    streamingData: YtMusicStreamingData

    @property
    def cover(self):
        cover = None
        if len(self.thumbnail.thumbnails) > 0:
            cover = self.thumbnail.thumbnails[0].url
        return cover

    @property
    def mv(self):
        mv = YtMusicExtractor().get_mv(self.videoId)
        return YtMusicMvModel(name=self.title, desc=self.shortDescription, cover=self.cover,
                              artist=','.join(self.artists), media=mv)

    @property
    def url(self):
        return YtMusicExtractor().get_url(self.videoId)

    @property
    def model(self):
        return YtMusicSongModel(title=self.title, duration=self.lengthSeconds * 1000, mv=self.mv, url=self.url)


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
        return cls(code=int(m.group(1)), extension=m.group(2),
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
    creator: str
    artist: str
    album: str
    title: str
    formats: List[YtdlNestedFormat]
    requested_formats: Optional[List[YtdlNestedFormat]]
    url: Optional[str]


from fuo_ytmusic.models import YtMusicSongModel, YtMusicArtistModel, YtMusicAlbumModel, YtMusicMvModel
