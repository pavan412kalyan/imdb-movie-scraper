import requests
import json
import argparse

def search_by_genre(target_genre="Action", limit=50, languages=None, min_year=None, max_year=None, min_rating=None, max_rating=None, title_type=None, after_cursor=None):
    """Search movies by genre and other filters using IMDb GraphQL API"""
    
    url = "https://caching.graphql.imdb.com/"
    
    # Build constraints object
    constraints = {}
    
    if target_genre:
        constraints["genreConstraint"] = {"allGenreIds": [target_genre]}
    
    if languages:
        lang_list = languages if isinstance(languages, list) else [languages]
        constraints["languageConstraint"] = {"allLanguages": lang_list}
    
    if min_year or max_year:
        start_date = f"{min_year or 1900}-01-01"
        end_date = f"{max_year or 2030}-12-31"
        constraints["releaseDateConstraint"] = {
            "releaseDateRange": {"start": start_date, "end": end_date}
        }
    
    if min_rating or max_rating:
        rating_range = {}
        if min_rating:
            rating_range["min"] = min_rating
        if max_rating:
            rating_range["max"] = max_rating
        constraints["userRatingsConstraint"] = {"aggregateRatingRange": rating_range}
    
    if title_type:
        constraints["titleTypeConstraint"] = {"anyTitleTypeIds": [title_type]}
    
    variables = {
        "first": limit,
        "sortBy": "POPULARITY"
    }
    if after_cursor:
        variables["after"] = after_cursor
    if constraints:
        variables["constraints"] = constraints
    
    payload = {
        "query": """query AdvancedTitleSearch($first: Int!, $constraints: AdvancedTitleSearchConstraints, $after: String) {
          advancedTitleSearch(first: $first, constraints: $constraints, after: $after) {
            edges {
              node {
                title {
                  id
                  titleText {
                    text
                  }
                  titleType {
                    text
                  }
                  releaseYear {
                    year
                  }
                  ratingsSummary {
                    aggregateRating
                  }
                  genres {
                    genres {
                      text
                    }
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }""",
        "operationName": "AdvancedTitleSearch",
        "variables": variables
    }
    
    headers = {
        "accept": "application/graphql+json, application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"❌ GraphQL errors: {data['errors']}")
        search_data = data.get("data", {}).get("advancedTitleSearch", {})
        return search_data.get("edges", []), search_data.get("pageInfo", {})
    else:
        print(f"❌ Error: {response.status_code}")
        return [], {}

def main():
    parser = argparse.ArgumentParser(description="Search IMDb movies with filters")
    parser.add_argument("--genre", default="Action", help="Genre to filter by")
    parser.add_argument("--limit", type=int, default=100, help="Number of movies to fetch")
    parser.add_argument("--min-year", type=int, help="Minimum release year")
    parser.add_argument("--max-year", type=int, help="Maximum release year")
    parser.add_argument("--min-rating", type=float, help="Minimum IMDb rating")
    parser.add_argument("--max-rating", type=float, help="Maximum IMDb rating")
    parser.add_argument("--type", help="Title type (movie, tvSeries, etc.)")
    parser.add_argument("--languages", nargs="+", help="Language codes (en te hi, etc.)")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch")
    
    args = parser.parse_args()
    
    all_movies = []
    after_cursor = None
    
    for page in range(args.pages):
        movies, page_info = search_by_genre(
            target_genre=args.genre,
            limit=args.limit,
            languages=args.languages,
            min_year=args.min_year,
            max_year=args.max_year,
            min_rating=args.min_rating,
            max_rating=args.max_rating,
            title_type=args.type,
            after_cursor=after_cursor
        )
        
        all_movies.extend(movies)
        
        if not page_info.get("hasNextPage"):
            print(f"No more pages available after page {page + 1}")
            break
            
        after_cursor = page_info.get("endCursor")
        print(f"Page {page + 1}: Found {len(movies)} movies")
    
    print(f"\nTotal found: {len(all_movies)} movies matching filters")
    
    for movie in all_movies:
        title_data = movie.get("node", {}).get("title", {})
        
        # Safe extraction with None checks
        ratings_summary = title_data.get('ratingsSummary') or {}
        rating = ratings_summary.get('aggregateRating', 'N/A')
        
        release_year = title_data.get('releaseYear') or {}
        year = release_year.get('year', 'N/A')
        
        title_type = title_data.get('titleType') or {}
        movie_type = title_type.get('text', 'N/A')
        
        title_text = title_data.get('titleText') or {}
        title = title_text.get('text', 'N/A')
        
        print(f"{title} ({year}) [{movie_type}] - {rating}")

if __name__ == "__main__":
    main()