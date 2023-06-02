from .client import Client

ImageName = str


def get_file_path(client: Client, file: ImageName) -> str:
    if not file:
        return ""
    return f"{client.index_endpoint()}/Special:FilePath/{file}"
    # TODO: Cache can be populated with:
    # try:
    #     res = requests.get(
    #         url, allow_redirects=True, headers=client.headers, stream=True
    #     )
    #     res.raise_for_status()
    #     res.close()
    #     url = res.url
    #     return url
    # except requests.exceptions.HTTPError as e:
    #     return file
