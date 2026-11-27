"""Shared utilities for IMDb data extraction modules."""

from .imdb_headers import (
    DESKTOP_USER_AGENT,
    MOBILE_USER_AGENT,
    GRAPHQL_ACCEPT,
    GRAPHQL_CACHING_URL,
    GRAPHQL_API_URL,
    GRAPHQL_PRIMARY_URL,
    HEADERS,
    get_graphql_headers,
)

__all__ = [
    "DESKTOP_USER_AGENT",
    "MOBILE_USER_AGENT",
    "GRAPHQL_ACCEPT",
    "GRAPHQL_CACHING_URL",
    "GRAPHQL_API_URL",
    "GRAPHQL_PRIMARY_URL",
    "HEADERS",
    "get_graphql_headers",
]
