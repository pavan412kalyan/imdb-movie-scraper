import requests
import json
import argparse
from ImdbDataExtraction.utils import GRAPHQL_CACHING_URL, get_graphql_headers

def get_trending_trailers(limit=50):
    """Get trending movie trailers from IMDb"""
    
    url = GRAPHQL_CACHING_URL
    
    variables = {
        "limit": limit
    }
    
    query = """
    query Trl_TrendingTitles($limit: Int!) {
      trendingTitles(limit: $limit) {
        titles {
          id
          titleText {
            text
          }
          latestTrailer {
            id
            name {
              value
            }
            runtime {
              value
            }
            description {
              value
            }
            thumbnail {
              url
              width
              height
            }
          }
        }
      }
    }
    """
    
    payload = {
        "operationName": "Trl_TrendingTitles",
        "query": query,
        "variables": variables
    }
    
    headers = get_graphql_headers()
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def extract_trailer_data(data):
    """Extract trailer information from API response"""
    trailers = []
    
    if "data" in data and "trendingTitles" in data["data"]:
        titles = data["data"]["trendingTitles"].get("titles", [])
        
        for title in titles:
            if "latestTrailer" in title and title["latestTrailer"]:
                trailer = title["latestTrailer"]
                trailer_info = {
                    "movie_id": title.get("id"),
                    "movie_title": title.get("titleText", {}).get("text") if title.get("titleText") else None,
                    "trailer_id": trailer.get("id"),
                    "trailer_name": trailer.get("name", {}).get("value") if trailer.get("name") else None,
                    "runtime": trailer.get("runtime", {}).get("value") if trailer.get("runtime") else None,
                    "description": trailer.get("description", {}).get("value") if trailer.get("description") else None,
                    "thumbnail_url": trailer.get("thumbnail", {}).get("url") if trailer.get("thumbnail") else None,
                    "thumbnail_width": trailer.get("thumbnail", {}).get("width") if trailer.get("thumbnail") else None,
                    "thumbnail_height": trailer.get("thumbnail", {}).get("height") if trailer.get("thumbnail") else None
                }
                trailers.append(trailer_info)
    
    return trailers

def main():
    parser = argparse.ArgumentParser(description="Get trending movie trailers from IMDb")
    parser.add_argument("--limit", type=int, default=50, help="Number of trailers to fetch (default: 50)")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    print(f"🎬 Fetching {args.limit} trending trailers...")
    
    data = get_trending_trailers(args.limit)
    
    if data:
        trailers = extract_trailer_data(data)
        
        print(f"✅ Found {len(trailers)} trailers")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(trailers, f, indent=2)
            print(f"💾 Saved to {args.output}")
        else:
            print(json.dumps(trailers, indent=2))
    else:
        print("❌ Failed to fetch trending trailers")

if __name__ == "__main__":
    main()