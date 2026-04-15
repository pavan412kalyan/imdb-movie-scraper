import argparse
import os
import requests
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "TitleMediaIndexPagination"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'referer': 'https://www.imdb.com/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-imdb-client-name': 'imdb-web-next-localized',
    'x-imdb-user-country': 'US',
    'x-imdb-user-language': 'en-US'
}

def get_variables(title_id, after_cursor):
    variables = {
        "const": title_id,
        "first": 50
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables

def fetch_page(title_id, after_cursor):
    payload = {
        "query": """query TitleMediaIndexPagination($const: ID!, $first: Int!, $after: ID) {
          title(id: $const) {
            images(first: $first, after: $after) {
              edges {
                node {
                  url
                  caption {
                    plainText
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
        "variables": get_variables(title_id, after_cursor)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return {}
    return response.json()

def download_image(img_url, folder):
    try:
        response = requests.get(img_url, headers={'User-Agent': HEADERS['user-agent']})
        response.raise_for_status()
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"❌ Failed to download {img_url}: {e}")

def extract_images(data):
    images = []
    if "data" in data and "title" in data["data"] and "images" in data["data"]["title"]:
        edges = data["data"]["title"]["images"].get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            if "url" in node:
                images.append(node["url"])
    return images

def main(title_id, max_pages=10000):
    after_cursor = ""
    folder = f"images_{title_id}"
    os.makedirs(folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for page in range(1, max_pages + 1):
            print(f"\n📥 Fetching page {page}...")
            data = fetch_page(title_id, after_cursor)

            if "data" not in data or "title" not in data["data"] or "images" not in data["data"]["title"]:
                print(f"❌ Invalid response structure on page {page}")
                break

            images = extract_images(data)
            print(f"📸 Found {len(images)} images on page {page}, downloading...")

            for img_url in images:
                executor.submit(download_image, img_url, folder)

            page_info = data["data"]["title"]["images"].get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                print("✅ No more pages.")
                break

            after_cursor = page_info.get("endCursor")
            if not after_cursor:
                print("🚫 No endCursor found.")
                break

            time.sleep(1)

    print(f"\n✅ Download complete! Images saved to {folder}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images for an IMDb title")
    parser.add_argument("title_id", help="IMDb title ID (e.g., tt0944947)")
    parser.add_argument("--max-pages", type=int, default=10000, help="Maximum pages to fetch")
    args = parser.parse_args()

    main(args.title_id, args.max_pages)
