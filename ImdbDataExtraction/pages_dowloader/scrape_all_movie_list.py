# scrape_all_movie_list.py
import os  # Add this for folder creation
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

def get_variables(after_cursor):
    variables = {
        "first": 20
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables

def fetch_page(after_cursor):
    payload = {
        "query": """query AdvancedTitleSearch($after: String, $first: Int!) {
          advancedTitleSearch(after: $after, first: $first) {
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
        "variables": get_variables(after_cursor)
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def extract_titles(data):
    edges = data.get("data", {}).get("advancedTitleSearch", {}).get("edges", [])
    return [edge.get("node", {}).get("title", {}).get("titleText", {}).get("text") for edge in edges if edge.get("node", {}).get("title", {}).get("titleText")]

def main(max_pages=5, save_files=False, start_cursor=None, process_callback=None, start_page=1):
    after_cursor = start_cursor

    # 📁 Create folder if saving is enabled
    folder = "all_imdb_movies"
    if save_files and not os.path.exists(folder):
        os.makedirs(folder)
    
    # Use the provided start_page
    page_count = start_page

    for _ in range(max_pages):
        print(f"\n🔎 Fetching page {page_count}...")
        data = fetch_page(after_cursor)

        if save_files:
            file_path = os.path.join(folder, f"imdb_page_{page_count}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        
        # Call the callback if provided
        if process_callback and callable(process_callback):
            process_callback(data, page_count)

        titles = extract_titles(data)
        # for i, title in enumerate(titles, start=1):
        #     print(f"{i}. {title}")
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

if __name__ == "__main__":
    main(max_pages=10000000, save_files=True)