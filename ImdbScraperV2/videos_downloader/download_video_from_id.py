import json
import re
import requests

def extract_video_data(html_content):
    """Extract video URLs and title from IMDb page HTML"""
    # Find the __NEXT_DATA__ script tag
    pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        return [], None
    
    try:
        data = json.loads(match.group(1))
        video_data = data['props']['pageProps']['videoPlaybackData']['video']
        playback_urls = video_data['playbackURLs']
        title = video_data.get('name', {}).get('value', 'Unknown')
        
        urls = []
        for url_data in playback_urls:
            # Skip HLS streams, look for direct MP4 URLs
            if 'mp4' in url_data.get('videoMimeType', '').lower():
                urls.append({
                    'quality': url_data['displayName']['value'],
                    'url': url_data['url'],
                    'type': url_data['videoMimeType']
                })
        return urls, title
    except (KeyError, json.JSONDecodeError):
        return [], None

def download_video(url, filename):
    """Download video from URL"""
    try:
        print(f"Downloading {filename}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Check if it's actually a video file
        content_type = response.headers.get('content-type', '')
        if 'video' not in content_type and 'octet-stream' not in content_type:
            print(f"Warning: Content type is {content_type}, not a video file")
        
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

def get_imdb_page(url):
    """Fetch IMDb page content"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# Load specific URL
if __name__ == "__main__":
    imdb_url = "https://www.imdb.com/video/vi59490329/"
    video_id = imdb_url.split('/')[-2]  # Extract vi59490329
    
    # Get page content
    html_content = get_imdb_page(imdb_url)
    
    # Extract URLs and title
    video_urls, title = extract_video_data(html_content)
    
    if video_urls:
        print(f"Video Title: {title}")
        print("Available video qualities:")
        for i, video in enumerate(video_urls):
            print(f"{i+1}. {video['quality']} ({video['type']})")
        
        # Download highest quality
        best_quality = video_urls[0]
        filename = f"{video_id}_{best_quality['quality']}.mp4"
        download_video(best_quality['url'], filename)
    else:
        print("No video URLs found")