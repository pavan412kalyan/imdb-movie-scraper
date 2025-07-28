#!/usr/bin/env python3
"""
Download trending movies from IMDb using GraphQL API
"""
import os
import requests
import json
import time
import argparse

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "Trending"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}

def get_trending_movies(count=8, data_window="HOURS"):
    """Fetch trending movies from IMDb"""
    payload = {
        'query': """query Trending($first: Int!, $input: TopTrendingInput!) {
          topTrendingTitles(first: $first, input: $input) {
            edges {
              node {
                item {
                  id
                  titleText {
                    text
                  }
                  originalTitleText {
                    text
                  }
                  titleType {
                    text
                  }
                  releaseYear {
                    year
                  }
                  releaseDate {
                    day
                    month
                    year
                  }
                  runtime {
                    seconds
                  }
                  ratingsSummary {
                    aggregateRating
                    voteCount
                  }
                  genres {
                    genres {
                      text
                    }
                  }
                  plot {
                    plotText {
                      plainText
                    }
                  }
                  primaryImage {
                    url
                    width
                    height
                  }
                  principalCredits {
                    category {
                      text
                    }
                    credits {
                      name {
                        id
                        nameText {
                          text
                        }
                      }
                      ... on Cast {
                        characters {
                          name
                        }
                      }
                    }
                  }

                }
                rank
              }
            }
          }
        }""",
        'operationName': OPERATION_NAME,
        'variables': {
            "first": count,
            "input": {
                "dataWindow": data_window,
                "trafficSource": "XWW"
            }
        }
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Response: {response.text}")
    response.raise_for_status()
    return response.json()

def extract_movie_ids(data):
    """Extract movie details from trending response"""
    movies = []
    edges = data.get("data", {}).get("topTrendingTitles", {}).get("edges", [])
    
    for edge in edges:
        node = edge.get("node", {})
        item = node.get("item", {})
        
        # Basic info
        movie_id = item.get("id")
        title = item.get("titleText", {}).get("text")
        original_title = item.get("originalTitleText", {}).get("text")
        title_type = item.get("titleType", {}).get("text")
        release_year = item.get("releaseYear", {}).get("year")
        
        # Release date
        release_date = item.get("releaseDate")
        full_release_date = None
        if release_date and isinstance(release_date, dict):
            day = release_date.get("day")
            month = release_date.get("month")
            year = release_date.get("year")
            if year:
                full_release_date = f"{year}-{month or '01'}-{day or '01'}"
        
        # Runtime
        runtime_data = item.get("runtime")
        runtime_seconds = runtime_data.get("seconds") if runtime_data else None
        runtime_minutes = runtime_seconds // 60 if runtime_seconds else None
        
        # Ratings
        ratings = item.get("ratingsSummary")
        rating = ratings.get("aggregateRating") if ratings else None
        vote_count = ratings.get("voteCount") if ratings else None
        
        # Genres
        genres = []
        genre_data = item.get("genres", {})
        if genre_data:
            for genre in genre_data.get("genres", []):
                if genre and genre.get("text"):
                    genres.append(genre.get("text"))
        
        # Plot
        plot_data = item.get("plot", {})
        plot = plot_data.get("plotText", {}).get("plainText") if plot_data else None
        
        # Image
        primary_image = item.get("primaryImage", {})
        poster_url = primary_image.get("url")
        image_width = primary_image.get("width")
        image_height = primary_image.get("height")
        
        # Credits (cast, directors, writers)
        credits_by_category = {}
        principal_credits = item.get("principalCredits", [])
        for credit_group in principal_credits:
            category = credit_group.get("category", {}).get("text", "Unknown")
            credits = credit_group.get("credits", [])
            
            category_credits = []
            for credit in credits:
                name_info = credit.get("name", {})
                name = name_info.get("nameText", {}).get("text")
                name_id = name_info.get("id")
                
                # Character info for cast
                characters = []
                if "characters" in credit:
                    for char in credit.get("characters", []):
                        characters.append(char.get("name"))
                
                if name:
                    credit_info = {
                        "name": name,
                        "id": name_id
                    }
                    if characters:
                        credit_info["characters"] = characters
                    category_credits.append(credit_info)
            
            if category_credits:
                credits_by_category[category] = category_credits
        
        # Keywords - removed due to API limitations
        keywords = []
        
        if movie_id:
            movies.append({
                "id": movie_id,
                "title": title,
                "original_title": original_title,
                "title_type": title_type,
                "release_year": release_year,
                "release_date": full_release_date,
                "runtime_minutes": runtime_minutes,
                "rating": rating,
                "vote_count": vote_count,
                "genres": genres,
                "plot": plot,
                "poster_url": poster_url,
                "image_dimensions": {"width": image_width, "height": image_height} if image_width and image_height else None,
                "credits": credits_by_category,
                "keywords": keywords,
                "rank": node.get("rank")
            })
    
    return movies

def save_trending_data(data, filename):
    """Save trending data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Trending data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Download trending movies from IMDb")
    parser.add_argument("-c", "--count", type=int, default=8, help="Number of trending movies to fetch (default: 8)")
    parser.add_argument("-w", "--window", default="HOURS", choices=["HOURS", "DAYS", "WEEKS"], 
                        help="Data window for trending (default: HOURS)")
    parser.add_argument("-o", "--output", default="trending_movies.json", 
                        help="Output filename (default: trending_movies.json)")
    parser.add_argument("--ids-only", action="store_true", 
                        help="Only extract and display movie IDs")
    
    args = parser.parse_args()
    
    print(f"Fetching top {args.count} trending movies...")
    
    try:
        data = get_trending_movies(count=args.count, data_window=args.window)
        
        if args.ids_only:
            movie_ids = extract_movie_ids(data)
            print("\nTrending Movie IDs:")
            for movie in movie_ids:
                print(f"{movie['rank']}. {movie['id']} - {movie['title']} ({movie.get('release_year', 'N/A')})")
        else:
            save_trending_data(data, args.output)
            
            # Display trending movies
            movie_ids = extract_movie_ids(data)
            print(f"\nTop {len(movie_ids)} Trending Movies:")
            for movie in movie_ids:
                print(f"\n{movie['rank']}. {movie['title']} ({movie['id']})")
                if movie.get('original_title') and movie['original_title'] != movie['title']:
                    print(f"   Original Title: {movie['original_title']}")
                if movie.get('title_type'):
                    print(f"   Type: {movie['title_type']}")
                if movie.get('release_year'):
                    print(f"   Year: {movie['release_year']}")
                if movie.get('runtime_minutes'):
                    print(f"   Runtime: {movie['runtime_minutes']} minutes")
                if movie.get('rating'):
                    print(f"   Rating: {movie['rating']}/10 ({movie.get('vote_count', 0)} votes)")
                if movie.get('genres'):
                    print(f"   Genres: {', '.join(movie['genres'])}")
                if movie.get('plot'):
                    plot_preview = movie['plot'][:100] + "..." if len(movie['plot']) > 100 else movie['plot']
                    print(f"   Plot: {plot_preview}")
                
                # Show credits by category
                credits = movie.get('credits', {})
                for category, people in credits.items():
                    names = [person['name'] for person in people[:3]]  # Show first 3
                    if names:
                        print(f"   {category}: {', '.join(names)}")
                

    
    except Exception as e:
        print(f"Error fetching trending movies: {e}")

if __name__ == "__main__":
    main()