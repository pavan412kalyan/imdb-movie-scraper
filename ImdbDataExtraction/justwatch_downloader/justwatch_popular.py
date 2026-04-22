#!/usr/bin/env python3
"""
Fetch popular titles from JustWatch by provider(s) and country.

Usage:
  python3 justwatch_popular.py --country IN --providers nfx
  python3 justwatch_popular.py --country US --providers nfx hoc amp --pages 3
  python3 justwatch_popular.py --country IN --providers nfx --type SHOW --min-rating 7 --output results.json
  python3 justwatch_popular.py --list-providers --country IN

Common provider short names:
  nfx=Netflix  amp=Prime Video  hoc=HBO Max  ppe=Apple TV+
  dnp=Disney+  hlu=Hulu  ppe=Peacock  trs=Tubi
"""
import argparse
import json
import time

import requests

API_URL = "https://apis.justwatch.com/graphql"
DEFAULT_COUNTRY = "US"
DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "app-version": "3.13.0-web-web",
    "content-type": "application/json",
    "origin": "https://www.justwatch.com",
    "referer": "https://www.justwatch.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

POPULAR_TITLES_QUERY = """query GetPopularTitles(
  $country: Country!,
  $first: Int! = 100,
  $language: Language!,
  $after: String,
  $popularTitlesFilter: TitleFilter,
  $popularTitlesSortBy: PopularTitlesSorting! = POPULAR,
  $sortRandomSeed: Int! = 0,
  $watchNowFilter: WatchNowOfferFilter!,
  $offset: Int = 0
) {
  popularTitles(
    country: $country
    filter: $popularTitlesFilter
    first: $first
    sortBy: $popularTitlesSortBy
    sortRandomSeed: $sortRandomSeed
    offset: $offset
    after: $after
  ) {
    edges {
      cursor
      node {
        id
        objectId
        objectType
        content(country: $country, language: $language) {
          title
          fullPath
          originalReleaseYear
          shortDescription
          runtime
          isReleased
          posterUrl(profile: S718, format: JPG)
          scoring {
            imdbScore
            imdbVotes
            tmdbScore
            tmdbPopularity
            tomatoMeter
            certifiedFresh
            jwRating
          }
          externalIds {
            imdbId
          }
        }
        watchNowOffer(country: $country, platform: WEB, filter: $watchNowFilter) {
          standardWebURL
          monetizationType
          presentationType
          retailPrice(language: $language)
          currency
          package {
            packageId
            clearName
            shortName
            technicalName
            icon
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
    totalCount
  }
}"""

PACKAGES_QUERY = """query GetPackages($country: Country!, $platform: Platform!) {
  packages(country: $country, platform: $platform) {
    id
    packageId
    clearName
    shortName
    technicalName
    icon
  }
}"""


