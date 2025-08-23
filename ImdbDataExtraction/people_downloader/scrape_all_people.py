#!/usr/bin/env python3
"""
Scrape all people/names from IMDb using AdvancedNameSearch
"""
import os
import requests
import json
import time
import urllib.parse

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "AdvancedNameSearch"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}

def get_variables(after_cursor=None):
    variables = {
        "explicitContentConstraint": {
            "explicitContentFilter": "INCLUDE_ADULT"
        },
        "first": 50,
        "locale": "en-US",
        "originalTitleText": False,
        "refTagQueryParam": "ref_=sr",
        "sortBy": "POPULARITY",
        "sortOrder": "ASC"
    }
    
    if after_cursor:
        variables["after"] = after_cursor
    
    return variables



def fetch_page(after_cursor=None):
    payload = {
        "query": """query AdvancedNameSearch($after: String, $first: Int!) {
          advancedNameSearch(after: $after, first: $first) {
            edges {
              node {
                name {
                  id
                  nameText {
                    text
                  }
                  primaryImage {
                    url
                    width
                    height
                  }
                  primaryProfessions {
                    category {
                      text
                      id
                    }
                  }
                  knownFor(first: 5) {
                    edges {
                      node {
                        title {
                          id
                          titleText {
                            text
                          }
                          releaseYear {
                            year
                          }
                          titleType {
                            text
                          }
                          ratingsSummary {
                            aggregateRating
                          }
                        }
                      }
                    }
                  }
                  birthDate {
                    dateComponents {
                      day
                      month
                      year
                    }
                  }
                  deathDate {
                    dateComponents {
                      day
                      month
                      year
                    }
                  }
                  birthLocation {
                    text
                  }
                  height {
                    measurement {
                      value
                      unit
                    }
                  }
                  bio {
                    text {
                      plainText
                    }
                  }
                  trivia(first: 5) {
                    edges {
                      node {
                        text {
                          plainText
                        }
                      }
                    }
                  }
                  quotes(first: 3) {
                    edges {
                      node {
                        text {
                          plainText
                        }
                      }
                    }
                  }
                  nickNames(limit: 5) {
                    text
                  }
                  akas(first: 10) {
                    edges {
                      node {
                        text
                      }
                    }
                  }
                  meterRanking {
                    currentRank
                    rankChange {
                      changeDirection
                      difference
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
        "variables": {
            "first": 50
        }
    }
    
    if after_cursor:
        payload["variables"]["after"] = after_cursor
    
    print(f"🌐 Requesting page with cursor: {after_cursor or '[first page]'}")
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"❌ Status Code: {response.status_code}")
        print(f"❌ Response: {response.text}")
    
    response.raise_for_status()
    return response.json()

def extract_people(data):
    """Extract people names from the response"""
    try:
        edges = data.get("data", {}).get("advancedNameSearch", {}).get("edges", [])
        people = []
        
        for edge in edges:
            if not edge or not edge.get("node"):
                continue
                
            node = edge["node"]
            if not node or not node.get("name"):
                continue
                
            name_data = node.get("name", {})
            if not name_data or not name_data.get("nameText"):
                continue
                
            name_text = name_data.get("nameText", {}).get("text")
            if not name_text:
                continue
            
            # Extract professions
            professions = []
            prof_data = name_data.get("primaryProfessions", [])
            if prof_data:
                for prof in prof_data:
                    if prof and prof.get("category", {}) and prof.get("category", {}).get("text"):
                        professions.append({
                            "text": prof["category"]["text"],
                            "id": prof["category"].get("id")
                        })
            
            # Extract known for titles
            known_for = []
            kf_data = name_data.get("knownFor", {})
            if kf_data and kf_data.get("edges"):
                for kf_edge in kf_data.get("edges", []):
                    if kf_edge and kf_edge.get("node") and kf_edge.get("node", {}).get("title"):
                        title = kf_edge["node"]["title"]
                        known_for.append({
                            "id": title.get("id"),
                            "title": title.get("titleText", {}).get("text") if title.get("titleText") else None,
                            "year": title.get("releaseYear", {}).get("year") if title.get("releaseYear") else None,
                            "type": title.get("titleType", {}).get("text") if title.get("titleType") else None,
                            "rating": title.get("ratingsSummary", {}).get("aggregateRating") if title.get("ratingsSummary") else None
                        })
            
            # Extract birth/death dates
            birth_date = None
            birth_data = name_data.get("birthDate")
            if birth_data and birth_data.get("dateComponents"):
                date_comp = birth_data.get("dateComponents")
                year = date_comp.get('year')
                month = date_comp.get('month', 1)
                day = date_comp.get('day', 1)
                if year:
                    birth_date = f"{year}-{month:02d}-{day:02d}"
            
            death_date = None
            death_data = name_data.get("deathDate")
            if death_data and death_data.get("dateComponents"):
                date_comp = death_data.get("dateComponents")
                year = date_comp.get('year')
                month = date_comp.get('month', 1)
                day = date_comp.get('day', 1)
                if year:
                    death_date = f"{year}-{month:02d}-{day:02d}"
            
            # Extract image with dimensions
            primary_image = name_data.get("primaryImage")
            image_info = None
            if primary_image:
                image_info = {
                    "url": primary_image.get("url"),
                    "width": primary_image.get("width"),
                    "height": primary_image.get("height")
                }
            
            # Extract birth location safely
            birth_location = None
            birth_loc_data = name_data.get("birthLocation")
            if birth_loc_data and birth_loc_data.get("text"):
                birth_location = birth_loc_data.get("text")
            
            # Extract height
            height = None
            height_data = name_data.get("height")
            if height_data and height_data.get("measurement"):
                measurement = height_data["measurement"]
                value = measurement.get("value")
                unit = measurement.get("unit")
                if value and unit:
                    height = f"{value} {unit}"
            
            # Extract bio
            bio = None
            bio_data = name_data.get("bio")
            if bio_data and bio_data.get("text") and bio_data.get("text").get("plainText"):
                bio = bio_data["text"]["plainText"]
            
            # Extract trivia
            trivia = []
            trivia_data = name_data.get("trivia", {})
            if trivia_data and trivia_data.get("edges"):
                for trivia_edge in trivia_data.get("edges", []):
                    if trivia_edge and trivia_edge.get("node") and trivia_edge.get("node").get("text"):
                        trivia_text = trivia_edge["node"]["text"].get("plainText")
                        if trivia_text:
                            trivia.append(trivia_text)
            
            # Extract quotes
            quotes = []
            quotes_data = name_data.get("quotes", {})
            if quotes_data and quotes_data.get("edges"):
                for quote_edge in quotes_data.get("edges", []):
                    if quote_edge and quote_edge.get("node") and quote_edge.get("node").get("text"):
                        quote_text = quote_edge["node"]["text"].get("plainText")
                        if quote_text:
                            quotes.append(quote_text)
            
            # Extract nicknames
            nicknames = []
            nicknames_data = name_data.get("nickNames", [])
            if nicknames_data:
                for nickname in nicknames_data:
                    if nickname and nickname.get("text"):
                        nicknames.append(nickname["text"])
            
            # Extract alternative names (akas)
            akas = []
            akas_data = name_data.get("akas", {})
            if akas_data and akas_data.get("edges"):
                for aka_edge in akas_data.get("edges", []):
                    if aka_edge and aka_edge.get("node") and aka_edge.get("node").get("text"):
                        akas.append(aka_edge["node"]["text"])
            
            # Extract meter ranking
            meter_ranking = None
            ranking_data = name_data.get("meterRanking")
            if ranking_data:
                rank_change = ranking_data.get("rankChange", {})
                meter_ranking = {
                    "currentRank": ranking_data.get("currentRank"),
                    "changeDirection": rank_change.get("changeDirection") if rank_change else None,
                    "difference": rank_change.get("difference") if rank_change else None
                }
            
            people.append({
                "id": name_data.get("id"),
                "name": name_text,
                "primaryImage": image_info,
                "professions": professions,
                "knownFor": known_for,
                "birthDate": birth_date,
                "deathDate": death_date,
                "birthLocation": birth_location,
                "height": height,
                "bio": bio,
                "trivia": trivia,
                "quotes": quotes,
                "nicknames": nicknames,
                "akas": akas,
                "meterRanking": meter_ranking
            })
        
        print(f"  Successfully extracted {len(people)} people")
        return people
    
    except Exception as e:
        print(f"❌ Error extracting people data: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_page_data(data, page_num, folder="all_imdb_people"):
    """Save raw page data to JSON file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, f"people_page_{page_num}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved people_page_{page_num}.json")

