from .client import Client, ClientError, raw_cached_get

ImageName = str


def get_file_path(client: Client, file: ImageName) -> str:
    url = f"{client.index_endpoint()}/Special:FilePath/{file}"
    try:
        res = raw_cached_get(client, url, {})
    except ClientError:
        return file
    return res.url
