import requests
import json

def get_title_videos_page(title_id, after_cursor=None):
    """Get one page of videos for a title using GraphQL API"""
    url = "https://caching.graphql.imdb.com/"
    
    headers = {
        'accept': 'application/graphql+json, application/json',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'origin': 'https://www.imdb.com',
        'referer': 'https://www.imdb.com/',
        'x-imdb-client-name': 'imdb-web-next-localized'
    }
    
    # Use provided cursor or empty string for first page
    cursor = after_cursor if after_cursor is not None else ""
    
    variables = {
        "const": title_id,
        "first": 50,
        "sort": {"by": "DATE", "order": "DESC"},
        "filter": {"nameConstraints": {}, "titleConstraints": {}, "maturityLevel": "INCLUDE_MATURE"}
    }
    
    # Only add after parameter if cursor is provided
    if after_cursor is not None:
        variables["after"] = cursor
    
    query = {
        "query": """query TitleVideoGalleryPagination($const: ID!, $first: Int!, $after: ID, $filter: VideosQueryFilter, $sort: VideoSort) {
          title(id: $const) {
            videoStrip(first: $first, after: $after, filter: $filter, sort: $sort) {
              total
              pageInfo {
                endCursor
              }
              edges {
                position
                node {
                  id
                  contentType {
                    displayName {
                      value
                    }
                  }
                  name {
                    value
                  }
                  primaryTitle {
                    titleText {
                      text
                    }
                  }
                  runtime {
                    value
                  }
                  thumbnail {
                    url
                  }
                }
              }
            }
          }
        }""",
        "operationName": "TitleVideoGalleryPagination",
        "variables": variables
    }
    
    response = requests.post(url, headers=headers, json=query)
    response.raise_for_status()
    return response.json()

def get_all_title_videos(title_id):
    """Get all videos for a title using pagination"""
    all_videos = []
    cursor = None
    
    while True:
        data = get_title_videos_page(title_id, cursor)
        videos = extract_video_ids(data)
        all_videos.extend(videos)
        
        print(f"Fetched {len(videos)} videos, total: {len(all_videos)}")
        
        # Check if there's more data
        try:
            cursor = data['data']['title']['videoStrip']['pageInfo']['endCursor']
            if not cursor or len(videos) == 0:
                break
        except KeyError:
            break
    
    return all_videos

def extract_video_ids(data):
    """Extract video IDs and URLs from GraphQL response"""
    videos = []
    try:
        edges = data['data']['title']['videoStrip']['edges']
        for edge in edges:
            node = edge['node']
            video_info = {
                'id': node['id'],
                'name': node['name']['value'],
                'type': node['contentType']['displayName']['value'],
                'runtime': node.get('runtime', {}).get('value', 0),
                'thumbnail': node.get('thumbnail', {}).get('url', '')
            }
            
            # Get video URLs by making additional request
            video_urls = get_video_urls(node['id'])
            video_info['urls'] = video_urls
            
            videos.append(video_info)
    except KeyError:
        pass
    return videos

def get_video_urls(video_id):
    """Get video playback URLs for a specific video ID"""
    url = "https://caching.graphql.imdb.com/"
    
    headers = {
        'accept': 'application/graphql+json, application/json',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'origin': 'https://www.imdb.com',
        'referer': 'https://www.imdb.com/'
    }
    
    query = {
        "query": """query VideoPlaybackData($const: ID!) {
          video(id: $const) {
            playbackURLs {
              displayName {
                value
              }
              url
            }
          }
        }""",
        "operationName": "VideoPlaybackData",
        "variables": {"const": video_id}
    }
    
    try:
        response = requests.post(url, headers=headers, json=query)
        response.raise_for_status()
        data = response.json()
        
        urls = []
        playback_urls = data.get('data', {}).get('video', {}).get('playbackURLs', [])
        for url_info in playback_urls:
            urls.append({
                'quality': url_info.get('displayName', {}).get('value', 'Unknown'),
                'url': url_info.get('url', '')
            })
        return urls
    except:
        return []

if __name__ == "__main__":
    title_id = "tt0944947"  # Game of Thrones
    
    videos = get_all_title_videos(title_id)
    
    print(f"\nTotal videos found: {len(videos)}")
    for i, video in enumerate(videos[:5]):  # Show first 5 with URLs
        print(f"{i+1}. ID: {video['id']}, Name: {video['name']}, Type: {video['type']}")
        if video.get('urls'):
            for url_info in video['urls']:
                print(f"   - {url_info['quality']}: {url_info['url'][:80]}...")
        print()
    
    # Save to JSON file
    with open(f"{title_id}_videos.json", 'w') as f:
        json.dump(videos, f, indent=2)
    print(f"\nSaved all videos to {title_id}_videos.json")