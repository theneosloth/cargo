from .client import Client, ClientError, raw_cached_get

ImageName = str


def get_file_path(client: Client, file: ImageName) -> str:
    url = f"{client.index_endpoint()}/Special:FilePath/{file}"
    try:
        with requests.get(url, follow_redirects=True, headers=client.headers, stream=True) as res:
            url = res.url
        return url
    except requests.exception.HTTPError as e:
        raise ClientError from e
