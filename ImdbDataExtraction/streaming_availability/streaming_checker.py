from ImdbDataExtraction.utils import GRAPHQL_API_URL, get_graphql_headers
import requests
import json
import argparse

def get_streaming_availability(title_id):
    """Get streaming availability for a single title ID"""
    
    url = GRAPHQL_API_URL
    
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
    
    headers = get_graphql_headers()
    
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