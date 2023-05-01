import requests
from .client import Client, ClientError

ImageName = str


def get_file_path(client: Client, file: ImageName) -> str:
    if not file:
        return ""
    url = f"{client.index_endpoint()}/Special:FilePath/{file}"
    try:
        res = requests.get(
            url, allow_redirects=True, headers=client.headers, stream=True
        )
        res.close()
        url = res.url
        return url
    except requests.exceptions.HTTPError as e:
        return file
