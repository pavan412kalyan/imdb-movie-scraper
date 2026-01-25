import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from extract_video_ids_from_gallery import get_all_title_videos
from download_video_from_id import get_video_data_graphql, download_video

def download_single_video(video_info, output_dir):
    """Download a single video by ID"""
    video_id = video_info['id']
    video_name = video_info['name']
    
    try:
        # Fetch playback URLs via GraphQL
        video_urls, _title = get_video_data_graphql(video_id)
        
        if video_urls:
            # Download highest quality
            best_quality = video_urls[0]
            # Clean video name for filename
            clean_name = "".join(c for c in video_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{video_id}_{clean_name}_{best_quality['quality']}.mp4"
            filepath = os.path.join(output_dir, filename)
            
            success = download_video(best_quality['url'], filepath)
            return {'id': video_id, 'name': video_name, 'success': success, 'file': filepath}
        else:
            print(f"No download URLs found for {video_id}")
            return {'id': video_id, 'name': video_name, 'success': False, 'error': 'No URLs'}
            
    except Exception as e:
        print(f"Error downloading {video_id}: {e}")
        return {'id': video_id, 'name': video_name, 'success': False, 'error': str(e)}

def download_all_videos(title_id, max_workers=5, limit=50, max_pages=None):
    """Download all videos for a title using multithreading"""
    # Create output directory
    output_dir = f"videos_{title_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all video IDs
    print(f"Fetching video list for {title_id}...")
    videos = get_all_title_videos(title_id, limit=limit, max_pages=max_pages)
    print(f"Found {len(videos)} videos to download")
    
    # Download with threading
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_video = {
            executor.submit(download_single_video, video, output_dir): video 
            for video in videos
        }
        
        for future in as_completed(future_to_video):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✅ Downloaded: {result['name']}")
            else:
                print(f"❌ Failed: {result['name']} - {result.get('error', 'Unknown error')}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Download Summary:")
    print(f"Total videos: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download all videos for an IMDb title")
    parser.add_argument("title_id", help="IMDb title ID (e.g., tt0944947)")
    parser.add_argument("--max-workers", type=int, default=25, help="Thread pool size")
    parser.add_argument("--limit", type=int, default=50, help="Videos per page")
    parser.add_argument("--max-pages", type=int, help="Maximum pages to fetch")
    args = parser.parse_args()

    download_all_videos(
        args.title_id,
        max_workers=args.max_workers,
        limit=args.limit,
        max_pages=args.max_pages
    )
