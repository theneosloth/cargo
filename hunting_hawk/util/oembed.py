"""oEmbed Generation"""

from dataclasses import dataclass
from typing import NewType, Optional
from urllib.parse import urlparse, parse_qs, unquote
from collections import namedtuple
from pathlib import PurePosixPath


url = NewType("url", str)


@dataclass(eq=True, frozen=True, kw_only=True)
class OEmbedType:
    version: str = "1.0"
    title: Optional[str] = None
    author_name: Optional[str] = None
    provider_name: Optional[str] = None
    provider_url: Optional[str] = None
    cache_age: Optional[int] = None
    thumbnail_url: Optional[url] = None
    thumbnail_width: Optional[int] = None
    thumbnail_height: Optional[int] = None


@dataclass(eq=True, frozen=True, kw_only=True)
class Photo(OEmbedType):
    url: str
    width: int
    height: int
    type: str = "photo"


@dataclass(eq=True, frozen=True, kw_only=True)
class Video(OEmbedType):
    width: int
    height: int
    html: str
    type: str = "video"


@dataclass(eq=True, frozen=True, kw_only=True)
class Link(OEmbedType):
    type: str = "link"


@dataclass(eq=True, frozen=True, kw_only=True)
class Rich(OEmbedType):
    html: str
    width: int
    height: int
    type: str = "rich"


# Not the right place for this
ParsedUrl = namedtuple("ParsedUrl", "parsed_url queries")


def parse_url(url: str) -> ParsedUrl:
    parsed = urlparse(url)
    return ParsedUrl(PurePosixPath(unquote(parsed.path)), parse_qs(unquote(parsed.query)))
