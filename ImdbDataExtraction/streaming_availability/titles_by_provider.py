#!/usr/bin/env python3
"""
List IMDb titles available on a specific streaming provider (forward search).

Uses the `streamingTitles` GraphQL query on api.graphql.imdb.com — IMDb returns
recently added / featured titles for a provider directly (~49 titles, one page).
This is not a full catalog; IMDb caps the result at one page without authentication.

Usage:
  python3 titles_by_provider.py netflix
  python3 titles_by_provider.py netflix --type movie --min-rating 7
  python3 titles_by_provider.py amazon_prime_video --country GB --type tvSeries --output prime_uk.json
  python3 titles_by_provider.py disney_plus --genre Animation --json
  python3 titles_by_provider.py --list-providers tt10919420 --country US

Common provider IDs (refTagFragment / short form):
  netflix, amazon_prime_video, disney_plus, hulu, max,
  apple_tv_plus, paramount_plus, peacock, tubi, mubi
"""
import argparse
import json
import time

import requests

API_URL = "https://api.graphql.imdb.com/"
DEFAULT_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 50
DEFAULT_COUNTRY = "US"
DEFAULT_LOCALE = "en-US"

HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "referer": "https://www.imdb.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "x-imdb-client-name": "imdb-web-next-localized",
    "x-imdb-user-country": "US",
    "x-imdb-user-language": "en-US",
}

STREAMING_TITLES_QUERY = """query StreamingTitles($providerIds: [ID!], $first: Int!, $after: ID) {
  streamingTitles(filter: { providers: $providerIds }) {
    titles(first: $first, after: $after) {
      edges {
        node {
          title {
            id
            titleText { text }
            originalTitleText { text }
            titleType { id text canHaveEpisodes }
            releaseYear { year endYear }
            releaseDate { day month year }
            runtime { seconds }
            ratingsSummary { aggregateRating voteCount }
            titleGenres { genres { genre { text } } }
            plot { plotText { plainText } }
            primaryImage { url width height caption { plainText } }
            certificate { rating }
            latestTrailer { id }
          }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}"""

WATCH_QUERY = """query HERO_WATCH_BOX($id: ID!) {
  title(id: $id) {
    watchOptionsByCategory {
      categorizedWatchOptionsList {
        categoryName { value }
        watchOptions {
          title { value }
          link(platform: WEB)
          provider {
            id
            refTagFragment
            name { value }
          }
        }
      }
    }
  }
}"""


# ---------------------------------------------------------------------------
# Provider discovery (helper — show all provider IDs for a given title)
# ---------------------------------------------------------------------------

def list_providers(title_id, country=DEFAULT_COUNTRY, locale=DEFAULT_LOCALE, timeout=DEFAULT_TIMEOUT):
    headers = dict(HEADERS)
    headers["x-imdb-user-country"] = country.upper()
    headers["x-imdb-user-language"] = locale

    payload = {
        "operationName": "HERO_WATCH_BOX",
        "query": WATCH_QUERY,
        "variables": {"id": title_id},
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1000]}")
    data = response.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    categorized = (
        ((data.get("data") or {}).get("title") or {})
        .get("watchOptionsByCategory") or {}
    ).get("categorizedWatchOptionsList") or []

    seen = {}
    for category in categorized:
        cat_name = ((category.get("categoryName") or {}).get("value")) or "Unknown"
        for option in category.get("watchOptions") or []:
            provider = option.get("provider") or {}
            pid = provider.get("id")
            if pid and pid not in seen:
                seen[pid] = {
                    "id": pid,
                    "name": ((provider.get("name") or {}).get("value")),
                    "refTagFragment": provider.get("refTagFragment"),
                    "category": cat_name,
                }

    if not seen:
        print(f"No watch options found for {title_id} in country={country}.")
        print("Try a different title or country.")
        return

    print(f"\nAvailable providers for {title_id} in {country}:")
    print(f"{'Provider ID':<40} {'Name':<25} {'Category':<15} refTagFragment")
    print("-" * 105)
    for p in seen.values():
        print(f"{p['id']:<40} {p['name'] or '':<25} {p['category']:<15} {p['refTagFragment'] or ''}")
    print(f"\nPass the Provider ID (or refTagFragment) as the first argument to search titles.")


# ---------------------------------------------------------------------------
# Provider ID resolution — accept short "netflix" or full "amzn1.imdb.w2w.provider.netflix"
# ---------------------------------------------------------------------------

