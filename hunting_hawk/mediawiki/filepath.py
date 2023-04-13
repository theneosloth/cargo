import requests
from .client import Client, ClientError, raw_cached_get

ImageName = str


def get_file_path(client: Client, file: ImageName) -> str:
    url = f"{client.index_endpoint()}/Special:FilePath/{file}"
    try:
        res = requests.get(url, allow_redirects=True, headers=client.headers, stream=True)
        res.close()
        url = res.url
        return url
    except requests.exceptions.HTTPError as e:
        raise ClientError from e
