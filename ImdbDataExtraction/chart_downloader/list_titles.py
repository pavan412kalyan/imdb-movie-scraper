#!/usr/bin/env python3
"""
Download IMDb list titles using the TitleListMainPage GraphQL operation.
"""
import argparse
import json

import requests

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "TitleListMainPage"
PERSISTED_QUERY_SHA256 = "40709e97940b0e987bf53a1be0d700d9e8486576e219aa5fff35c434e91db8c5"
DEFAULT_PAGE_SIZE = 250

HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "priority": "u=1, i",
    "referer": "https://www.imdb.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "x-imdb-client-name": "imdb-web-next-localized",
    "x-imdb-user-country": "US",
    "x-imdb-user-language": "en-US",
}


def normalize_runtime(runtime_seconds):
    if not runtime_seconds:
        return None
    return runtime_seconds // 60


def get_variables(list_id, first=DEFAULT_PAGE_SIZE, jump_to_position=1):
    return {
        "first": first,
        "jumpToPosition": jump_to_position,
        "locale": "en-US",
        "lsConst": list_id,
        "sort": {
            "by": "LIST_ORDER",
            "order": "ASC",
        },
    }


def fetch_list_page(list_id, first=DEFAULT_PAGE_SIZE, jump_to_position=1):
    params = {
        "operationName": OPERATION_NAME,
        "variables": json.dumps(
            get_variables(list_id=list_id, first=first, jump_to_position=jump_to_position),
            separators=(",", ":"),
        ),
        "extensions": json.dumps(
            {
                "persistedQuery": {
                    "sha256Hash": PERSISTED_QUERY_SHA256,
                    "version": 1,
                }
            },
            separators=(",", ":"),
        ),
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1000]}")

    data = response.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    return data


def extract_list_metadata(data):
    list_data = data.get("data", {}).get("list") or {}
    if not list_data:
        raise RuntimeError("Could not find list data in GraphQL response.")

    primary_image = (list_data.get("primaryImage") or {}).get("image") or {}
    return {
        "id": list_data.get("id"),
        "name": (list_data.get("name") or {}).get("originalText"),
        "description": ((list_data.get("description") or {}).get("originalText") or {}).get("plainText"),
        "author_username": ((list_data.get("author") or {}).get("username") or {}).get("text"),
        "author_user_id": (list_data.get("author") or {}).get("userId"),
        "list_type": (list_data.get("listType") or {}).get("id"),
        "list_class": ((list_data.get("listClass") or {}).get("name") or {}).get("text"),
        "visibility": (list_data.get("visibility") or {}).get("id"),
        "created_date": list_data.get("createdDate"),
        "last_modified_date": list_data.get("lastModifiedDate"),
        "item_total": ((list_data.get("items") or {}).get("total")),
        "primary_image_url": primary_image.get("url"),
        "primary_image_width": primary_image.get("width"),
        "primary_image_height": primary_image.get("height"),
        "primary_image_caption": (primary_image.get("caption") or {}).get("plainText"),
    }


def extract_list_titles(data, list_id):
    list_data = data.get("data", {}).get("list") or {}
    search_data = list_data.get("titleListItemSearch") or {}
    edges = search_data.get("edges") or []
    titles = []

    for edge in edges:
        node = edge.get("node") or {}
        list_item = edge.get("listItem") or {}
        title_type = list_item.get("titleType") or {}
        release_year = list_item.get("releaseYear") or {}
        ratings = list_item.get("ratingsSummary") or {}
        runtime = list_item.get("runtime") or {}
        image = list_item.get("primaryImage") or {}
        plot = (list_item.get("plot") or {}).get("plotText") or {}
        certificate = list_item.get("certificate") or {}
        title_genres = (list_item.get("titleGenres") or {}).get("genres") or []
        stage = (list_item.get("productionStatus") or {}).get("currentProductionStage") or {}

        titles.append(
            {
                "list_id": list_id,
                "item_id": node.get("itemId"),
                "absolute_position": node.get("absolutePosition"),
                "added_at": node.get("createdDate"),
                "item_description": ((node.get("description") or {}).get("originalText") or {}).get("plainText"),
                "id": list_item.get("id"),
                "title": (list_item.get("titleText") or {}).get("text"),
                "original_title": (list_item.get("originalTitleText") or {}).get("text"),
                "title_type": title_type.get("text"),
                "title_type_id": title_type.get("id"),
                "can_have_episodes": title_type.get("canHaveEpisodes"),
                "year": release_year.get("year"),
                "end_year": release_year.get("endYear"),
                "release_date": list_item.get("releaseDate"),
                "runtime_seconds": runtime.get("seconds"),
                "runtime_minutes": normalize_runtime(runtime.get("seconds")),
                "rating": ratings.get("aggregateRating"),
                "vote_count": ratings.get("voteCount"),
                "certificate": certificate.get("rating"),
                "genres": [
                    genre.get("genre", {}).get("text")
                    for genre in title_genres
                    if genre.get("genre", {}).get("text")
                ],
                "plot": plot.get("plainText"),
                "image_url": image.get("url"),
                "image_width": image.get("width"),
                "image_height": image.get("height"),
                "image_caption": (image.get("caption") or {}).get("plainText"),
                "latest_trailer_id": (list_item.get("latestTrailer") or {}).get("id"),
                "production_stage_id": stage.get("id"),
                "production_stage": stage.get("text"),
            }
        )

    return titles


def get_all_list_data(list_id, limit=None):
    metadata = None
    all_titles = []
    jump_to_position = 1
    target_limit = limit if limit is not None else DEFAULT_PAGE_SIZE

    while True:
        remaining = (limit - len(all_titles)) if limit is not None else DEFAULT_PAGE_SIZE
        if limit is not None and remaining <= 0:
            break
        page_size = min(remaining, DEFAULT_PAGE_SIZE)
        data = fetch_list_page(list_id=list_id, first=page_size, jump_to_position=jump_to_position)

        if metadata is None:
            metadata = extract_list_metadata(data)
            if limit is None:
                item_total = metadata.get("item_total")
                if isinstance(item_total, int) and item_total > 0:
                    target_limit = item_total

        page_titles = extract_list_titles(data, list_id)
        if not page_titles:
            break

        all_titles.extend(page_titles)
        if len(all_titles) >= target_limit:
            break

        page_info = ((data.get("data") or {}).get("list") or {}).get("titleListItemSearch", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break

        jump_to_position = len(all_titles) + 1

    return metadata or {}, all_titles[:limit] if limit is not None else all_titles


def main():
    parser = argparse.ArgumentParser(description="Download IMDb list titles using GraphQL")
    parser.add_argument("list_id", help="IMDb list ID (e.g., ls039852437)")
    parser.add_argument("--limit", type=int, help="Maximum number of titles to fetch (default: all items)")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--titles-only", action="store_true", help="Output only the normalized title items")

    args = parser.parse_args()

    print(f"Fetching IMDb list via GraphQL: {args.list_id}")

    try:
        metadata, titles = get_all_list_data(args.list_id, limit=args.limit)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    result = titles if args.titles_only else {"list": metadata, "titles": titles}

    print(f"Found {len(titles)} titles")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file_handle:
            json.dump(result, file_handle, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
