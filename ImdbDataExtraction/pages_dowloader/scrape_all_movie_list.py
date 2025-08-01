# scrape_all_movie_list.py
import os
import requests
import urllib.parse
import json
import time

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "AdvancedTitleSearch"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i'
}

def get_variables(after_cursor, filters=None, title_types=["movie"]):
    variables = {
        "first": 20,
        "constraints": {
            "titleTypeConstraint": {
                "anyTitleTypeIds": title_types
            }
        }
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables

def fetch_page(after_cursor, filters=None, title_types=["movie"]):
    payload = {
        "query": """query AdvancedTitleSearch($after: String, $first: Int!, $constraints: AdvancedTitleSearchConstraints) {
          advancedTitleSearch(after: $after, first: $first, constraints: $constraints) {
            edges {
              node {
                title {
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
                      id
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
                  metacritic {
                    metascore {
                      score
                    }
                  }
                  principalCredits {
                    category {
                      text
                      id
                    }
                    credits {
                      name {
                        id
                        nameText {
                          text
                        }
                        primaryImage {
                          url
                        }
                      }
                      ... on Cast {
                        characters {
                          name
                        }
                      }
                    }
                  }
                  certificate {
                    rating
                  }
                  spokenLanguages {
                    spokenLanguages {
                      text
                      id
                    }
                  }
                  countriesOfOrigin {
                    countries {
                      text
                      id
                    }
                  }
                  canHaveEpisodes
                  isAdult
                  latestTrailer {
                    id
                    name {
                      value
                    }
                    thumbnail {
                      url
                    }
                    runtime {
                      value
                    }
                    playbackURLs {
                      displayName {
                        value
                      }
                      url
                    }
                    contentType {
                      displayName {
                        value
                      }
                    }
                    createdDate
                  }
                  productionStatus {
                    currentProductionStage {
                      text
                      id
                    }
                  }
                  series {
                    series {
                      id
                      titleText {
                        text
                      }
                      releaseYear {
                        year
                      }
                    }
                  }
                  technicalSpecifications {
                    soundMixes {
                      items {
                        text
                      }
                    }
                    aspectRatios {
                      items {
                        aspectRatio
                      }
                    }
                    colorations {
                      items {
                        text
                      }
                    }
                  }
                  meterRanking {
                    currentRank
                  }
                  reviews(first: 1) {
                    total
                  }
                  keywords(first: 5) {
                    edges {
                      node {
                        text
                        id
                      }
                    }
                  }
                  akas(first: 5) {
                    edges {
                      node {
                        text
                        country {
                          text
                          id
                        }
                      }
                    }
                  }
                  companyCredits(first: 5) {
                    edges {
                      node {
                        company {
                          id
                          companyText {
                            text
                          }
                        }
                        category {
                          text
                          id
                        }
                      }
                    }
                  }
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
            total
          }
        }""",
        "operationName": OPERATION_NAME,
        "variables": get_variables(after_cursor, filters, title_types)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
    response.raise_for_status()
    return response.json()

def extract_titles(data):
    edges = data.get("data", {}).get("advancedTitleSearch", {}).get("edges", [])
    return [edge.get("node", {}).get("title", {}).get("titleText", {}).get("text") for edge in edges if edge.get("node", {}).get("title", {}).get("titleText")]

def get_last_page_info():
    """Find the highest page number and its cursor token"""
    folder = "all_imdb_movies"
    if not os.path.exists(folder):
        return 0, None
    
    import glob
    page_files = glob.glob(os.path.join(folder, "imdb_page_*.json"))
    if not page_files:
        return 0, None
    
    page_numbers = []
    for file in page_files:
        try:
            page_num = int(file.split("_")[-1].split(".")[0])
            page_numbers.append((page_num, file))
        except (ValueError, IndexError):
            continue
    
    if not page_numbers:
        return 0, None
    
    last_page_num, last_file = max(page_numbers, key=lambda x: x[0])
    
    try:
        with open(last_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cursor = data.get("data", {}).get("advancedTitleSearch", {}).get("pageInfo", {}).get("endCursor")
            return last_page_num, cursor
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return last_page_num, None

def main(max_pages=5, save_files=False, start_cursor=None, process_callback=None, start_page=1, resume=True, filters=None, title_types=["movie"]):
    if resume and start_cursor is None:
        last_page, cursor_token = get_last_page_info()
        if last_page > 0:
            print(f"📄 Resuming from page {last_page + 1} (found {last_page} existing pages)")
            if cursor_token:
                print(f"🔗 Using cursor token: {cursor_token[:50]}...")
                start_cursor = cursor_token
                start_page = last_page + 1
            else:
                print("⚠️ No cursor token found, starting fresh")
        else:
            print("🆕 Starting fresh scraping")
    
    after_cursor = start_cursor
    folder = "all_imdb_movies"
    if save_files and not os.path.exists(folder):
        os.makedirs(folder)
    
    page_count = start_page

    for _ in range(max_pages):
        print(f"\n🔎 Fetching page {page_count}...")
        data = fetch_page(after_cursor, filters, title_types)

        if save_files:
            file_path = os.path.join(folder, f"imdb_page_{page_count}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        
        if process_callback and callable(process_callback):
            process_callback(data, page_count)

        titles = extract_titles(data)
        print(f"Fetched {len(titles)} titles")

        page_info = data.get("data", {}).get("advancedTitleSearch", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            print("✅ No more pages.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            print("⚠️ No end cursor found, cannot continue pagination")
            break

        page_count += 1

def create_filters(title_type=None, genres=None, release_year_min=None, release_year_max=None, 
                  rating_min=None, rating_max=None, countries=None, languages=None):
    """Create constraints for AdvancedTitleSearch"""
    constraints = {}
    
    if title_type:
        constraints["titleTypeConstraint"] = {"anyTitleTypeIds": [title_type]}
    
    if genres:
        genre_list = [genres] if isinstance(genres, str) else genres
        constraints["genreSearchConstraint"] = {"excludeGenreIds": genre_list}
    
    if release_year_min or release_year_max:
        start_date = f"{release_year_min}-01-01" if release_year_min else "1900-01-01"
        end_date = f"{release_year_max}-12-31" if release_year_max else "2030-12-31"
        constraints["releaseDateSearchConstraint"] = {"releaseDateRange": {"start": start_date, "end": end_date}}
    
    if rating_min or rating_max:
        rating_range = {}
        if rating_min:
            rating_range["min"] = rating_min
        if rating_max:
            rating_range["max"] = rating_max
        constraints["userRatingsSearchConstraint"] = {"aggregateRatingRange": rating_range}
    
    if countries:
        country_list = [countries] if isinstance(countries, str) else countries
        constraints["originCountrySearchConstraint"] = {"allCountries": country_list}
    
    if languages:
        lang_list = [languages] if isinstance(languages, str) else languages
        constraints["languageSearchConstraint"] = {"allLanguages": lang_list}
    
    return constraints

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape IMDB movie data with filters')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum number of pages to scrape')
    parser.add_argument('--save-files', action='store_true', help='Save data to JSON files')
    parser.add_argument('--resume', action='store_true', default=True, help='Resume from last page')
    parser.add_argument('--title-types', nargs='+', default=['movie'], help='Title types to scrape (movie, tvSeries, etc.)')
    parser.add_argument('--genre', help='Filter by genre')
    parser.add_argument('--year-min', type=int, help='Minimum release year')
    parser.add_argument('--year-max', type=int, help='Maximum release year')
    parser.add_argument('--rating-min', type=float, help='Minimum IMDb rating')
    parser.add_argument('--rating-max', type=float, help='Maximum IMDb rating')
    
    args = parser.parse_args()
    
    main(max_pages=args.max_pages, save_files=args.save_files, resume=args.resume, filters=None, title_types=args.title_types)