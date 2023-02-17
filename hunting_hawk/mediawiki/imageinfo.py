"""Image info api endpoint wrapper"""
from dataclasses import dataclass
from typing import TypedDict, List, Dict, cast
from .client import Client, cached_get

ImageName = str

ImageInfoNormalized = TypedDict('ImageInfoNormalized', {'from': ImageName, 'to': ImageName})

class ImageInfoInfo(TypedDict):
    timestamp: str
    user: str

class ImageInfoPage(TypedDict):
    pageid: int
    ns: int
    title: str
    imagerepository: str
    imageinfo: List[ImageInfoInfo]

class ImageInfoQuery(TypedDict, total=True):
    normalized: List[ImageInfoNormalized]
    pages: Dict[str, ImageInfoPage]

class ImageInfoResponse(TypedDict, total=True):
    batchcomplete: str
    query: ImageInfoQuery

# As documented here:
# https://discoursedb.org/w/api.php?action=help&modules=cargoquery
@dataclass(eq=True, frozen=True)
class ImageInfoParams:
    """A dict that only permits imageinfo parameters."""

    titles: str
    action: str = "query"
    format: str = "json"
    prop: str = "imageinfo"

def get_image_info(client: Client, image_name: str) -> ImageInfoResponse:
    params = ImageInfoParams(titles = image_name).__dict__
    res = cached_get(client, client.index_endpoint(), params)
    match res:
        case dict():
            return cast(ImageInfoResponse, res)
        case _:
            raise TypeError("Failed to parse")
