from . import imageinfo, client

mediawiki_client = client.Client(domain="https://en.wikipedia.org/w/", base_path="api.php")

def test_get_image_info() -> None:
    resp = imageinfo.get_image_info(mediawiki_client, "File:Billy_Tipton.jpg")
    assert resp["query"]["normalized"][0]["to"] == "File:Billy Tipton.jpg"
