"""A wrapper for basic Mediawiki API features"""
import requests
import requests_cache

from dataclasses import dataclass, field

from .__version__ import VERSION

@dataclass(eq=True, frozen=True)
class Client:
    domain: str
    base_path: str
    headers: dict[str, str] = field(
        default_factory=lambda: {"User-Agent": f"cargo-export/{VERSION}"}
    )
    timeout: int = 10
    limit: int = 500

    def index_endpoint(self) -> str:
        """Construct a mediawiki API endpoint for a given mediawiki site."""
        return f"{self.domain}{self.base_path}"

class ClientError(Exception):
    """Base class for cargo thrown exceptions."""

    pass

class ClientNetworkError(ClientError):
    """Exception class for cargo exceptions related to network failures."""

def cached_get(client: Client, path: str, params: dict) -> list | dict:
    """Call a given URL. Caches the response"""
    req_params = params
    req = requests.Request("GET", path, headers=client.headers, params=req_params)
    prepped = req.prepare()

    s = requests_cache.CachedSession(use_temp = True)
    url = prepped.url

    if url is None:
        raise ClientError("Failed to construct url.")
    try:
        request = s.send(prepped, timeout=client.timeout)
        request.raise_for_status()

    except requests.exceptions.JSONDecodeError as e:
        raise ClientNetworkError from e

    except requests.exceptions.HTTPError as e:
        raise ClientNetworkError from e

    res = request.json()

    if "error" in res:
        raise ClientError(res["error"])

    match res:
        case list() | dict():
            return res
        case _:
            raise TypeError("Unknown return type")
