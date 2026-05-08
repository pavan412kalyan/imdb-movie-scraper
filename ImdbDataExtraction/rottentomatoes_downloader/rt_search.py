#!/usr/bin/env python3
"""
Search Rotten Tomatoes titles and people through the public Algolia search endpoint.

Example:
  python3 rt_search.py "finding nemo" --json
"""
import argparse
import json
from urllib.parse import urlencode

import requests

ALGOLIA_URL = "https://79frdp12pn-dsn.algolia.net/1/indexes/*/queries"
ALGOLIA_PARAMS = {
    "x-algolia-agent": "Algolia for JavaScript (4.26.0); Browser (lite)",
    "x-algolia-api-key": "175588f6e5f8319b27702e4cc4013561",
    "x-algolia-application-id": "79FRDP12PN",
}
DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.rottentomatoes.com",
    "referer": "https://www.rottentomatoes.com/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}

INDEX_NAMES = {
    "content": "content_rt",
    "people": "people_rt",
}


def build_query_params(hits_per_page):
    return urlencode(
        {
            "analyticsTags": '["header_search"]',
            "clickAnalytics": "true",
            "filters": "isEmsSearchable = 1",
            "hitsPerPage": str(hits_per_page),
        }
    )


def rotten_tomatoes_url(hit):
    vanity = hit.get("vanity")
    if not vanity:
        return None

    title_type = hit.get("type")
    if title_type == "movie":
        return f"https://www.rottentomatoes.com/m/{vanity}"
    if title_type in ("tvSeries", "tv"):
        return f"https://www.rottentomatoes.com/tv/{vanity}"
    return None


def normalize_score(score):
    if not isinstance(score, dict):
        return None
    return {
        "score": score.get("score"),
        "rating_count": score.get("ratingCount"),
        "sentiment": score.get("sentiment"),
    }


def normalize_content_hit(hit):
    scores = hit.get("rottenTomatoes") or {}
    return {
        "object_id": hit.get("objectID"),
        "rt_id": hit.get("id"),
        "ems_id": hit.get("emsId"),
        "ems_version_id": hit.get("emsVersionId"),
        "type": hit.get("type"),
        "title": hit.get("title"),
        "vanity": hit.get("vanity"),
        "url": rotten_tomatoes_url(hit),
        "release_year": hit.get("releaseYear"),
        "runtime_minutes": hit.get("runtimeMinutes"),
        "rating": hit.get("rating"),
        "genres": hit.get("genres") or [],
        "cast": hit.get("cast") or [],
        "crew": hit.get("crew") or [],
        "poster_url": hit.get("posterImageUrl"),
        "description": hit.get("description"),
        "critics_score": normalize_score(scores.get("criticsScore")),
        "audience_score": normalize_score(scores.get("audienceScore")),
        "raw": hit,
    }


def normalize_people_hit(hit):
    return {
        "object_id": hit.get("objectID"),
        "ems_id": hit.get("emsId"),
        "name": hit.get("name"),
        "vanity": hit.get("vanity"),
        "url": f"https://www.rottentomatoes.com/celebrity/{hit.get('vanity')}" if hit.get("vanity") else None,
        "raw": hit,
    }


def normalize_result(index_name, result):
    hits = result.get("hits") or []
    if index_name == "content_rt":
        normalized_hits = [normalize_content_hit(hit) for hit in hits]
    elif index_name == "people_rt":
        normalized_hits = [normalize_people_hit(hit) for hit in hits]
    else:
        normalized_hits = hits

    return {
        "index_name": index_name,
        "hits": normalized_hits,
        "nb_hits": result.get("nbHits"),
        "page": result.get("page"),
        "nb_pages": result.get("nbPages"),
        "hits_per_page": result.get("hitsPerPage"),
        "processing_time_ms": result.get("processingTimeMS"),
    }


def search_rotten_tomatoes(query, indexes=("content_rt",), hits_per_page=5, timeout=DEFAULT_TIMEOUT):
    payload = {
        "requests": [
            {
                "indexName": index_name,
                "params": build_query_params(hits_per_page),
                "query": query,
            }
            for index_name in indexes
        ]
    }
    response = requests.post(
        ALGOLIA_URL,
        params=ALGOLIA_PARAMS,
        headers=HEADERS,
        data=json.dumps(payload),
        timeout=timeout,
    )
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")

    data = response.json()
    raw_results = data.get("results") or []
    return {
        "query": query,
        "results": [
            normalize_result(indexes[index], result)
            for index, result in enumerate(raw_results)
        ],
        "raw": data,
    }


def search_content(query, hits_per_page=10, timeout=DEFAULT_TIMEOUT):
    result = search_rotten_tomatoes(
        query=query,
        indexes=("content_rt",),
        hits_per_page=hits_per_page,
        timeout=timeout,
    )
    results = result.get("results") or []
    return results[0].get("hits") if results else []


def selected_indexes(value):
    if value == "both":
        return ("content_rt", "people_rt")
    return (INDEX_NAMES[value],)


def main():
    parser = argparse.ArgumentParser(
        description="Search Rotten Tomatoes through the public Algolia search endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rt_search.py "finding nemo"
  python3 rt_search.py "margo's got money troubles" --hits-per-page 10 --json
  python3 rt_search.py "tom hanks" --index people --json
        """,
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--index", choices=("content", "people", "both"), default="content",
                        help="Search index to query (default: content)")
    parser.add_argument("--hits-per-page", type=int, default=5,
                        help="Hits per index (default: 5)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--output", help="Save results to JSON")
    parser.add_argument("--json", action="store_true", help="Print full JSON to stdout")

    args = parser.parse_args()

    try:
        result = search_rotten_tomatoes(
            query=args.query,
            indexes=selected_indexes(args.index),
            hits_per_page=args.hits_per_page,
            timeout=args.timeout,
        )
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
        for index_result in result.get("results") or []:
            print(f"\n{index_result.get('index_name')} | {index_result.get('nb_hits')} hits")
            for hit in index_result.get("hits") or []:
                title = hit.get("title") or hit.get("name")
                detail = hit.get("release_year") or hit.get("type") or ""
                print(f"- {title} {detail} | {hit.get('url') or hit.get('vanity') or ''}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
