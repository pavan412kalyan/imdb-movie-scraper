"""Shared IMDb HTTP headers and GraphQL endpoints."""

DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 "
    "Safari/537.36"
)

MOBILE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 "
    "Mobile Safari/537.36"
)

GRAPHQL_ACCEPT = (
    "application/graphql-response+json, application/graphql+json, "
    "application/json, */*"
)

GRAPHQL_CACHING_URL = "https://caching.graphql.imdb.com/graphql"
GRAPHQL_API_URL = "https://api.graphql.imdb.com/graphql"
GRAPHQL_PRIMARY_URL = "https://graphql.imdb.com/graphql"


def get_graphql_headers(**overrides):
    """Return a fresh copy of the common IMDb GraphQL headers."""
    headers = {
        "accept": GRAPHQL_ACCEPT,
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://www.imdb.com",
        "referer": "https://www.imdb.com/",
        "priority": "u=1, i",
        "user-agent": DESKTOP_USER_AGENT,
        "x-imdb-client-name": "imdb-web-next-localized",
        "x-imdb-user-country": "US",
        "x-imdb-user-language": "en-US",
    }
    headers.update(overrides)
    return headers


# Convenient immutable-style default for modules that do not mutate headers.
HEADERS = get_graphql_headers()
