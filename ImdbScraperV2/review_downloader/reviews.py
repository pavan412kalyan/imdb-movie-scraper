import os
import requests
import urllib.parse
import json
import time



MOVIE_ID = "tt0944947"

# === CONFIGURATION ===
BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "TitleReviewsRefine"
PERSISTED_QUERY_HASH = "8e851a269025170d18a33b296a5ced533529abb4e7bc3d6b96d1f36636e7f685"
PAGE_SIZE = 25 #fixed
OUTPUT_FOLDER = MOVIE_ID

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i'
}

def get_encoded_variables(after_cursor):
    variables = {
        "const": MOVIE_ID,
        "filter": {},
        "first": PAGE_SIZE,
        "locale": "en-US",
        "sort": {
            "by": "HELPFULNESS_SCORE",
            "order": "DESC"
        }
    }
    if after_cursor:
        variables["after"] = after_cursor
    return urllib.parse.quote(json.dumps(variables, separators=(',', ':')))


def fetch_page(after_cursor):
    encoded_vars = get_encoded_variables(after_cursor)
    extensions = {
        "persistedQuery": {
            "sha256Hash": PERSISTED_QUERY_HASH,
            "version": 1
        }
    }
    encoded_ext = urllib.parse.quote(json.dumps(extensions, separators=(',', ':')))
    url = f"{BASE_URL}?operationName={OPERATION_NAME}&variables={encoded_vars}&extensions={encoded_ext}"

    print(f"🌐 Requesting page with cursor: {after_cursor or '[first page]'}")
    response = requests.get(url, headers=HEADERS)
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


def save_raw_json(data, page):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    filename = os.path.join(OUTPUT_FOLDER, f"raw_page_{page}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved raw_page_{page}.json with {len(data['data']['title']['reviews']['edges'])} reviews.")


def main():
    after_cursor = None
    page = 1

    while True:
        print(f"\n📄 Fetching Page {page}...")
        data = fetch_page(after_cursor)

        if not is_valid_response(data):
            print("⚠️ Skipping save. Exiting early due to invalid response.")
            break

        save_raw_json(data, page)

        page_info = data.get("data", {}).get("title", {}).get("reviews", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            print("🚫 No more pages. Exiting.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            print("⚠️ No endCursor found. Exiting.")
            break

        page += 1
        time.sleep(1)

    print(f"\n✅ Completed fetching all valid review pages for {MOVIE_ID}.")

if __name__ == "__main__":
    main()
