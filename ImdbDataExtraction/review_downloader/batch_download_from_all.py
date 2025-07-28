#!/usr/bin/env python3
"""
Batch download reviews from all movies in the all_imdb_movies directory
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from reviews import download_reviews

def extract_movie_ids_from_file(file_path):
    """Extract movie IDs from a single page file"""
    movie_ids = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        edges = data.get("data", {}).get("advancedTitleSearch", {}).get("edges", [])
        for edge in edges:
            if edge and "node" in edge:
                node = edge.get("node", {})
                if node and "title" in node:
                    title = node.get("title", {})
                    if title and "id" in title:
                        movie_ids.append(title["id"])
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return movie_ids

def get_all_movie_ids(directory="all_imdb_movies"):
    """Get all movie IDs from all page files"""
    all_movie_ids = []
    
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        return all_movie_ids
    
    # Get all page files
    page_files = []
    for file_name in os.listdir(directory):
        if file_name.startswith("imdb_page_") and file_name.endswith(".json"):
            page_files.append(file_name)
    
    # Sort by page number
    page_files.sort(key=lambda x: int(x.replace("imdb_page_", "").replace(".json", "")))
    
    print(f"Found {len(page_files)} page files")
    
    for file_name in page_files:
        file_path = os.path.join(directory, file_name)
        page_num = file_name.replace("imdb_page_", "").replace(".json", "")
        print(f"Processing page {page_num}...")
        
        movie_ids = extract_movie_ids_from_file(file_path)
        all_movie_ids.extend(movie_ids)
        print(f"  Found {len(movie_ids)} movies")
    
    print(f"Total movies found: {len(all_movie_ids)}")
    return all_movie_ids

def main():
    parser = argparse.ArgumentParser(description="Batch download reviews from all movies")\n    parser.add_argument("--directory", default="all_imdb_movies", \n                        help="Directory containing IMDb movie JSON files (default: all_imdb_movies)")\n    parser.add_argument("-o", "--output-dir", help="Base output directory (default: reviews)")\n    parser.add_argument("-m", "--max-movies", type=int, help="Maximum number of movies to process")\n    parser.add_argument("-p", "--max-pages", type=int, help="Maximum pages per movie")\n    parser.add_argument("-s", "--sort-by", default="HELPFULNESS_SCORE", \n                        choices=["HELPFULNESS_SCORE", "SUBMIT_DATE", "RATING"],\n                        help="Sort reviews by (default: HELPFULNESS_SCORE)")\n    parser.add_argument("-r", "--sort-order", default="DESC", choices=["ASC", "DESC"],\n                        help="Sort order (default: DESC)")\n    parser.add_argument("-d", "--delay", type=float, default=1,\n                        help="Delay between requests in seconds (default: 1)")\n    parser.add_argument("-w", "--wait", type=float, default=5,\n                        help="Wait time between movies in seconds (default: 5)")\n    parser.add_argument("--resume", action="store_true", help="Resume from where left off")\n    \n    args = parser.parse_args()\n    \n    # Get all movie IDs\n    print("Extracting movie IDs from all page files...")\n    movie_ids = get_all_movie_ids(args.directory)\n    \n    if not movie_ids:\n        print("No movie IDs found. Exiting.")\n        return\n    \n    # Limit movies if specified\n    if args.max_movies:\n        movie_ids = movie_ids[:args.max_movies]\n        print(f"Limited to first {args.max_movies} movies")\n    \n    # Set up output directory\n    output_base = args.output_dir or "reviews"\n    if not os.path.exists(output_base):\n        os.makedirs(output_base)\n    \n    # Process each movie\n    processed = 0\n    skipped = 0\n    \n    for i, movie_id in enumerate(movie_ids, 1):\n        output_folder = os.path.join(output_base, movie_id)\n        \n        # Check if already processed (for resume functionality)\n        if args.resume and os.path.exists(output_folder):\n            # Check if there are any review files\n            existing_files = [f for f in os.listdir(output_folder) if f.startswith("raw_page_")]\n            if existing_files:\n                print(f"[{i}/{len(movie_ids)}] Skipping {movie_id} (already processed)")\n                skipped += 1\n                continue\n        \n        print(f"\\n[{i}/{len(movie_ids)}] Processing {movie_id}...")\n        \n        try:\n            pages = download_reviews(\n                movie_id=movie_id,\n                output_folder=output_folder,\n                max_pages=args.max_pages,\n                sort_by=args.sort_by,\n                sort_order=args.sort_order,\n                delay=args.delay\n            )\n            \n            processed += 1\n            print(f"✅ Downloaded {pages} pages for {movie_id}")\n            \n            # Wait between movies (except for the last one)\n            if i < len(movie_ids):\n                print(f"Waiting {args.wait} seconds before next movie...")\n                time.sleep(args.wait)\n                \n        except Exception as e:\n            print(f"❌ Error processing {movie_id}: {e}")\n            continue\n    \n    print(f"\\n🎉 Batch download completed!")\n    print(f"   Processed: {processed} movies")\n    print(f"   Skipped: {skipped} movies")\n    print(f"   Total: {len(movie_ids)} movies")\n\nif __name__ == "__main__":\n    main()