def main(max_pages=5, save_files=True, start_cursor=None, start_page=1):
    after_cursor = start_cursor
    page_count = start_page
    total_people = 0

    for _ in range(max_pages):
        try:
            print(f"\n📄 Fetching page {page_count}...")
            data = fetch_page(after_cursor)
            
            # Check for errors
            if "errors" in data:
                print("❌ Response contains errors:")
                for error in data["errors"]:
                    print(f"  - {error.get('message', 'Unknown error')}")
                break
            
            if save_files:
                save_page_data(data, page_count)
            
            # Extract people info
            people = extract_people(data)
            total_people += len(people)
            
            print(f"📊 Fetched {len(people)} people (Total: {total_people})")
            
            # Show sample people
            if people:
                for i, person in enumerate(people[:3], 1):
                    print(f"  {i}. {person['name']} ({person['id']})")
            else:
                print("  No people extracted - checking data structure...")
                edges = data.get("data", {}).get("advancedNameSearch", {}).get("edges", [])
                print(f"  Found {len(edges)} edges in response")
                if edges:
                    first_edge = edges[0]
                    print(f"  First edge structure: {list(first_edge.keys()) if first_edge else 'None'}")
                    if first_edge and first_edge.get("node"):
                        node = first_edge["node"]
                        print(f"  Node structure: {list(node.keys()) if node else 'None'}")
                        if node and node.get("name"):
                            name_data = node["name"]
                            print(f"  Name data structure: {list(name_data.keys()) if name_data else 'None'}")
            
            # Check pagination
            page_info = data.get("data", {}).get("advancedNameSearch", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                print("✅ No more pages available.")
                break
            
            after_cursor = page_info.get("endCursor")
            if not after_cursor:
                print("⚠️ No end cursor found, cannot continue pagination")
                break
            
            page_count += 1
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error on page {page_count}: {e}")
            break
    
    print(f"\n🎉 Completed! Fetched {total_people} people across {page_count - start_page + 1} pages")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape people from IMDb")
    parser.add_argument("--max-pages", type=int, default=10, help="Maximum pages to fetch")
    parser.add_argument("--no-save", action="store_true", help="Don't save files")
    parser.add_argument("--start-page", type=int, default=1, help="Starting page number")
    
    args = parser.parse_args()
    
    main(
        max_pages=args.max_pages,
        save_files=not args.no_save,
        start_page=args.start_page
    )