# IMDb Videos Downloader

Tools to extract and download video trailers/clips from IMDb.

## Scripts

- `extract_video_ids_from_gallery.py`  
  Fetches all videos for a title and prints/saves metadata (includes playback URLs).

- `download_video_from_id.py`  
  Fetches playback URLs for a single video ID and downloads the best available stream.

- `bulk_video_downloader.py`  
  Gets all video IDs for a title and downloads them in parallel.

## Usage

From the repo root, install dependencies once:

```bash
python -m pip install -r requirements.txt
```

```bash
# Extract video IDs and metadata for a title
python3 extract_video_ids_from_gallery.py tt0944947 --limit 25 --max-pages 2 --output got_videos.json

# Download a single video by ID
python3 download_video_from_id.py vi59490329 --quality 1080p --output trailer.mp4

# Download all videos for a title (multithreaded)
python3 bulk_video_downloader.py tt0944947 --max-workers 10 --limit 25 --max-pages 2
```

## Notes

- HLS streams (`.m3u8`) typically include audio, MP4 URLs may be video-only.
- If you download an HLS URL without `ffmpeg`, you’ll only save a small playlist file (not a playable `.mp4`).
- For HLS downloads, install `ffmpeg` so the scripts can fetch segments and remux to MP4: `brew install ffmpeg`
- If you get video with no audio, the downloader now uses an `ffmpeg` fallback that re-encodes audio to AAC for compatibility.
