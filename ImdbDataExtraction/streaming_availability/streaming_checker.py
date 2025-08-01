import requests
import json
import argparse

def get_streaming_availability(title_id):
    """Get streaming availability for a single title ID"""
    
    url = "https://api.graphql.imdb.com/"
    
    variables = {
        "id": title_id
    }
    
    query = """
    query HERO_WATCH_BOX($id: ID!) {
      title(id: $id) {
        primaryWatchOption {
          additionalWatchOptionsCount
          watchOption {
            provider {
              name {
                value
              }
              refTagFragment
            }
            link(platform: WEB)
            title {
              value
            }
            description {
              value
            }
            promoted
          }
        }
        watchOptionsByCategory {
          categorizedWatchOptionsList {
            categoryName {
              value
            }
            watchOptions {
              title {
                value
              }
              shortDescription {
                value
              }
              link(platform: WEB)
              provider {
                id
                logos {
                  slate {
                    url
                    height
                    width
                  }
                }
                refTagFragment
              }
            }
          }
        }
      }
    }
    """
    
    payload = {
        "operationName": "HERO_WATCH_BOX",
        "query": query,
        "variables": variables
    }
    
    headers = {
        "accept": "application/graphql+json, application/json",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36",
        "Referer": "https://www.imdb.com/",
        "x-imdb-user-country": "US",
        "x-imdb-user-language": "en-US"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Check streaming availability for movies")
    parser.add_argument("--title", required=True, help="IMDb title ID (e.g., tt0899043)")
    
    args = parser.parse_args()
    
    result = get_streaming_availability(args.title)
    
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to get streaming data")

if __name__ == "__main__":
    main()