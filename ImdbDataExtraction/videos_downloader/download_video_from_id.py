import json
import requests

def get_video_data_graphql(video_id):
    """Get video data using GraphQL API"""
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
            id
            name {
              value
            }
            contentType {
              displayName {
                value
              }
            }
            runtime {
              value
            }
            thumbnail {
              url
            }
            playbackURLs {
              displayName {
                value
              }
              url
              videoMimeType
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
        
        video_data = data.get('data', {}).get('video', {})
        if not video_data:
            return [], None
        
        title = video_data.get('name', {}).get('value', 'Unknown')
        playback_urls = video_data.get('playbackURLs', [])
        
        urls = []
        for url_data in playback_urls:
            quality = url_data.get('displayName', {}).get('value', 'Unknown')
            url = url_data.get('url', '')
            mime_type = url_data.get('videoMimeType', '')
            
            # Prefer HLS streams (contain audio) over MP4 (video-only)
            if 'hls' in url.lower() or 'm3u8' in url.lower():
                urls.append({
                    'quality': quality,
                    'url': url,
                    'type': 'application/x-mpegURL',
                    'has_audio': True
                })
            elif 'mp4' in mime_type.lower():
                urls.append({
                    'quality': quality,
                    'url': url,
                    'type': mime_type,
                    'has_audio': False
                })
        
        # Sort to prioritize HLS streams with audio
        urls.sort(key=lambda x: (not x.get('has_audio', False), x.get('quality', '')))
        
        return urls, title
    except Exception as e:
        print(f"Error fetching video data: {e}")
        return [], None

def download_video(url, filename):
    """Download video from URL"""
    try:
        print(f"Downloading {filename}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='', flush=True)
        
        print(f"\nDownloaded: {filename}")
        return True
    except Exception as e:
        print(f"\nError downloading {filename}: {e}")
        return False



# Load specific video ID
if __name__ == "__main__":
    video_id = "vi59490329"  # Game of Thrones Official Series Trailer
    
    # Get video data using GraphQL
    video_urls, title = get_video_data_graphql(video_id)
    
    if video_urls:
        print(f"Video Title: {title}")
        print("Available video qualities:")
        for i, video in enumerate(video_urls):
            audio_status = "✅ with audio" if video.get('has_audio') else "❌ video only"
            print(f"{i+1}. {video['quality']} ({video['type']}) {audio_status}")
        
        # Download best quality (prioritizes audio)
        best_quality = video_urls[0]
        extension = '.mp4' if 'mp4' in best_quality.get('type', '') else '.mp4'
        filename = f"{video_id}_{best_quality['quality']}{extension}"
        
        print(f"\nDownloading: {best_quality['quality']} ({'with audio' if best_quality.get('has_audio') else 'video only'})")
        download_video(best_quality['url'], filename)
    else:
        print("No video URLs found")
        
    print("\n💡 Tip: HLS streams (.m3u8) contain audio, MP4 URLs are often video-only")
    print("💡 Install ffmpeg for best results: brew install ffmpeg")