import argparse
import json
import shutil
import subprocess
from urllib.parse import urlparse
try:
    import requests
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Missing dependency 'requests'. Install dependencies from the repo root with: "
        "python -m pip install -r requirements.txt"
    ) from e

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

def _is_probably_hls(url, mime_type=None):
    if mime_type and "mpegurl" in mime_type.lower():
        return True
    path = urlparse(url).path.lower()
    return path.endswith(".m3u8") or "m3u8" in path

def _ffprobe_has_audio(filename):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=codec_type",
                "-of",
                "csv=p=0",
                filename,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return None

def _download_hls_with_ffmpeg(url, filename):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg not found in PATH")

    # Remux HLS to MP4 without re-encoding.
    # Note: HLS AAC audio often needs `aac_adtstoasc` when remuxing to MP4.
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    remux_cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-user_agent",
        user_agent,
        "-i",
        url,
        "-map",
        "0",
        "-c",
        "copy",
        "-bsf:a",
        "aac_adtstoasc",
        "-movflags",
        "+faststart",
        filename,
    ]
    subprocess.run(remux_cmd, check=True)

    has_audio = _ffprobe_has_audio(filename)
    if has_audio is False:
        # Fallback: copy video but re-encode audio to AAC for maximum compatibility.
        transcode_audio_cmd = [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-user_agent",
            user_agent,
            "-i",
            url,
            "-map",
            "0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            filename,
        ]
        subprocess.run(transcode_audio_cmd, check=True)

def download_video(url, filename):
    """Download video from URL"""
    try:
        print(f"Downloading {filename}...")

        # HLS playlists (.m3u8) are not MP4 files; use ffmpeg to fetch segments and remux.
        if _is_probably_hls(url):
            try:
                _download_hls_with_ffmpeg(url, filename)
                print(f"Downloaded: {filename}")
                return True
            except FileNotFoundError:
                fallback = filename
                if fallback.lower().endswith(".mp4"):
                    fallback = fallback[:-4] + ".m3u8"
                print(
                    f"\nHLS playlist detected. Install ffmpeg to download this as MP4.\n"
                    f"Saved playlist as: {fallback}\n"
                    f"Then run: ffmpeg -i '{url}' -c copy '{filename}'"
                )
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                with open(fallback, "wb") as f:
                    f.write(response.content)
                return False
            except subprocess.CalledProcessError as e:
                print(f"\nffmpeg failed for {filename}: {e}")
                return False

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()
        if "text/html" in content_type:
            print(f"\nUnexpected content-type for {filename}: {content_type}")
            return False

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        chunks = response.iter_content(chunk_size=8192)
        first_chunk = next(chunks, b"")
        if first_chunk.startswith(b"#EXTM3U"):
            fallback = filename
            if fallback.lower().endswith(".mp4"):
                fallback = fallback[:-4] + ".m3u8"
            with open(fallback, "wb") as f:
                f.write(first_chunk)
                for chunk in chunks:
                    f.write(chunk)
            print(
                f"\nDownloaded an HLS playlist (not an MP4). Saved as: {fallback}\n"
                f"Install ffmpeg and run: ffmpeg -i '{url}' -c copy '{filename}'"
            )
            return False

        with open(filename, 'wb') as f:
            if first_chunk:
                f.write(first_chunk)
                downloaded += len(first_chunk)
            for chunk in chunks:
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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download an IMDb video by ID")
    parser.add_argument("video_id", help="IMDb video ID (e.g., vi59490329)")
    parser.add_argument("--output", help="Output filename (default: <id>_<quality>.mp4)")
    parser.add_argument(
        "--quality",
        help="Preferred quality name (e.g., 1080p). Defaults to best available",
    )
    args = parser.parse_args()

    video_urls, title = get_video_data_graphql(args.video_id)

    if video_urls:
        print(f"Video Title: {title}")
        print("Available video qualities:")
        for i, video in enumerate(video_urls):
            audio_status = "✅ with audio" if video.get('has_audio') else "❌ video only"
            print(f"{i+1}. {video['quality']} ({video['type']}) {audio_status}")

        selected = video_urls[0]
        if args.quality:
            for video in video_urls:
                if video.get("quality") == args.quality:
                    selected = video
                    break

        extension = '.mp4' if 'mp4' in selected.get('type', '') else '.mp4'
        filename = args.output or f"{args.video_id}_{selected['quality']}{extension}"

        print(f"\nDownloading: {selected['quality']} ({'with audio' if selected.get('has_audio') else 'video only'})")
        download_video(selected['url'], filename)
    else:
        print("No video URLs found")

    print("\n💡 Tip: HLS streams (.m3u8) contain audio, MP4 URLs are often video-only")
    print("💡 Install ffmpeg for best results: brew install ffmpeg")
