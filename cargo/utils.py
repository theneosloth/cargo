"""Miscellaneous utility functions."""
from dataclasses import field, make_dataclass


def where(params: dict) -> str:
    """Convert dictionary to SQL query."""
    return " AND ".join([f'{k}="{v}"' for k, v in params.items()])
