#!/usr/bin/env python3
"""
Download video information for a specific person from IMDb using NameVideoGalleryPagination
"""
import os
import requests
import json
import time

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "NameVideoGalleryPagination"

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
            "maturityLevel": "INCLUDE_MATURE",
            "nameConstraints": {},
            "titleConstraints": {}
        },
        "first": 50,
        "isInPace": False,
        "locale": "en-US",
        "originalTitleText": False,
        "sort": {
            "by": "DATE",
            "order": "DESC"
        }
    }
    
    # Always include after cursor - create initial cursor for first page
    if after_cursor:
        variables["after"] = after_cursor
    else:
        # Create initial cursor for first page (base64 encoded JSON)
        import base64
        initial_cursor_data = {
            "query": "",
            "startingPosition": 0,
            "sortValue": "9999999999999"
        }
        initial_cursor = base64.b64encode(json.dumps(initial_cursor_data).encode()).decode()
        variables["after"] = initial_cursor
    
    return variables

def fetch_page(person_id, after_cursor=None):
    payload = {
        "query": """query NameVideoGalleryPagination($const: ID!, $after: ID, $first: Int!) {
          name(id: $const) {
            videos(after: $after, first: $first) {
              edges {
                node {
                  id
                  name {
                    value
                  }
                  thumbnail {
                    url
                  }
                  runtime {
                    value
                  }
                  contentType {
                    displayName {
                      value
                    }
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
        "variables": get_variables(person_id, after_cursor)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return {}
    
    return response.json()

def extract_videos(data):
    videos = []
    if ("data" in data and 
        data["data"] and 
        "name" in data["data"] and 
        data["data"]["name"] and 
        "videos" in data["data"]["name"] and 
        data["data"]["name"]["videos"]):
        edges = data["data"]["name"]["videos"].get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            if node:
                video_info = {
                    "id": node.get("id"),
                    "name": node.get("name", {}).get("value"),
                    "contentType": node.get("contentType", {}).get("displayName", {}).get("value"),
                    "runtime": node.get("runtime", {}).get("value"),
                    "thumbnail": {
                        "url": node.get("thumbnail", {}).get("url"),
                        "width": node.get("thumbnail", {}).get("width"),
                        "height": node.get("thumbnail", {}).get("height")
                    }
                }
                
                # Extract primary title info
                primary_title = node.get("primaryTitle", {})
                if primary_title:
                    video_info["primaryTitle"] = {
                        "id": primary_title.get("id"),
                        "title": primary_title.get("titleText", {}).get("text"),
                        "year": primary_title.get("releaseYear", {}).get("year"),
                        "type": primary_title.get("titleType", {}).get("id")
                    }
                    
                    # Extract series info if available
                    series = primary_title.get("series")
                    if series:
                        video_info["series"] = {
                            "title": series.get("series", {}).get("titleText", {}).get("text"),
                            "season": series.get("displayableEpisodeNumber", {}).get("displayableSeason", {}).get("season"),
                            "episode": series.get("displayableEpisodeNumber", {}).get("episodeNumber", {}).get("episodeNumber")
                        }
                
                videos.append(video_info)
    
    return videos

def save_videos_data(videos, person_id, page_num, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, f"videos_page_{page_num}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved videos_page_{page_num}.json")

def main(person_id, max_pages=10, save_files=True):
    after_cursor = None
    folder = f"person_videos_{person_id}"
    all_videos = []
    
    print(f"🎬 Extracting videos for person: {person_id}")
    
    for page in range(1, max_pages + 1):
        print(f"\n📥 Fetching page {page}...")
        data = fetch_page(person_id, after_cursor)

        if ("data" not in data or 
            not data["data"] or 
            "name" not in data["data"] or 
            not data["data"]["name"] or 
            "videos" not in data["data"]["name"] or 
            not data["data"]["name"]["videos"]):
            print(f"❌ Invalid response structure on page {page}")
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            break

        videos = extract_videos(data)
        all_videos.extend(videos)
        
        print(f"🎬 Found {len(videos)} videos on page {page}")
        
        # Show sample videos
        for i, video in enumerate(videos[:3], 1):
            title = video.get("primaryTitle", {}).get("title", "Unknown")
            content_type = video.get("contentType", "Unknown")
            print(f"  {i}. {video.get('name')} ({content_type}) - {title}")
        
        if save_files:
            save_videos_data(videos, person_id, page, folder)

        page_info = data["data"]["name"]["videos"].get("pageInfo", {})
        if not page_info.get("endCursor"):
            print("✅ No more pages.")
            break

        after_cursor = page_info.get("endCursor")
        time.sleep(1)
    
    # Save all videos to a single file
    if save_files and all_videos:
        all_videos_file = os.path.join(folder, f"all_videos_{person_id}.json")
        with open(all_videos_file, "w", encoding="utf-8") as f:
            json.dump(all_videos, f, indent=2, ensure_ascii=False)
        print(f"\n✅ All {len(all_videos)} videos saved to {all_videos_file}")
    
    print(f"\n🎉 Completed! Found {len(all_videos)} videos for {person_id}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract video information for a specific person from IMDb")
    parser.add_argument("person_id", help="IMDb person ID (e.g., nm3229685)")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum pages to fetch")
    parser.add_argument("--no-save", action="store_true", help="Don't save files")
    
    args = parser.parse_args()
    
    main(args.person_id, args.max_pages, not args.no_save)