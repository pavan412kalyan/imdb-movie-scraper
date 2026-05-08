#!/usr/bin/env python3
"""
Extract Rotten Tomatoes title data from a movie or TV URL.

Example:
  python3 rt_title_page.py https://www.rottentomatoes.com/tv/margos_got_money_troubles --json
"""
import argparse
import html
import json
import re

import requests

DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}


def fetch_html(url, timeout=DEFAULT_TIMEOUT):
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
    return response.text


def load_json(value):
    return json.loads(html.unescape(value))


def load_js_object(value):
    value = html.unescape(value)
    value = re.sub(r"\bundefined\b", "null", value)
    return json.loads(value)


def extract_json_ld(page_html):
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page_html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    parsed = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        try:
            parsed.append(load_json(block))
        except json.JSONDecodeError:
            continue
    return parsed


def extract_meta_tags(page_html):
    tags = {}
    pattern = re.compile(r"<meta\s+([^>]+)>", flags=re.IGNORECASE)
    attr_pattern = re.compile(r'([:\w-]+)=["\']([^"\']*)["\']')

    for match in pattern.finditer(page_html):
        attrs = dict(attr_pattern.findall(match.group(1)))
        key = attrs.get("property") or attrs.get("name")
        value = attrs.get("content")
        if key and value:
            tags[key] = html.unescape(value)

    canonical = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
        page_html,
        flags=re.IGNORECASE,
    )
    if canonical:
        tags["canonical"] = html.unescape(canonical.group(1))

    return tags


def extract_js_object(page_html, assignment_name):
    pattern = re.compile(
        re.escape(assignment_name) + r"\s*=\s*(\{.*?\});",
        flags=re.DOTALL,
    )
    match = pattern.search(page_html)
    if not match:
        return None
    try:
        return load_js_object(match.group(1))
    except json.JSONDecodeError:
        return None


def normalize_person(person):
    if not isinstance(person, dict):
        return None
    return {
        "name": person.get("name"),
        "url": person.get("sameAs"),
        "image": person.get("image"),
    }


def normalize_people(value):
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []
    return [person for person in (normalize_person(item) for item in value) if person]


def normalize_video(video):
    if not isinstance(video, dict):
        return None
    return {
        "name": video.get("name") or video.get("title"),
        "duration": video.get("duration"),
        "thumbnail_url": video.get("thumbnailUrl") or video.get("thumbnail"),
        "content_url": video.get("contentUrl") or video.get("file"),
        "upload_date": video.get("uploadDate"),
        "description": video.get("description"),
        "source_organization": video.get("sourceOrganization"),
    }


def context_for_title(context, ems_id):
    if not isinstance(context, dict):
        return None
    context_ems_id = context.get("emsId") or context.get("emsID") or context.get("titleId")
    if ems_id and context_ems_id and context_ems_id != ems_id:
        return None
    return context


