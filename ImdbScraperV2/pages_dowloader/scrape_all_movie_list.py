# scrape_all_movie_list.py
import os  # Add this for folder creation
import requests
import urllib.parse
import json
import time

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "AdvancedTitleSearch"
## Pull from Network request in Chrome DevTools
PERSISTED_QUERY_HASH = "81b46290a78cc1e8b3d713e6a43c191c55b4dccf3e1945d6b46668945846d832"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i'
}

def get_variables(after_cursor):
    variables = {
        "first": 1000
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables

def fetch_page(after_cursor):
    payload = {
        "query": """query AdvancedTitleSearch($after: String, $first: Int!) {
          advancedTitleSearch(after: $after, first: $first) {
            edges {
              node {
                title {
                  id
                  titleText {
                    text
                  }
                  titleType {
                    text
                  }
                  releaseYear {
                    year
                  }
                  ratingsSummary {
                    aggregateRating
                    voteCount
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            total
          }
        }""",
        "operationName": OPERATION_NAME,
        "variables": get_variables(after_cursor)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def extract_titles(data):
    edges = data.get("data", {}).get("advancedTitleSearch", {}).get("edges", [])
    return [edge.get("node", {}).get("title", {}).get("titleText", {}).get("text") for edge in edges if edge.get("node", {}).get("title", {}).get("titleText")]

def main(max_pages=5, save_files=False):
    after_cursor = None

    # 📁 Create folder if saving is enabled
    folder = "all_imdb_movies"
    if save_files and not os.path.exists(folder):
        os.makedirs(folder)

    for page in range(1, max_pages + 1):
        print(f"\n🔎 Fetching page {page}...")
        data = fetch_page(after_cursor)

        if save_files:
            file_path = os.path.join(folder, f"imdb_page_{page}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        titles = extract_titles(data)
        for i, title in enumerate(titles, start=1):
            print(f"{i}. {title}")

        page_info = data.get("data", {}).get("advancedTitleSearch", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            print("✅ No more pages.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            break

        time.sleep(1)

if __name__ == "__main__":
    main(max_pages=10000000, save_files=True)