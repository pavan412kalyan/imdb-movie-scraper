#!/usr/bin/env python3
"""
Download IMDb chart titles using the chartTitles GraphQL endpoint.
"""
import argparse
import json

import requests

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "ChartTitles"

CHART_TYPES = {
    "top": "TOP_RATED_MOVIES",
    "toptv": "TOP_RATED_TV_SHOWS",
    "bottom": "LOWEST_RATED_MOVIES",
    "moviemeter": "MOST_POPULAR_MOVIES",
    "tvmeter": "MOST_POPULAR_TV_SHOWS",
}

HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "referer": "https://www.imdb.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}

QUERY_TEMPLATE = """
query ChartTitles($first: Int!, $after: String) {
  chartTitles(first: $first, after: $after, chart: { chartType: CHART_TYPE_LITERAL }) {
    edges {
      currentRank
      node {
        id
        titleText {
          text
        }
        originalTitleText {
          text
        }
        titleType {
          id
          text
          canHaveEpisodes
        }
        primaryImage {
          url
          width
          height
          caption {
            plainText
          }
        }
        releaseYear {
          year
          endYear
        }
        releaseDate {
          day
          month
          year
        }
        ratingsSummary {
          aggregateRating
          voteCount
        }
        runtime {
          seconds
        }
        certificate {
          rating
        }
        titleGenres {
          genres {
            genre {
              text
            }
          }
        }
        plot {
          plotText {
            plainText
          }
        }
        latestTrailer {
          id
        }
        productionStatus {
          currentProductionStage {
            id
            text
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""


def get_variables(chart_name, first=250, after_cursor=None):
    variables = {
        "first": first,
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables


def build_query(chart_name):
    return QUERY_TEMPLATE.replace("CHART_TYPE_LITERAL", CHART_TYPES[chart_name])


def fetch_chart_page(chart_name, first=250, after_cursor=None):
    payload = {
        "operationName": OPERATION_NAME,
        "query": build_query(chart_name),
        "variables": get_variables(chart_name, first=first, after_cursor=after_cursor),
    }

    response = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=30)
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1000]}")

    data = response.json()
    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    return data


def normalize_runtime(runtime_seconds):
    if not runtime_seconds:
        return None
    return runtime_seconds // 60


def extract_chart_titles(data, chart_name):
    titles = []
    edges = data.get("data", {}).get("chartTitles", {}).get("edges", [])

    for edge in edges:
        node = edge.get("node", {})
        title_type = node.get("titleType") or {}
        release_year = node.get("releaseYear") or {}
        ratings = node.get("ratingsSummary") or {}
        runtime = node.get("runtime") or {}
        image = node.get("primaryImage") or {}
        plot = (node.get("plot") or {}).get("plotText") or {}
        certificate = node.get("certificate") or {}
        stage = (node.get("productionStatus") or {}).get("currentProductionStage") or {}
        title_genres = (node.get("titleGenres") or {}).get("genres") or []

        titles.append(
            {
                "chart": chart_name,
                "rank": edge.get("currentRank"),
                "id": node.get("id"),
                "title": (node.get("titleText") or {}).get("text"),
                "original_title": (node.get("originalTitleText") or {}).get("text"),
                "title_type": title_type.get("text"),
                "title_type_id": title_type.get("id"),
                "can_have_episodes": title_type.get("canHaveEpisodes"),
                "year": release_year.get("year"),
                "end_year": release_year.get("endYear"),
                "release_date": node.get("releaseDate"),
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
                "latest_trailer_id": (node.get("latestTrailer") or {}).get("id"),
                "production_stage_id": stage.get("id"),
                "production_stage": stage.get("text"),
            }
        )

    return titles


def get_all_chart_titles(chart_name, limit=250):
    all_titles = []
    after_cursor = None

    while len(all_titles) < limit:
        remaining = limit - len(all_titles)
        page_size = min(remaining, 250)
        data = fetch_chart_page(chart_name, first=page_size, after_cursor=after_cursor)
        page_titles = extract_chart_titles(data, chart_name)
        all_titles.extend(page_titles)

        page_info = data.get("data", {}).get("chartTitles", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            break

    return all_titles


def main():
    parser = argparse.ArgumentParser(description="Download IMDb chart titles using GraphQL")
    parser.add_argument("--chart", choices=sorted(CHART_TYPES.keys()), default="top", help="Chart to fetch")
    parser.add_argument("--limit", type=int, default=250, help="Maximum number of titles to fetch")
    parser.add_argument("--output", help="Output JSON file path")

    args = parser.parse_args()

    print(f"Fetching IMDb chart via GraphQL: {args.chart}")

    try:
        titles = get_all_chart_titles(args.chart, limit=args.limit)
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Found {len(titles)} titles")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file_handle:
            json.dump(titles, file_handle, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(titles, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
