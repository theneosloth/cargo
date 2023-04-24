"""Image info api endpoint wrapper"""
from typing import Dict, List, Optional

from pydantic import BaseModel, ValidationError

from .client import Client, cached_get

ImageName = str
ImageInfoNormalized = Dict[str, ImageName]


class ImageInfoInfo(BaseModel):
    timestamp: str
    user: str
    url: Optional[str]
    descriptionurl: Optional[str]
    descriptionshorturl: Optional[str]


class ImageInfoPage(BaseModel):
    pageid: Optional[int]
    ns: int
    title: str
    imagerepository: str
    imageinfo: Optional[List[ImageInfoInfo]]


class ImageInfoQuery(BaseModel):
    normalized: List[ImageInfoNormalized]
    pages: Dict[str, ImageInfoPage]


class ImageInfoResponse(BaseModel):
    batchcomplete: str
    query: ImageInfoQuery


# As documented here:
# https://discoursedb.org/w/api.php?action=help&modules=cargoquery
class ImageInfoParams(BaseModel):
    """A dict that only permits imageinfo parameters."""

    titles: ImageName
    action: str = "query"
    format: str = "json"
    prop: str = "imageinfo"


def get_image_info(client: Client, image_name: ImageName) -> ImageInfoResponse:
    params = ImageInfoParams(titles=image_name).__dict__
    res = cached_get(client, client.index_endpoint(), params)
    try:
        return ImageInfoResponse.parse_obj(res)
    except ValidationError as e:
        raise TypeError("Failed to unmarshal the model") from e
