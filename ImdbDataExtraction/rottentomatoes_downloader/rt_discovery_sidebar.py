#!/usr/bin/env python3
"""
Fetch Rotten Tomatoes discovery-sidebar modules.

Example:
  python3 rt_discovery_sidebar.py --media-type tvSeries --status AIRING --json
"""
import argparse
import json

import requests

BASE_URL = "https://www.rottentomatoes.com/cnapi/modules/discovery-sidebar"
DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.rottentomatoes.com/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}


def fetch_discovery_sidebar(media_type="tvSeries", status="AIRING", timeout=DEFAULT_TIMEOUT):
    """Fetch one Rotten Tomatoes discovery-sidebar module."""
    url = f"{BASE_URL}/{media_type}/{status}"
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
    return response.json()


def first_value(data, keys):
    """Return the first non-empty value for any key in keys."""
    for key in keys:
        if isinstance(data, dict) and data.get(key) not in (None, "", []):
            return data.get(key)
    return None


def iter_items(data, section_title=None, list_title=None, details_url=None):
    """
    Yield title records from the module response without depending on one exact
    wrapper shape. RT commonly returns sections containing lists containing items.
    """
    if isinstance(data, list):
        for entry in data:
            yield from iter_items(entry, section_title, list_title, details_url)
        return

    if not isinstance(data, dict):
        return

    current_section = first_value(data, ("sectionTitle", "moduleTitle")) or section_title
    if data.get("domId") and data.get("title"):
        current_section = data.get("title")

    if isinstance(data.get("lists"), list):
        for media_list in data["lists"]:
            yield from iter_items(
                media_list,
                section_title=current_section,
                list_title=media_list.get("title"),
                details_url=media_list.get("detailsUrl"),
            )
        return

    if isinstance(data.get("items"), list):
        for item in data["items"]:
            if isinstance(item, dict):
                record = dict(item)
                record["_section_title"] = current_section
                record["_list_title"] = list_title or data.get("title")
                record["_details_url"] = details_url or data.get("detailsUrl")
                yield record
        return

    candidate_keys = ("mediaItems", "movies", "tvSeries", "titles", "results", "content")
    for key in candidate_keys:
        if isinstance(data.get(key), list):
            for item in data[key]:
                if isinstance(item, dict):
                    yield item
            return

    for value in data.values():
        if isinstance(value, (dict, list)):
            yield from iter_items(value, current_section, list_title, details_url)


def score_value(value):
    """Normalize RT score values that may be plain numbers or nested dicts."""
    if isinstance(value, dict):
        return first_value(value, ("scorePercent", "score", "value"))
    return value


def normalize_item(item):
    """Normalize common Rotten Tomatoes title fields while preserving raw data."""
    title = first_value(item, ("title", "name", "displayName", "emsName"))
    url = first_value(item, ("url", "vanityUrl", "tomatometerUrl", "mediaUrl"))
    if url and isinstance(url, str) and url.startswith("/"):
        url = f"https://www.rottentomatoes.com{url}"

    poster = first_value(item, ("posterUrl", "posterImage", "imageUrl", "image", "thumbnailUrl"))
    if isinstance(poster, dict):
        poster = first_value(poster, ("url", "src"))

    tomato_score = score_value(
        first_value(
            item,
            (
                "tomatometerScore",
                "tomatometer",
                "criticsScore",
                "criticScore",
                "meterScore",
            ),
        )
    )
    audience_score = score_value(
        first_value(
            item,
            (
                "audienceScore",
                "audience",
                "popcornmeterScore",
                "popcornmeter",
            ),
        )
    )

    return {
        "id": first_value(item, ("id", "emsId", "mediaId", "rtId")),
        "title": title,
        "year": first_value(item, ("year", "releaseYear", "startYear")),
        "section": item.get("_section_title"),
        "list": item.get("_list_title"),
        "details_url": (
            f"https://www.rottentomatoes.com{item.get('_details_url')}"
            if item.get("_details_url") and item.get("_details_url").startswith("/")
            else item.get("_details_url")
        ),
        "url": url,
        "poster_url": poster,
        "tomatometer_score": tomato_score,
        "audience_score": audience_score,
        "synopsis": first_value(item, ("synopsis", "description", "summary")),
        "raw": item,
    }


def extract_titles(data):
    """Extract normalized title records from the discovery-sidebar response."""
    return [normalize_item(item) for item in iter_items(data) if isinstance(item, dict)]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Rotten Tomatoes discovery-sidebar title data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rt_discovery_sidebar.py
  python3 rt_discovery_sidebar.py --media-type tvSeries --status AIRING --output rt_airing_tv.json
  python3 rt_discovery_sidebar.py --media-type movies --status OPENING --json
  python3 rt_discovery_sidebar.py --raw --json
        """,
    )
    parser.add_argument("--media-type", default="tvSeries", help="RT media type path segment (default: tvSeries)")
    parser.add_argument("--status", default="AIRING", help="RT status path segment (default: AIRING)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--output", help="Save results to a JSON file")
    parser.add_argument("--json", action="store_true", help="Print results as JSON to stdout")
    parser.add_argument("--raw", action="store_true", help="Return the raw cnapi module response")

    args = parser.parse_args()

    try:
        data = fetch_discovery_sidebar(
            media_type=args.media_type,
            status=args.status,
            timeout=args.timeout,
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    result = data if args.raw else extract_titles(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    elif args.json or args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if not result:
            print("No titles found.")
            return 0

        for item in result:
            title = item.get("title") or "Untitled"
            year = item.get("year") or "N/A"
            tomato = item.get("tomatometer_score")
            audience = item.get("audience_score")
            print(f"{title} ({year}) | Tomatometer: {tomato or 'N/A'} | Audience: {audience or 'N/A'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
