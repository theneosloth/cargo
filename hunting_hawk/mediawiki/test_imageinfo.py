import os

import pytest

from . import client, imageinfo

mediawiki_client = client.Client(
    domain="https://en.wikipedia.org/w/", index_path="", api_path="api.php"
)

RUN_SMOKE = os.getenv("HUNTING_HAWK_SMOKE", False)


@pytest.mark.skipif(not RUN_SMOKE, reason="Makes real requests.")
def test_get_image_info() -> None:
    resp = imageinfo.get_image_info(
        mediawiki_client, imageinfo.ImageName("File:Billy_Tipton.jpg")
    )
    assert resp.query.normalized[0]["to"] == "File:Billy Tipton.jpg"