def list_providers(country=DEFAULT_COUNTRY, timeout=DEFAULT_TIMEOUT):
    payload = {
        "operationName": "GetPackages",
        "query": PACKAGES_QUERY,
        "variables": {"country": country.upper(), "platform": "WEB"},
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
    data = response.json()
    packages = (data.get("data") or {}).get("packages") or []
    if not packages:
        print(f"No providers found for country: {country}")
        return
    print(f"\nAvailable providers (country: {country}) — {len(packages)} total\n")
    print(f"{'Short Name':<12} {'Technical Name':<20} Clear Name")
    print("-" * 55)
    for p in sorted(packages, key=lambda x: x.get("clearName", "")):
        print(f"{p.get('shortName', ''):<12} {p.get('technicalName', ''):<20} {p.get('clearName', '')}")


def normalize(node, country):
    content = node.get("content") or {}
    scoring = content.get("scoring") or {}
    external_ids = content.get("externalIds") or {}
    offer = node.get("watchNowOffer") or {}
    pkg = offer.get("package") or {}
    poster = content.get("posterUrl") or ""
    if poster and not poster.startswith("http"):
        poster = f"https://images.justwatch.com{poster}"
    return {
        "id": node.get("id"),
        "object_id": node.get("objectId"),
        "type": node.get("objectType"),
        "title": content.get("title"),
        "year": content.get("originalReleaseYear"),
        "runtime_minutes": content.get("runtime"),
        "description": content.get("shortDescription"),
        "poster_url": poster,
        "imdb_score": scoring.get("imdbScore"),
        "imdb_votes": scoring.get("imdbVotes"),
        "tmdb_score": scoring.get("tmdbScore"),
        "tmdb_popularity": scoring.get("tmdbPopularity"),
        "tomato_meter": scoring.get("tomatoMeter"),
        "certified_fresh": scoring.get("certifiedFresh"),
        "jw_rating": scoring.get("jwRating"),
        "imdb_id": external_ids.get("imdbId"),
        "watch_url": offer.get("standardWebURL"),
        "monetization_type": offer.get("monetizationType"),
        "presentation_type": offer.get("presentationType"),
        "price": offer.get("retailPrice"),
        "currency": offer.get("currency"),
        "provider_id": pkg.get("packageId"),
        "provider_name": pkg.get("clearName"),
        "provider_short": pkg.get("shortName"),
        "jw_path": content.get("fullPath"),
    }


def fetch_popular(
    providers,
    country=DEFAULT_COUNTRY,
    language="en",
    object_types=None,
    min_rating=None,
    max_rating=None,
    page_size=DEFAULT_PAGE_SIZE,
    max_pages=None,
    limit=None,
    request_delay=0.0,
    timeout=DEFAULT_TIMEOUT,
):
    title_filter = {
        "ageCertifications": [],
        "excludeGenres": [],
        "excludeProductionCountries": [],
        "objectTypes": object_types or [],
        "productionCountries": [],
        "subgenres": [],
        "genres": [],
        "packages": providers,
        "excludeIrrelevantTitles": False,
        "presentationTypes": [],
        "monetizationTypes": [],
        "searchQuery": "",
    }
    watch_now_filter = {"packages": providers, "monetizationTypes": []}

    all_titles = []
    after_cursor = None
    page = 0

    while True:
        page += 1
        variables = {
            "country": country.upper(),
            "language": language,
            "first": page_size,
            "popularTitlesSortBy": "POPULAR",
            "sortRandomSeed": 0,
            "offset": None,
            "after": after_cursor,
            "popularTitlesFilter": title_filter,
            "watchNowFilter": watch_now_filter,
        }
        payload = {
            "operationName": "GetPopularTitles",
            "query": POPULAR_TITLES_QUERY,
            "variables": variables,
        }
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        if data.get("errors"):
            raise RuntimeError(f"GraphQL errors: {data['errors']}")

        popular = (data.get("data") or {}).get("popularTitles") or {}
        edges = popular.get("edges") or []
        page_info = popular.get("pageInfo") or {}
        total = popular.get("totalCount")

        if page == 1:
            print(f"Total available: {total}")

        page_count = 0
        for edge in edges:
            node = edge.get("node") or {}
            record = normalize(node, country)
            if min_rating is not None and (record.get("imdb_score") or 0) < min_rating:
                continue
            if max_rating is not None and (record.get("imdb_score") or 10) > max_rating:
                continue
            all_titles.append(record)
            page_count += 1

        print(f"  Page {page}: fetched {len(edges)}, {page_count} passed filters (total: {len(all_titles)})")

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


def main():
    parser = argparse.ArgumentParser(
        description="Fetch popular titles from JustWatch by provider and country",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 justwatch_popular.py --country IN --providers nfx
  python3 justwatch_popular.py --country US --providers nfx hoc --pages 3 --min-rating 7
  python3 justwatch_popular.py --country IN --providers nfx --type SHOW --output shows.json
  python3 justwatch_popular.py --list-providers --country IN
        """,
    )
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="Country code (default: US)")
    parser.add_argument("--providers", nargs="+", help="Provider short names (e.g. nfx amp hoc)")
    parser.add_argument("--list-providers", action="store_true", help="List available providers for the country")
    parser.add_argument("--type", nargs="+", dest="object_types",
                        help="Filter by type: MOVIE, SHOW")
    parser.add_argument("--min-rating", type=float, help="Minimum IMDb rating")
    parser.add_argument("--max-rating", type=float, help="Maximum IMDb rating")
    parser.add_argument("--pages", type=int, dest="max_pages", help="Max pages to fetch")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE,
                        help=f"Results per page (default: {DEFAULT_PAGE_SIZE})")
    parser.add_argument("--limit", type=int, help="Max total titles to return")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests (seconds)")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    parser.add_argument("--output", help="Save results to a JSON file")
    parser.add_argument("--json", action="store_true", help="Print results as JSON to stdout")

    args = parser.parse_args()

    if args.list_providers:
        try:
            list_providers(country=args.country)
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        return 0

    if not args.providers:
        parser.error("--providers is required. Use --list-providers to see available options.")

    print(f"Fetching popular titles | country={args.country} providers={args.providers}")

    try:
        titles = fetch_popular(
            providers=args.providers,
            country=args.country,
            language=args.language,
            object_types=args.object_types,
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            page_size=args.page_size,
            max_pages=args.max_pages,
            limit=args.limit,
            request_delay=args.delay,
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
            score = f"★{t['imdb_score']:.1f}" if t.get("imdb_score") else "★N/A"
            provider = t.get("provider_name") or "N/A"
            ttype = t.get("type") or "N/A"
            print(f"{t['title']} ({t.get('year') or 'N/A'}) [{ttype}] {score} | {provider}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
