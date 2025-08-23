#!/usr/bin/env python3
"""
Download images for a specific person from IMDb using NameMediaIndexPagination
"""
import os
import requests
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "NameMediaIndexPagination"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    'x-imdb-client-name': 'imdb-web-next-localized',
    'x-imdb-user-country': 'US',
    'x-imdb-user-language': 'en-US'
}

def get_variables(person_id, after_cursor=None):
    variables = {
        "const": person_id,
        "filter": {
            "galleryConstraints": {},
            "nameConstraints": {},
            "titleConstraints": {}
        },
        "first": 50,
        "firstFacets": 250,
        "locale": "en-US",
        "originalTitleText": False
    }
    
    # Only include after cursor if it exists
    if after_cursor:
        variables["after"] = after_cursor
    
    return variables

def fetch_page(person_id, after_cursor=None):
    payload = {
        "query": """query NameMediaIndexPagination($const: ID!, $after: ID, $first: Int!) {
          name(id: $const) {
            images(after: $after, first: $first) {
              edges {
                node {
                  url
                  caption {
                    plainText
                  }
                  width
                  height
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
        "variables": get_variables(person_id, after_cursor)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return {}
    
    return response.json()

def download_image(img_url, folder, caption=""):
    try:
        response = requests.get(img_url, headers={'User-Agent': HEADERS['user-agent']})
        response.raise_for_status()
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded: {filename} - {caption[:50]}...")
    except Exception as e:
        print(f"❌ Failed to download {img_url}: {e}")

def extract_images(data):
    images = []
    if ("data" in data and 
        data["data"] and 
        "name" in data["data"] and 
        data["data"]["name"] and 
        "images" in data["data"]["name"] and 
        data["data"]["name"]["images"]):
        edges = data["data"]["name"]["images"].get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            if "url" in node:
                caption = node.get("caption", {}).get("plainText", "")
                images.append({
                    "url": node["url"],
                    "caption": caption,
                    "width": node.get("width"),
                    "height": node.get("height")
                })
    return images

def main(person_id, max_pages=10):
    after_cursor = None
    folder = f"person_images_{person_id}"
    os.makedirs(folder, exist_ok=True)
    
    print(f"📸 Downloading images for person: {person_id}")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        for page in range(1, max_pages + 1):
            print(f"\n📥 Fetching page {page}...")
            data = fetch_page(person_id, after_cursor)

            if ("data" not in data or 
                not data["data"] or 
                "name" not in data["data"] or 
                not data["data"]["name"] or 
                "images" not in data["data"]["name"] or 
                not data["data"]["name"]["images"]):
                print(f"❌ Invalid response structure on page {page}")
                print(f"Response: {json.dumps(data, indent=2)[:500]}...")
                break

            images = extract_images(data)
            print(f"📸 Found {len(images)} images on page {page}, downloading...")
            
            for img_data in images:
                executor.submit(download_image, img_data["url"], folder, img_data["caption"])

            page_info = data["data"]["name"]["images"].get("pageInfo", {})
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Download images for a specific person from IMDb")
    parser.add_argument("person_id", help="IMDb person ID (e.g., nm0912528)")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum pages to fetch")
    
    args = parser.parse_args()
    
    main(args.person_id, args.max_pages)