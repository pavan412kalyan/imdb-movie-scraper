import os
import requests
import urllib.parse
import json
import time
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "TitleVideosPagination"  # pull from DevTools
PERSISTED_QUERY_HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
IMDB_ID = "tt0944947"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'referer': 'https://www.imdb.com/',
    'user-agent': 'Mozilla/5.0',
}

def get_encoded_variables(after_cursor):
    variables = {
        "after": after_cursor,
        "const": IMDB_ID,
        "filter": {},
        "first": 25,
        "locale": "en-US",
    }
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
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return {}
    return response.json()

def extract_videos(data):
    videos = []
    edges = data.get("data", {}).get("title", {}).get("videos", {}).get("edges", [])
    for edge in edges:
        node = edge.get("node", {})
        playback = node.get("playbackURLs", [])
        if playback:
            url = playback[0].get("url")
            if url:
                videos.append(url)
    return videos

def download_video(url, folder, index):
    try:
        r = requests.get(url, headers={'User-Agent': HEADERS['user-agent']})
        r.raise_for_status()
        path = os.path.join(folder, f"video_{index}.mp4")
        with open(path, 'wb') as f:
            f.write(r.content)
        print(f"Downloaded {path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main(max_pages=10):
    after_cursor = ""
    folder = f"videos_{IMDB_ID}"
    os.makedirs(folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=3) as executor:
        page = 1
        index = 1
        while page <= max_pages:
            data = fetch_page(after_cursor)
            if not data:
                break
            videos = extract_videos(data)
            for v in videos:
                executor.submit(download_video, v, folder, index)
                index += 1
            page_info = data.get("data", {}).get("title", {}).get("videos", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            after_cursor = page_info.get("endCursor")
            if not after_cursor:
                break
            page += 1
            time.sleep(1)

if __name__ == "__main__":
    main()
