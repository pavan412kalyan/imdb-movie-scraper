#!/usr/bin/env python3
"""
Resolve an IMDb title ID to a Rotten Tomatoes title, then download RT reviews.

Example:
  python3 rt_reviews_by_imdb.py tt0266543 --type critic --limit 25 --json
"""
import argparse
import json
import re

import requests

from rt_reviews import DEFAULT_PAGE_COUNT, DEFAULT_TIMEOUT, fetch_reviews
from rt_search import search_content

IMDB_URL = "https://caching.graphql.imdb.com/"

IMDB_HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}

IMDB_TITLE_QUERY = """
query GetTitle($id: ID!) {
  title(id: $id) {
    id
    titleText {
      text
    }
    originalTitleText {
      text
    }
    titleType {
      text
      id
    }
    releaseYear {
      year
    }
    series {
      series {
        id
        titleText {
          text
        }
        releaseYear {
          year
        }
      }
    }
  }
}
"""


def normalize_text(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def get_imdb_title(imdb_id, timeout=DEFAULT_TIMEOUT):
    payload = {"query": IMDB_TITLE_QUERY, "variables": {"id": imdb_id}}
    response = requests.post(IMDB_URL, headers=IMDB_HEADERS, json=payload, timeout=timeout)
    if not response.ok:
        raise RuntimeError(f"IMDb HTTP {response.status_code}: {response.text[:500]}")
    data = response.json()
    if data.get("errors"):
        raise RuntimeError(f"IMDb GraphQL error: {data['errors']}")

    title = ((data.get("data") or {}).get("title") or {})
    if not title:
        raise RuntimeError(f"IMDb title not found for {imdb_id}")

    title_type = title.get("titleType") or {}
    release_year = title.get("releaseYear") or {}
    series = ((title.get("series") or {}).get("series") or {})
    series_release_year = series.get("releaseYear") or {}

    return {
        "id": title.get("id"),
        "title": ((title.get("titleText") or {}).get("text")),
        "original_title": ((title.get("originalTitleText") or {}).get("text")),
        "title_type": {
            "id": title_type.get("id"),
            "text": title_type.get("text"),
        },
        "release_year": release_year.get("year"),
        "series": {
            "id": series.get("id"),
            "title": ((series.get("titleText") or {}).get("text")),
            "release_year": series_release_year.get("year"),
        } if series else None,
    }


def expected_rt_type(imdb_title):
    title_type = imdb_title.get("title_type") or {}
    value = f"{title_type.get('id') or ''} {title_type.get('text') or ''}".lower()
    if "episode" in value:
        return "tvEpisode"
    if "series" in value:
        return "tvSeries"
    if "movie" in value or "video" in value:
        return "movie"
    return None


def search_query_for_imdb_title(imdb_title):
    if expected_rt_type(imdb_title) == "tvEpisode" and imdb_title.get("series"):
        return imdb_title["series"].get("title") or imdb_title.get("title")
    return imdb_title.get("title") or imdb_title.get("original_title")


def score_candidate(candidate, imdb_title):
    score = 0
    candidate_title = normalize_text(candidate.get("title"))
    imdb_titles = {
        normalize_text(imdb_title.get("title")),
        normalize_text(imdb_title.get("original_title")),
    }
    imdb_titles.discard("")

    if candidate_title in imdb_titles:
        score += 60
    elif any(candidate_title and (candidate_title in title or title in candidate_title) for title in imdb_titles):
        score += 30

    candidate_year = candidate.get("release_year")
    imdb_year = imdb_title.get("release_year")
    if expected_rt_type(imdb_title) == "tvEpisode" and imdb_title.get("series"):
        imdb_year = imdb_title["series"].get("release_year") or imdb_year

    if candidate_year and imdb_year:
        if int(candidate_year) == int(imdb_year):
            score += 25
        else:
            score -= min(20, abs(int(candidate_year) - int(imdb_year)) * 5)

    expected_type = expected_rt_type(imdb_title)
    if expected_type == "tvEpisode":
        expected_type = "tvSeries"
    if expected_type and candidate.get("type") == expected_type:
        score += 15
    elif expected_type and candidate.get("type"):
        score -= 15

    if candidate.get("url"):
        score += 5

    return score


def ranked_candidates(imdb_title, hits):
    candidates = []
    for hit in hits:
        candidate = dict(hit)
        candidate["match_score"] = score_candidate(hit, imdb_title)
        candidates.append(candidate)
    return sorted(candidates, key=lambda item: item["match_score"], reverse=True)


def resolve_rt_match(imdb_title, hits, minimum_score=65):
    candidates = ranked_candidates(imdb_title, hits)
    if not candidates:
        raise RuntimeError("Rotten Tomatoes search returned no candidates.")

    best = candidates[0]
    if not best.get("url"):
        raise RuntimeError("Best Rotten Tomatoes candidate does not have a usable URL.")
    if best["match_score"] < minimum_score:
        raise RuntimeError(
            f"Low-confidence Rotten Tomatoes match ({best['match_score']}). "
            "Use --show-candidates or pass --rt-url."
        )

    if len(candidates) > 1:
        second = candidates[1]
        if second["match_score"] >= best["match_score"] - 5:
            raise RuntimeError(
                "Ambiguous Rotten Tomatoes match. Use --show-candidates or pass --rt-url."
            )

    return best, candidates


def fetch_reviews_by_imdb_id(
    imdb_id,
    review_type="critic",
    top_only=False,
    verified=False,
    page_count=DEFAULT_PAGE_COUNT,
    max_pages=None,
    limit=None,
    delay=0.0,
    timeout=DEFAULT_TIMEOUT,
    search_hits=10,
    rt_url=None,
    allow_low_confidence=False,
):
    imdb_title = get_imdb_title(imdb_id, timeout=timeout)
    candidates = []
    rt_match = None

    if rt_url:
        target_url = rt_url
    else:
        query = search_query_for_imdb_title(imdb_title)
        hits = search_content(query, hits_per_page=search_hits, timeout=timeout)
        candidates = ranked_candidates(imdb_title, hits)
        if allow_low_confidence:
            if not candidates or not candidates[0].get("url"):
                raise RuntimeError("Rotten Tomatoes search returned no usable candidates.")
            rt_match = candidates[0]
        else:
            rt_match, candidates = resolve_rt_match(imdb_title, hits)
        target_url = rt_match["url"]

    reviews_result = fetch_reviews(
        url=target_url,
        review_type=review_type,
        top_only=top_only,
        verified=verified,
        page_count=page_count,
        max_pages=max_pages,
        limit=limit,
        delay=delay,
        timeout=timeout,
    )

    if not rt_match:
        rt_title = reviews_result.get("title") or {}
        rt_match = {
            "title": rt_title.get("name"),
            "type": rt_title.get("type"),
            "url": target_url,
            "ems_id": rt_title.get("ems_id"),
            "match_score": None,
        }

    return {
        "imdb_title": imdb_title,
        "rt_match": rt_match,
        "candidates": candidates,
        "reviews_result": reviews_result,
    }


def print_candidates(candidates):
    for candidate in candidates:
        print(
            "- "
            f"{candidate.get('title')} "
            f"({candidate.get('release_year') or 'N/A'}, {candidate.get('type') or 'N/A'}) "
            f"score={candidate.get('match_score')} "
            f"{candidate.get('url') or ''}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Download Rotten Tomatoes reviews by IMDb title ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rt_reviews_by_imdb.py tt0266543 --type critic --limit 25
  python3 rt_reviews_by_imdb.py tt0266543 --type audience --limit 50 --json
  python3 rt_reviews_by_imdb.py tt0266543 --show-candidates
  python3 rt_reviews_by_imdb.py tt0266543 --rt-url https://www.rottentomatoes.com/m/finding_nemo
        """,
    )
    parser.add_argument("imdb_id", help="IMDb title ID, for example tt0266543")
    parser.add_argument("--type", choices=("critic", "audience"), default="critic", dest="review_type",
                        help="Review type to fetch (default: critic)")
    parser.add_argument("--top-only", action="store_true", help="Only fetch top critic reviews")
    parser.add_argument("--verified", action="store_true", help="Only fetch verified audience reviews")
    parser.add_argument("--page-count", type=int, default=DEFAULT_PAGE_COUNT,
                        help=f"Reviews per page (default: {DEFAULT_PAGE_COUNT})")
    parser.add_argument("--pages", type=int, dest="max_pages", help="Maximum pages to fetch")
    parser.add_argument("--limit", type=int, help="Maximum reviews to return")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between paginated requests in seconds")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--search-hits", type=int, default=10,
                        help="Rotten Tomatoes search candidates to inspect (default: 10)")
    parser.add_argument("--rt-url", help="Skip search and fetch reviews from this Rotten Tomatoes URL")
    parser.add_argument("--allow-low-confidence", action="store_true",
                        help="Use the best RT search result even when the score is low")
    parser.add_argument("--show-candidates", action="store_true",
                        help="Print RT search candidates before fetching reviews")
    parser.add_argument("--output", help="Save results to JSON")
    parser.add_argument("--json", action="store_true", help="Print full JSON to stdout")

    args = parser.parse_args()

    try:
        imdb_title = get_imdb_title(args.imdb_id, timeout=args.timeout)
        hits = []
        candidates = []
        if not args.rt_url:
            hits = search_content(
                search_query_for_imdb_title(imdb_title),
                hits_per_page=args.search_hits,
                timeout=args.timeout,
            )
            candidates = ranked_candidates(imdb_title, hits)

        if args.show_candidates:
            print(f"{imdb_title.get('title')} | {imdb_title.get('release_year')} | {args.imdb_id}")
            print_candidates(candidates)
            return 0

        result = fetch_reviews_by_imdb_id(
            imdb_id=args.imdb_id,
            review_type=args.review_type,
            top_only=args.top_only,
            verified=args.verified,
            page_count=args.page_count,
            max_pages=args.max_pages,
            limit=args.limit,
            delay=args.delay,
            timeout=args.timeout,
            search_hits=args.search_hits,
            rt_url=args.rt_url,
            allow_low_confidence=args.allow_low_confidence,
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
        imdb_title = result.get("imdb_title") or {}
        rt_match = result.get("rt_match") or {}
        reviews = (result.get("reviews_result") or {}).get("reviews") or []
        print(
            f"\nIMDb: {imdb_title.get('title')} ({imdb_title.get('release_year')}) "
            f"| RT: {rt_match.get('title')} "
            f"| score={rt_match.get('match_score')} "
            f"| {len(reviews)} reviews"
        )
        for review in reviews[:10]:
            if args.review_type == "critic":
                critic = (review.get("critic") or {}).get("name") or "Unknown critic"
                publication = (review.get("publication") or {}).get("name") or "Unknown publication"
                print(f"- {critic} ({publication}) [{review.get('score_sentiment') or 'N/A'}]: {review.get('quote') or ''}")
            else:
                print(f"- {review.get('display_name') or 'Unknown'} [{review.get('rating_number') or 'N/A'}]: {review.get('review') or ''}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