_SHORT_NAMES = {
    "disney_plus": "disneyplus",
    "amazon_prime_video": "prime_video",
    "prime": "prime_video",
    "prime_video_subscription": "prime_video.PRIME",
    "hbo_max": "hbo_max",
    "max": "hbo_max",
    "apple_tv_plus": "appletv",
    "appletv_plus": "appletv",
    "paramount_plus": "cbs_aa",
    "crunchyroll": "prime_video.crunchyroll",
    "mgm_plus": "epix",
    "mgmplus": "epix",
    "roku": "rokuchannel",
}

STREAMING_PROVIDERS_QUERY = """query StreamingProviders {
  streamingTitles(filter: { providers: [] }) {
    availableFilters {
      ... on StreamingTitlesFilterableAttribute {
        id
        text
        availableOptions {
          id
          text
        }
      }
    }
  }
}"""

# Fallback: discover providers by scraping a popular title's watch options per country
POPULAR_TITLES_BY_COUNTRY = {
    "IN": "tt0816692",  # Interstellar — widely available in India
    "GB": "tt0816692",
    "AU": "tt0816692",
    "CA": "tt0816692",
    "DE": "tt0816692",
    "FR": "tt0816692",
    "JP": "tt0816692",
    "BR": "tt0816692",
}


def list_all_providers(country=DEFAULT_COUNTRY, locale=DEFAULT_LOCALE, timeout=DEFAULT_TIMEOUT):
    """Fetch country-specific providers via the WatchProviders GraphQL query.
    Falls back to scraping watch options from a popular title if the global
    query returns US-only results.
    """
    headers = dict(HEADERS)
    headers["x-imdb-user-country"] = country.upper()
    headers["x-imdb-user-language"] = locale

    # The watchProviders query is country-aware via the header
    WATCH_PROVIDERS_QUERY = """query WatchProviders($first: Int!, $after: ID) {
  watchProviders(first: $first, after: $after) {
    edges {
      node {
        id
        name { value }
        refTagFragment
        isPopular
        isSupported(platform: WEB)
        watchOptionCategoryType
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}"""

    all_providers = []
    after_cursor = None
    while True:
        variables = {"first": 200}
        if after_cursor:
            variables["after"] = after_cursor
        payload = {
            "operationName": "WatchProviders",
            "query": WATCH_PROVIDERS_QUERY,
            "variables": variables,
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1000]}")
        data = response.json()
        if data.get("errors"):
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        conn = (data.get("data") or {}).get("watchProviders") or {}
        edges = conn.get("edges") or []
        for edge in edges:
            all_providers.append(edge.get("node") or {})
        page_info = conn.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            break

    # watchProviders is a global catalog — supplement with country-specific
    # providers discovered from a popular title's watch options
    probe_title = POPULAR_TITLES_BY_COUNTRY.get(country.upper(), "tt0816692")
    try:
        probe_payload = {
            "operationName": "HERO_WATCH_BOX",
            "query": WATCH_QUERY,
            "variables": {"id": probe_title},
        }
        probe_resp = requests.post(API_URL, headers=headers, json=probe_payload, timeout=timeout)
        if probe_resp.ok:
            probe_data = probe_resp.json()
            categorized = (
                ((probe_data.get("data") or {}).get("title") or {})
                .get("watchOptionsByCategory") or {}
            ).get("categorizedWatchOptionsList") or []
            existing_ids = {p.get("id") for p in all_providers}
            for category in categorized:
                cat_name = ((category.get("categoryName") or {}).get("value")) or ""
                for option in category.get("watchOptions") or []:
                    provider = option.get("provider") or {}
                    pid = provider.get("id")
                    if pid and pid not in existing_ids:
                        all_providers.append({
                            "id": pid,
                            "name": provider.get("name"),
                            "refTagFragment": provider.get("refTagFragment"),
                            "isPopular": False,
                            "watchOptionCategoryType": cat_name,
                        })
                        existing_ids.add(pid)
    except Exception:
        pass

    print(f"\nAvailable providers (country: {country}) — {len(all_providers)} total\n")
    print(f"{'Provider ID':<50} {'Name':<30} {'Category':<15} {'Popular':<8} refTagFragment")
    print("-" * 140)
    for p in sorted(all_providers, key=lambda x: (not x.get("isPopular"), ((x.get("name") or {}).get("value", "") if isinstance(x.get("name"), dict) else (x.get("name") or "")))):
        name_raw = p.get("name")
        name = name_raw.get("value", "") if isinstance(name_raw, dict) else (name_raw or "")
        cat = p.get("watchOptionCategoryType") or ""
        popular = "yes" if p.get("isPopular") else ""
        print(f"{p.get('id', ''):<50} {name:<30} {cat:<15} {popular:<8} {p.get('refTagFragment', '')}")

    return all_providers


def resolve_provider_id(provider_arg):
    """Resolve short names to full provider IDs."""
    if provider_arg.startswith("amzn1."):
        return provider_arg
    fragment = _SHORT_NAMES.get(provider_arg, provider_arg)
    return f"amzn1.imdb.w2w.provider.{fragment}"