def normalize_title(json_ld, meta_tags, dtm_data, bk_data, page_context):
    rating = json_ld.get("aggregateRating") or {}
    seasons = json_ld.get("containsSeason") or []
    if isinstance(seasons, dict):
        seasons = [seasons]
    ems_id = dtm_data.get("emsID") or dtm_data.get("titleId") or bk_data.get("TvSeriesId") or bk_data.get("MovieId")

    return {
        "name": json_ld.get("name") or meta_tags.get("og:title"),
        "type": json_ld.get("@type") or dtm_data.get("titleType") or bk_data.get("SiteSection"),
        "ems_id": ems_id,
        "url": json_ld.get("url") or meta_tags.get("canonical") or meta_tags.get("og:url"),
        "canonical_url": meta_tags.get("canonical"),
        "description": json_ld.get("description") or meta_tags.get("description") or meta_tags.get("og:description"),
        "synopsis": json_ld.get("description"),
        "image": json_ld.get("image") or meta_tags.get("og:image"),
        "genre": json_ld.get("genre") or [],
        "release_date": json_ld.get("dateCreated") or json_ld.get("datePublished"),
        "runtime": json_ld.get("duration"),
        "rating": {
            "name": rating.get("name"),
            "value": rating.get("ratingValue"),
            "best": rating.get("bestRating"),
            "worst": rating.get("worstRating"),
            "count": rating.get("ratingCount"),
            "review_count": rating.get("reviewCount"),
            "description": rating.get("description"),
        },
        "cast": normalize_people(json_ld.get("actor")),
        "directors": normalize_people(json_ld.get("director")),
        "producers": normalize_people(json_ld.get("producer")),
        "creators": normalize_people(json_ld.get("creator")),
        "seasons": [
            {
                "name": season.get("name"),
                "url": season.get("url"),
                "start_date": season.get("startDate"),
            }
            for season in seasons
            if isinstance(season, dict)
        ],
        "number_of_seasons": json_ld.get("numberOfSeasons"),
        "part_of_series": json_ld.get("partOfSeries"),
        "trailer": normalize_video(json_ld.get("video")),
        "meta": meta_tags,
        "rt_context": {
            "dtm_data": dtm_data,
            "bk_data": bk_data,
            "video": context_for_title(page_context.get("video"), ems_id),
            "video_clips": page_context.get("video_clips"),
            "review": context_for_title(page_context.get("review"), ems_id),
        },
        "raw_json_ld": json_ld,
    }


def extract_title_page(url, timeout=DEFAULT_TIMEOUT):
    page_html = fetch_html(url, timeout=timeout)
    json_ld_blocks = extract_json_ld(page_html)
    title_json_ld = next(
        (
            block
            for block in json_ld_blocks
            if isinstance(block, dict)
            and block.get("@type") in ("Movie", "TVSeries", "TVSeason", "TVEpisode")
        ),
        json_ld_blocks[0] if json_ld_blocks else {},
    )
    meta_tags = extract_meta_tags(page_html)
    dtm_data = extract_js_object(page_html, "RottenTomatoes.dtmData") or {}
    bk_data = extract_js_object(page_html, "root.BK") or {}
    page_context = {
        "video": extract_js_object(page_html, "root.RottenTomatoes.context.video"),
        "video_clips": extract_js_object(page_html, "root.RottenTomatoes.context.videoClipsJson"),
        "review": extract_js_object(page_html, "root.RottenTomatoes.context.review"),
    }

    return normalize_title(title_json_ld, meta_tags, dtm_data, bk_data, page_context)


def main():
    parser = argparse.ArgumentParser(
        description="Extract Rotten Tomatoes title data from a movie or TV URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rt_title_page.py https://www.rottentomatoes.com/tv/margos_got_money_troubles
  python3 rt_title_page.py https://www.rottentomatoes.com/m/finding_nemo --json
  python3 rt_title_page.py https://www.rottentomatoes.com/tv/margos_got_money_troubles --output rt_title.json
        """,
    )
    parser.add_argument("url", help="Rotten Tomatoes movie, TV series, season, or episode URL")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--output", help="Save result to a JSON file")
    parser.add_argument("--json", action="store_true", help="Print full JSON to stdout")

    args = parser.parse_args()

    try:
        result = extract_title_page(args.url, timeout=args.timeout)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    elif args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        rating = result.get("rating") or {}
        print(f"{result.get('name') or 'Untitled'}")
        print(f"Type: {result.get('type') or 'N/A'}")
        print(f"EMS ID: {result.get('ems_id') or 'N/A'}")
        print(f"Release: {result.get('release_date') or 'N/A'}")
        print(f"Tomatometer: {rating.get('value') or 'N/A'} ({rating.get('review_count') or 0} reviews)")
        print(f"Cast: {', '.join(person['name'] for person in result.get('cast', [])[:5] if person.get('name')) or 'N/A'}")
        print(f"URL: {result.get('url') or 'N/A'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
