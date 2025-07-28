#!/usr/bin/env python3
"""
Search movies and people by string query
"""
import requests
import json
import argparse

BASE_URL = "https://v3.sg.media-imdb.com/suggestion"

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://m.imdb.com',
    'priority': 'u=1, i',
    'referer': 'https://m.imdb.com/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}

def search_all(query, limit=20):
    """Search using IMDb suggestion API"""
    # Get first letter for the API endpoint
    first_letter = query[0].lower() if query else 'a'
    
    # Build the suggestion URL
    url = f"{BASE_URL}/{first_letter}/{query}.json"
    params = {'includeVideos': '1'}
    
    print(f"🌐 Sending request to: {url}")
    print(f"📊 Parameters: {params}")
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    print(f"📡 Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Response text: {response.text}")
    
    response.raise_for_status()
    return response.json()

def format_results(data, limit=20):
    """Format search results for display"""
    suggestions = data.get("d", [])
    results = []
    
    for item in suggestions[:limit]:
        if not item:
            continue
            
        item_id = item.get("id", "")
        name = item.get("l", "Unknown")
        rank = item.get("rank", 0)
        description = item.get("s", "")
        year = item.get("y")  # Year for titles
        
        # Determine if it's a title or person based on ID prefix
        if item_id.startswith("tt"):
            # Title (movie/TV show)
            result = {
                "type": "Title",
                "id": item_id,
                "name": name,
                "year": year,
                "description": description,
                "rank": rank,
                "image": item.get("i", {}).get("imageUrl") if item.get("i") else None
            }
        elif item_id.startswith("nm"):
            # Person
            result = {
                "type": "Person",
                "id": item_id,
                "name": name,
                "description": description,
                "rank": rank,
                "image": item.get("i", {}).get("imageUrl") if item.get("i") else None
            }
        else:
            continue
            
        results.append(result)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Search IMDb by string")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--limit", type=int, default=10, help="Number of results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        data = search_all(args.query, args.limit)
        results = format_results(data, args.limit)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n🔍 Search results for '{args.query}':")
            print(f"Found {len(results)} results\n")
            
            for i, result in enumerate(results, 1):
                if result["type"] == "Title":
                    year_str = f" ({result['year']})" if result.get('year') else ""
                    print(f"{i:2d}. 🎬 {result['name']}{year_str}")
                elif result["type"] == "Person":
                    print(f"{i:2d}. 👤 {result['name']}")
                
                print(f"     ID: {result['id']}")
                if result.get('description'):
                    print(f"     📝 {result['description']}")
                print(f"     📊 Rank: {result['rank']}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())