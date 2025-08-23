import requests
import json
import argparse

def get_trending_trailers(limit=50):
    """Get trending movie trailers from IMDb"""
    
    url = "https://caching.graphql.imdb.com/"
    
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
    
    headers = {
        "accept": "application/graphql+json, application/json",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "origin": "https://www.imdb.com",
        "referer": "https://www.imdb.com/",
        "x-imdb-user-country": "US",
        "x-imdb-user-language": "en-US"
    }
    
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
                    "movie_title": title.get("titleText", {}).get("text"),
                    "trailer_id": trailer.get("id"),
                    "trailer_name": trailer.get("name", {}).get("value"),
                    "runtime": trailer.get("runtime", {}).get("value"),
                    "description": trailer.get("description", {}).get("value"),
                    "thumbnail_url": trailer.get("thumbnail", {}).get("url"),
                    "thumbnail_width": trailer.get("thumbnail", {}).get("width"),
                    "thumbnail_height": trailer.get("thumbnail", {}).get("height")
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