# ---------------------------------------------------------------------------
# Core fetch — direct catalog query
# ---------------------------------------------------------------------------

def normalize_title(title_node):
    runtime = (title_node.get("runtime") or {}).get("seconds")
    ratings = title_node.get("ratingsSummary") or {}
    release_year = title_node.get("releaseYear") or {}
    release_date = title_node.get("releaseDate") or {}
    title_type = title_node.get("titleType") or {}
    image = title_node.get("primaryImage") or {}
    plot = ((title_node.get("plot") or {}).get("plotText") or {})
    genres = ((title_node.get("titleGenres") or {}).get("genres") or [])
    cert = title_node.get("certificate") or {}

    year = release_date.get("year")
    month = release_date.get("month")
    day = release_date.get("day")
    full_date = None
    if year and month and day:
        full_date = f"{year:04d}-{month:02d}-{day:02d}"
    elif year:
        full_date = str(year)

    return {
        "id": title_node.get("id"),
        "title": (title_node.get("titleText") or {}).get("text"),
        "original_title": (title_node.get("originalTitleText") or {}).get("text"),
        "title_type": title_type.get("text"),
        "title_type_id": title_type.get("id"),
        "can_have_episodes": title_type.get("canHaveEpisodes"),
        "year": release_year.get("year"),
        "end_year": release_year.get("endYear"),
        "release_date": full_date,
        "runtime_minutes": runtime // 60 if runtime else None,
        "rating": ratings.get("aggregateRating"),
        "vote_count": ratings.get("voteCount"),
        "certificate": cert.get("rating"),
        "genres": [
            g.get("genre", {}).get("text")
            for g in genres
            if g.get("genre", {}).get("text")
        ],
        "plot": plot.get("plainText"),
        "image_url": image.get("url"),
        "image_width": image.get("width"),
        "image_height": image.get("height"),
        "image_caption": (image.get("caption") or {}).get("plainText"),
        "latest_trailer_id": (title_node.get("latestTrailer") or {}).get("id"),
    }


def apply_filters(title, title_types, genres, min_year, max_year, min_rating, max_rating):
    """Client-side filtering since streamingTitles has no server-side filter args."""
    if title_types:
        tid = title.get("title_type_id") or ""
        if tid not in title_types:
            return False
    if genres:
        title_genres = [g.lower() for g in (title.get("genres") or [])]
        if not any(g.lower() in title_genres for g in genres):
            return False
    if min_year is not None and (title.get("year") or 0) < min_year:
        return False
    if max_year is not None and (title.get("year") or 9999) > max_year:
        return False
    if min_rating is not None and (title.get("rating") or 0) < min_rating:
        return False
    if max_rating is not None and (title.get("rating") or 10) > max_rating:
        return False
    return True


def fetch_provider_titles(
    provider_id,
    country=DEFAULT_COUNTRY,
    locale=DEFAULT_LOCALE,
    page_size=DEFAULT_PAGE_SIZE,
    max_pages=None,
    limit=None,
    title_types=None,
    genres=None,
    min_year=None,
    max_year=None,
    min_rating=None,
    max_rating=None,
    request_delay=0.0,
    timeout=DEFAULT_TIMEOUT,
):
    headers = dict(HEADERS)
    headers["x-imdb-user-country"] = country.upper()
    headers["x-imdb-user-language"] = locale

    all_titles = []
    after_cursor = None
    page = 0
    provider_name = None

    while True:
        page += 1
        variables = {
            "providerIds": [provider_id],
            "first": page_size,
        }
        if after_cursor:
            variables["after"] = after_cursor

        payload = {
            "operationName": "StreamingTitles",
            "query": STREAMING_TITLES_QUERY,
            "variables": variables,
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1000]}")
        data = response.json()
        # Non-fatal errors (e.g. missing provider metadata) are tolerated —
        # only bail if title data itself is missing.
        errors = data.get("errors") or []
        streaming_list = (data.get("data") or {}).get("streamingTitles") or []
        if not streaming_list:
            if errors:
                raise RuntimeError(f"GraphQL errors: {errors}")
            print("No streaming data returned.")
            break

        # streamingTitles returns a list (one entry per provider)
        provider_data = streaming_list[0]

        if provider_name is None:
            provider_name = provider_id
            print(f"Provider: {provider_name}")

        titles_conn = provider_data.get("titles") or {}
        edges = titles_conn.get("edges") or []
        page_info = titles_conn.get("pageInfo") or {}

        page_count = 0
        for edge in edges:
            title_node = ((edge.get("node") or {}).get("title")) or {}
            if not title_node.get("id"):
                continue
            record = normalize_title(title_node)
            if apply_filters(record, title_types, genres, min_year, max_year, min_rating, max_rating):
                all_titles.append(record)
                page_count += 1

        print(f"  Page {page}: fetched {len(edges)} titles, {page_count} passed filters (total: {len(all_titles)})")

        if limit and len(all_titles) >= limit:
            all_titles = all_titles[:limit]
            break

        if not page_info.get("hasNextPage"):
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            break

        if max_pages and page >= max_pages:
            print(f"Reached --max-pages limit ({max_pages}).")
            break

        if request_delay > 0:
            time.sleep(request_delay)

    return all_titles


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="List IMDb titles available on a streaming provider (direct catalog fetch)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # All titles on Netflix (US)
  python3 titles_by_provider.py netflix

  # Movies on Netflix with rating >= 7
  python3 titles_by_provider.py netflix --type movie --min-rating 7

  # TV series on Prime Video in the UK, save to file
  python3 titles_by_provider.py amazon_prime_video --country GB --type tvSeries --output prime_uk.json

  # Disney+ animations, output as JSON
  python3 titles_by_provider.py disney_plus --genre Animation --json

  # Fetch with delay between pages
  python3 titles_by_provider.py netflix --max-pages 10 --page-size 50 --request-delay 0.5

  # Discover provider IDs for a title
  python3 titles_by_provider.py --list-providers tt10919420 --country US

