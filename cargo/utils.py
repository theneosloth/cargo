"""Miscellaneous utility."""


def where(params: dict) -> str:
    """Convert dictionary to SQL query."""
    return " AND ".join([f'{k}="{v}"' for k, v in params.items()])
