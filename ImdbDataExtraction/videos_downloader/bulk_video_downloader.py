import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from extract_video_ids_from_gallery import get_all_title_videos
from download_video_from_id import extract_video_data, download_video, get_imdb_page

def download_single_video(video_info, output_dir):
    """Download a single video by ID"""
    video_id = video_info['id']
    video_name = video_info['name']
    
    try:
        # Get video page
        video_url = f"https://www.imdb.com/video/{video_id}/"
        html_content = get_imdb_page(video_url)
        
        # Extract download URLs
        video_urls, title = extract_video_data(html_content)
        
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

def download_all_videos(title_id, max_workers=5):
    """Download all videos for a title using multithreading"""
    # Create output directory
    output_dir = f"videos_{title_id}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all video IDs
    print(f"Fetching video list for {title_id}...")
    videos = get_all_title_videos(title_id)
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
    title_id = "tt0944947"  # Game of Thrones
    download_all_videos(title_id, max_workers=25)