Common provider IDs:
  netflix, amazon_prime_video, disney_plus, hulu, max,
  apple_tv_plus, paramount_plus, peacock, tubi, mubi
        """,
    )

    parser.add_argument("provider", nargs="?",
                        help="Provider ID or short name (e.g. netflix, amazon_prime_video)")
    parser.add_argument("--list-all-providers", action="store_true",
                        help="List all available streaming providers for the given country")
    parser.add_argument("--list-providers", metavar="TITLE_ID",
                        help="Show providers available for a specific title (e.g. tt10919420)")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="Country code (default: US)")
    parser.add_argument("--locale", default=DEFAULT_LOCALE, help="Locale (default: en-US)")
    parser.add_argument("--type", nargs="+", dest="title_types",
                        help="Filter by title type ID: movie, tvSeries, tvMiniSeries, short, etc.")
    parser.add_argument("--genre", nargs="+", dest="genres",
                        help="Filter by genre: Action, Drama, Comedy, Animation, etc.")
    parser.add_argument("--min-year", type=int, help="Minimum release year")
    parser.add_argument("--max-year", type=int, help="Maximum release year")
    parser.add_argument("--min-rating", type=float, help="Minimum IMDb rating")
    parser.add_argument("--max-rating", type=float, help="Maximum IMDb rating")
    parser.add_argument("--max-pages", type=int, help="Max pages to fetch (default: all)")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE,
                        help=f"Titles per page (default: {DEFAULT_PAGE_SIZE})")
    parser.add_argument("--limit", type=int, help="Max total titles to return")
    parser.add_argument("--request-delay", type=float, default=0.0,
                        help="Delay between page requests in seconds")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help="Request timeout in seconds")
    parser.add_argument("--output", help="Save results to a JSON file")
    parser.add_argument("--json", action="store_true", help="Print results as JSON to stdout")

    args = parser.parse_args()

    if args.list_all_providers:
        try:
            list_all_providers(country=args.country, locale=args.locale, timeout=args.timeout)
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        return 0

    if args.list_providers:
        try:
            list_providers(args.list_providers, country=args.country,
                           locale=args.locale, timeout=args.timeout)
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        return 0

    if not args.provider:
        parser.error("provider is required. Use --list-providers to discover IDs.")

    provider_id = resolve_provider_id(args.provider)
    print(f"Fetching titles for provider: {provider_id} (country: {args.country})")

    try:
        titles = fetch_provider_titles(
            provider_id=provider_id,
            country=args.country,
            locale=args.locale,
            page_size=args.page_size,
            max_pages=args.max_pages,
            limit=args.limit,
            title_types=args.title_types,
            genres=args.genres,
            min_year=args.min_year,
            max_year=args.max_year,
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            request_delay=args.request_delay,
            timeout=args.timeout,
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"\nTotal: {len(titles)} titles")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(titles, fh, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    elif args.json:
        print(json.dumps(titles, indent=2, ensure_ascii=False))
    else:
        for t in titles:
            year = t.get("year") or "N/A"
            rating = t.get("rating")
            rating_str = f"{rating:.1f}" if rating else "N/A"
            ttype = t.get("title_type") or "N/A"
            genres = ", ".join(t.get("genres") or []) or "N/A"
            print(f"{t['title']} ({year}) [{ttype}] ★{rating_str} | {genres}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
