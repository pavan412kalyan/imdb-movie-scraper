import os
import requests
import json
import time
import argparse
from pathlib import Path

# === CONFIGURATION ===
BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "TitleReviewsRefine"
PAGE_SIZE = 25 #fixed

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i'
}

def get_variables(movie_id, after_cursor, sort_by="HELPFULNESS_SCORE", sort_order="DESC"):
    variables = {
        "const": movie_id,
        "filter": {},
        "first": PAGE_SIZE,
        "sort": {
            "by": sort_by,
            "order": sort_order
        }
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables


def fetch_page(movie_id, after_cursor, sort_by="HELPFULNESS_SCORE", sort_order="DESC"):
    payload = {
        "query": """query TitleReviewsRefine($const: ID!, $filter: ReviewsFilter, $first: Int!, $sort: ReviewsSort, $after: ID) {
          title(id: $const) {
            reviews(filter: $filter, first: $first, sort: $sort, after: $after) {
              edges {
                node {
                  id
                  author {
                    nickName
                  }
                  authorRating
                  helpfulness {
                    upVotes
                    downVotes
                  }
                  submissionDate
                  text {
                    originalText {
                      plainText
                    }
                  }
                  summary {
                    originalText
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }""",
        "operationName": OPERATION_NAME,
        "variables": get_variables(movie_id, after_cursor, sort_by, sort_order)
    }

    print(f"🌐 Requesting page with cursor: {after_cursor or '[first page]'}")
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()


def is_valid_response(data):
    if "errors" in data:
        print("❌ Response contains errors:")
        for err in data["errors"]:
            print(f"  - {err.get('message', 'Unknown error')}")
        return False

    edges = data.get("data", {}).get("title", {}).get("reviews", {}).get("edges")
    if not isinstance(edges, list):
        print("❌ Response is missing expected 'data.title.reviews.edges' structure.")
        return False

    return True


def save_raw_json(data, output_folder, page):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    filename = output_path / f"raw_page_{page}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved raw_page_{page}.json with {len(data['data']['title']['reviews']['edges'])} reviews.")


def download_reviews(movie_id, output_folder=None, max_pages=None, sort_by="HELPFULNESS_SCORE", sort_order="DESC", delay=1):
    """Download reviews for a specific movie ID
    
    Args:
        movie_id (str): IMDb movie ID (e.g., tt0944947)
        output_folder (str, optional): Folder to save reviews. Defaults to movie_id.
        max_pages (int, optional): Maximum number of pages to download. Defaults to all.
        sort_by (str, optional): Sort reviews by. Defaults to "HELPFULNESS_SCORE".
        sort_order (str, optional): Sort order. Defaults to "DESC".
        delay (int, optional): Delay between requests in seconds. Defaults to 1.
    """
    if not output_folder:
        output_folder = movie_id
    
    after_cursor = None
    page = 1

    while True:
        print(f"\n📄 Fetching Page {page}...")
        data = fetch_page(movie_id, after_cursor, sort_by, sort_order)

        if not is_valid_response(data):
            print("⚠️ Skipping save. Exiting early due to invalid response.")
            break

        save_raw_json(data, output_folder, page)

        page_info = data.get("data", {}).get("title", {}).get("reviews", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage") or (max_pages and page >= max_pages):
            print("🚫 No more pages or reached max pages. Exiting.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            print("⚠️ No endCursor found. Exiting.")
            break

        page += 1
        time.sleep(delay)

    print(f"\n✅ Completed fetching review pages for {movie_id}.")
    return page - 1


def main():
    parser = argparse.ArgumentParser(description="Download IMDb reviews for a movie or TV show")
    parser.add_argument("movie_id", help="IMDb movie ID (e.g., tt0944947)")
    parser.add_argument("-o", "--output", help="Output folder (default: movie_id)")
    parser.add_argument("-m", "--max-pages", type=int, help="Maximum number of pages to download")
    parser.add_argument("-s", "--sort-by", default="HELPFULNESS_SCORE", 
                        choices=["HELPFULNESS_SCORE", "SUBMIT_DATE", "RATING"], 
                        help="Sort reviews by (default: HELPFULNESS_SCORE)")
    parser.add_argument("-r", "--sort-order", default="DESC", choices=["ASC", "DESC"], 
                        help="Sort order (default: DESC)")
    parser.add_argument("-d", "--delay", type=float, default=1, 
                        help="Delay between requests in seconds (default: 1)")
    
    args = parser.parse_args()
    
    pages_downloaded = download_reviews(
        movie_id=args.movie_id,
        output_folder=args.output,
        max_pages=args.max_pages,
        sort_by=args.sort_by,
        sort_order=args.sort_order,
        delay=args.delay
    )
    
    print(f"Downloaded {pages_downloaded} pages of reviews for {args.movie_id}")

if __name__ == "__main__":
    main()
