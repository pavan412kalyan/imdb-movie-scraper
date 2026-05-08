#!/usr/bin/env python3
"""
Download Rotten Tomatoes critic or audience reviews for a movie, TV season, or episode.

Examples:
  python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type critic --json
  python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type audience --limit 50
"""
import argparse
import json
import time

import requests

from rt_title_page import extract_title_page

BASE_URL = "https://www.rottentomatoes.com"
DEFAULT_PAGE_COUNT = 20
DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.rottentomatoes.com/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}

MEDIA_API_PATHS = {
    "Movie": "movies",
    "TVSeason": "tv/seasons",
    "TVEpisode": "tv/episodes",
}


def star_rating_to_number(value):
    if not value or not isinstance(value, str) or not value.startswith("STAR_"):
        return None
    value = value.replace("STAR_", "").replace("_", ".")
    try:
        return float(value)
    except ValueError:
        return None


def resolve_review_target(url, timeout=DEFAULT_TIMEOUT):
    title = extract_title_page(url, timeout=timeout)
    title_type = title.get("type")

    if title_type == "TVSeries":
        seasons = title.get("seasons") or []
        if seasons and seasons[0].get("url"):
            title = extract_title_page(seasons[0]["url"], timeout=timeout)
            title["resolved_from_series_url"] = url
            title_type = title.get("type")

    if title_type not in MEDIA_API_PATHS:
        raise RuntimeError(
            f"Reviews API target is unsupported for type={title_type}. "
            "Use a movie, TV season, or TV episode URL."
        )
    if not title.get("ems_id"):
        raise RuntimeError("Could not find Rotten Tomatoes EMS ID for this URL.")

    return title


def reviews_api_url(title):
    media_path = MEDIA_API_PATHS[title["type"]]
    return f"{BASE_URL}/napi/rtcf/v1/{media_path}/{title['ems_id']}/reviews"


def normalize_critic_review(review):
    critic = review.get("critic") or {}
    publication = review.get("publication") or {}
    return {
        "id": review.get("reviewId"),
        "review_type": "critic",
        "quote": review.get("reviewQuote"),
        "score_sentiment": review.get("scoreSentiment"),
        "original_score": review.get("originalScore"),
        "date": review.get("createDate"),
        "language": review.get("language"),
        "url": review.get("publicationReviewUrl"),
        "is_top_review": review.get("isTopReview"),
        "critic": {
            "name": critic.get("displayName"),
            "url": critic.get("rottenTomatoesUrl"),
            "vanity": critic.get("vanity"),
            "is_top_critic": critic.get("isTopCritic"),
            "tomatometer_approved": critic.get("tomatometerApproved"),
            "image": critic.get("displayImageUrl"),
        },
        "publication": {
            "name": publication.get("name"),
            "url": publication.get("editorialUrl"),
            "is_top_publication": publication.get("isTopPublication"),
            "tomatometer_approved": publication.get("tomatometerApproved"),
        },
        "raw": review,
    }


def normalize_audience_review(review):
    user = review.get("user") or {}
    return {
        "id": review.get("ratingId"),
        "review_type": "audience",
        "review": review.get("review"),
        "rating": review.get("rating"),
        "rating_number": star_rating_to_number(review.get("rating")),
        "date": review.get("createDate"),
        "display_name": review.get("displayName"),
        "is_verified": review.get("isVerified"),
        "is_super_reviewer": review.get("isSuperReviewer"),
        "has_spoilers": review.get("hasSpoilers"),
        "has_profanity": review.get("hasProfanity"),
        "user": {
            "display_name": user.get("displayName"),
            "profile_handle": user.get("profileHandle"),
            "realm": user.get("realm"),
            "image": user.get("profileImage"),
        },
        "raw": review,
    }


def normalize_review(review, review_type):
    if review_type == "critic":
        return normalize_critic_review(review)
    return normalize_audience_review(review)


def fetch_reviews(
    url,
    review_type="critic",
    top_only=False,
    verified=False,
    page_count=DEFAULT_PAGE_COUNT,
    max_pages=None,
    limit=None,
    delay=0.0,
    timeout=DEFAULT_TIMEOUT,
):
    title = resolve_review_target(url, timeout=timeout)
    api_url = reviews_api_url(title)
    reviews = []
    after = ""
    page = 0

    while True:
        page += 1
        params = {
            "after": after,
            "before": "",
            "pageCount": page_count,
            "topOnly": str(bool(top_only)).lower(),
            "type": review_type,
            "verified": str(bool(verified)).lower(),
        }
        response = requests.get(api_url, headers=HEADERS, params=params, timeout=timeout)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()

        page_reviews = data.get("reviews") or []
        page_info = data.get("pageInfo") or {}
        for review in page_reviews:
            reviews.append(normalize_review(review, review_type))
            if limit and len(reviews) >= limit:
                return {"title": title, "reviews": reviews[:limit], "page_info": page_info}

        print(f"Page {page}: fetched {len(page_reviews)} reviews (total: {len(reviews)})")

        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break
        if max_pages and page >= max_pages:
            break
        if delay > 0:
            time.sleep(delay)

    return {"title": title, "reviews": reviews, "page_info": page_info}


def main():
    parser = argparse.ArgumentParser(
        description="Download Rotten Tomatoes critic or audience reviews",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type critic
  python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type audience --limit 50 --output reviews.json
  python3 rt_reviews.py https://www.rottentomatoes.com/tv/margos_got_money_troubles/s01 --top-only --json
        """,
    )
    parser.add_argument("url", help="Rotten Tomatoes movie, TV season, TV episode, or TV series URL")
    parser.add_argument("--type", choices=("critic", "audience"), default="critic", dest="review_type",
                        help="Review type to fetch (default: critic)")
    parser.add_argument("--top-only", action="store_true", help="Only fetch top critic reviews")
    parser.add_argument("--verified", action="store_true", help="Only fetch verified audience reviews")
    parser.add_argument("--page-count", type=int, default=DEFAULT_PAGE_COUNT,
                        help=f"Reviews per page (default: {DEFAULT_PAGE_COUNT})")
    parser.add_argument("--pages", type=int, dest="max_pages", help="Maximum pages to fetch")
    parser.add_argument("--limit", type=int, help="Maximum reviews to return")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between paginated requests in seconds")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Request timeout seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--output", help="Save results to JSON")
    parser.add_argument("--json", action="store_true", help="Print full JSON to stdout")

    args = parser.parse_args()

    try:
        result = fetch_reviews(
            url=args.url,
            review_type=args.review_type,
            top_only=args.top_only,
            verified=args.verified,
            page_count=args.page_count,
            max_pages=args.max_pages,
            limit=args.limit,
            delay=args.delay,
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
        title = result.get("title") or {}
        print(f"\n{title.get('name')} | {title.get('type')} | {len(result['reviews'])} reviews")
        for review in result["reviews"][:10]:
            if args.review_type == "critic":
                critic = (review.get("critic") or {}).get("name") or "Unknown critic"
                publication = (review.get("publication") or {}).get("name") or "Unknown publication"
                print(f"- {critic} ({publication}) [{review.get('score_sentiment') or 'N/A'}]: {review.get('quote') or ''}")
            else:
                print(f"- {review.get('display_name') or 'Unknown'} [{review.get('rating_number') or 'N/A'}]: {review.get('review') or ''}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
