#!/usr/bin/env python3
"""
Search movie by IMDb ID and get detailed information
"""
import os
import requests
import json
import argparse

BASE_URL = "https://caching.graphql.imdb.com/"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}

def get_movie_details(movie_id):
    """Get detailed movie information by IMDb ID"""
    payload = {
        'query': """query GetTitle($id: ID!) {
          title(id: $id) {
            id
            titleText {
              text
            }
            originalTitleText {
              text
            }
            titleType {
              text
              id
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
            metacritic {
              metascore {
                score
              }
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
              language {
                id
              }
            }
            primaryImage {
              url
              width
              height
              caption {
                plainText
              }
            }
            imageCount: images {
              total
            }
            videoCount: videos {
              total
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
                attributes {
                  text
                }
              }
            }
            certificate {
              rating
              country {
                text
              }
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
            productionStatus {
              currentProductionStage {
                text
                id
              }
            }
            canHaveEpisodes
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
            episodes {
              episodes {
                total
              }
            }
            titleGenres {
              genres {
                genre {
                  text
                }
              }
            }
            companyCredits {
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
                  }
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



            akas {
              edges {
                node {
                  text
                  country {
                    text
                  }
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
            keywords {
              edges {
                node {
                  text
                }
              }
            }
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
            reviews(first: 1) {
              total
            }
            connections {
              edges {
                node {
                  associatedTitle {
                    id
                    titleText {
                      text
                    }
                    releaseYear {
                      year
                    }
                  }
                  category {
                    text
                  }
                }
              }
            }
            moreLikeThisTitles(first: 5) {
              edges {
                node {
                  id
                  titleText {
                    text
                  }
                  releaseYear {
                    year
                  }
                  ratingsSummary {
                    aggregateRating
                  }
                  primaryImage {
                    url
                  }
                }
              }
            }
            titleGenres {
              genres {
                genre {
                  text
                }
              }
            }
            canRate {
              isRatable
            }
            isAdult
            titleGenres {
              genres {
                genre {
                  text
                }
              }
            }
            nominations {
              total
            }
            canHaveEpisodes
            imageGallery: images(first: 5) {
              edges {
                node {
                  url
                  caption {
                    plainText
                  }
                  width
                  height
                }
              }
            }
            trivia(first: 3) {
              edges {
                node {
                  text {
                    plainText
                  }
                }
              }
            }
            goofs(first: 3) {
              edges {
                node {
                  text {
                    plainText
                  }
                }
              }
            }

          }
        }""",
        'operationName': 'GetTitle',
        'variables': {
            'id': movie_id
        }
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Response: {response.text}")
    response.raise_for_status()
    return response.json()

def format_movie_details(data):
    """Format movie details for display"""
    title_data = data.get("data", {}).get("title", {})
    if not title_data:
        return None
    
    # Basic info
    movie_id = title_data.get("id")
    title = title_data.get("titleText", {}).get("text")
    original_title = title_data.get("originalTitleText", {}).get("text")
    title_type = title_data.get("titleType", {}).get("text")
    release_year = title_data.get("releaseYear", {}).get("year")
    
    # Release date
    release_date = title_data.get("releaseDate")
    full_release_date = None
    if release_date and isinstance(release_date, dict):
        day = release_date.get("day")
        month = release_date.get("month")
        year = release_date.get("year")
        if year:
            full_release_date = f"{year}-{month or '01'}-{day or '01'}"
    
    # Runtime
    runtime_data = title_data.get("runtime")
    runtime_seconds = runtime_data.get("seconds") if runtime_data else None
    runtime_minutes = runtime_seconds // 60 if runtime_seconds else None
    
    # Ratings
    ratings = title_data.get("ratingsSummary")
    rating = ratings.get("aggregateRating") if ratings else None
    vote_count = ratings.get("voteCount") if ratings else None
    
    # Genres
    genres = []
    genre_data = title_data.get("genres")
    if genre_data and isinstance(genre_data, dict):
        for genre in genre_data.get("genres", []):
            if genre and genre.get("text"):
                genres.append(genre.get("text"))
    
    # Plot
    plot_data = title_data.get("plot")
    plot = None
    if plot_data and isinstance(plot_data, dict):
        plot_text = plot_data.get("plotText")
        if plot_text and isinstance(plot_text, dict):
            plot = plot_text.get("plainText")
    
    # Image
    primary_image = title_data.get("primaryImage")
    poster_url = primary_image.get("url") if primary_image else None
    image_width = primary_image.get("width") if primary_image else None
    image_height = primary_image.get("height") if primary_image else None
    
    # Certificate
    cert_data = title_data.get("certificate")
    certificate = cert_data.get("rating") if cert_data else None
    
    # Languages
    languages = []
    lang_data = title_data.get("spokenLanguages")
    if lang_data and isinstance(lang_data, dict):
        for lang in lang_data.get("spokenLanguages", []):
            if lang and lang.get("text"):
                languages.append(lang.get("text"))
    
    # Countries
    countries = []
    country_data = title_data.get("countriesOfOrigin")
    if country_data and isinstance(country_data, dict):
        for country in country_data.get("countries", []):
            if country and country.get("text"):
                countries.append(country.get("text"))
    
    # Production status
    prod_data = title_data.get("productionStatus")
    production_status = None
    if prod_data and isinstance(prod_data, dict):
        stage_data = prod_data.get("currentProductionStage")
        if stage_data and isinstance(stage_data, dict):
            production_status = stage_data.get("text")
    
    # Series info
    is_series = title_data.get("canHaveEpisodes", False)
    series_data = title_data.get("series")
    series_info = series_data.get("series") if series_data else None
    
    episodes_data = title_data.get("episodes")
    episode_count = None
    if episodes_data and isinstance(episodes_data, dict):
        ep_data = episodes_data.get("episodes")
        if ep_data and isinstance(ep_data, dict):
            episode_count = ep_data.get("total")
    
    # Credits
    credits_by_category = {}
    principal_credits = title_data.get("principalCredits", [])
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
                profile_image = name_info.get("primaryImage", {}).get("url") if name_info.get("primaryImage") else None
                credit_info = {
                    "name": name,
                    "id": name_id,
                    "profile_image": profile_image
                }
                if characters:
                    credit_info["characters"] = characters
                category_credits.append(credit_info)
        
        if category_credits:
            credits_by_category[category] = category_credits
    
    # Additional data extraction
    
    # Metacritic score
    metacritic_data = title_data.get("metacritic")
    metascore = None
    if metacritic_data and isinstance(metacritic_data, dict):
        meta_score_data = metacritic_data.get("metascore")
        if meta_score_data and isinstance(meta_score_data, dict):
            metascore = meta_score_data.get("score")
    
    # Image and video counts
    images_data = title_data.get("imageCount")
    image_count = images_data.get("total") if images_data else None
    
    videos_data = title_data.get("videoCount")
    video_count = videos_data.get("total") if videos_data else None
    
    # Company credits
    companies = {}
    company_credits_data = title_data.get("companyCredits")
    if company_credits_data and isinstance(company_credits_data, dict):
        company_credits = company_credits_data.get("edges", [])
        for edge in company_credits:
            if not edge:
                continue
            node = edge.get("node", {})
            if not node:
                continue
            company = node.get("company", {})
            if not company:
                continue
            category_data = node.get("category")
            category = category_data.get("text") if category_data else None
            company_text_data = company.get("companyText")
            company_name = company_text_data.get("text") if company_text_data else None
            company_id = company.get("id")
            
            if category and company_name:
                if category not in companies:
                    companies[category] = []
                companies[category].append({
                    "name": company_name,
                    "id": company_id
                })
    
    # Technical specifications
    tech_specs = title_data.get("technicalSpecifications")
    sound_mixes = []
    aspect_ratios = []
    colorations = []
    
    if tech_specs and isinstance(tech_specs, dict):
        sound_mix_data = tech_specs.get("soundMixes")
        if sound_mix_data and isinstance(sound_mix_data, dict):
            for item in sound_mix_data.get("items", []):
                if item and item.get("text"):
                    sound_mixes.append(item.get("text"))
        
        aspect_ratio_data = tech_specs.get("aspectRatios")
        if aspect_ratio_data and isinstance(aspect_ratio_data, dict):
            for item in aspect_ratio_data.get("items", []):
                if item and item.get("aspectRatio"):
                    aspect_ratios.append(item.get("aspectRatio"))
        
        coloration_data = tech_specs.get("colorations")
        if coloration_data and isinstance(coloration_data, dict):
            for item in coloration_data.get("items", []):
                if item and item.get("text"):
                    colorations.append(item.get("text"))
    
    # Additional comprehensive data
    
    # Meter ranking
    meter_data = title_data.get("meterRanking")
    current_rank = meter_data.get("currentRank") if meter_data else None
    
    # Keywords
    keywords = []
    keyword_data = title_data.get("keywords")
    if keyword_data and isinstance(keyword_data, dict):
        keyword_edges = keyword_data.get("edges", [])
        for edge in keyword_edges[:10]:  # Limit to first 10
            if edge and edge.get("node"):
                keyword_text = edge["node"].get("text")
                if keyword_text:
                    keywords.append(keyword_text)
    
    # Trailer information
    trailer_data = title_data.get("latestTrailer")
    trailer = None
    if trailer_data:
        # Extract playback URLs
        playback_urls = trailer_data.get("playbackURLs", [])
        trailer_url = None
        embed_url = None
        
        for playback in playback_urls:
            if playback and playback.get("url"):
                display_name = playback.get("displayName", {}).get("value", "")
                if "480p" in display_name or "720p" in display_name:
                    trailer_url = playback.get("url")
                    break
        
        # If no specific quality found, use first available
        if not trailer_url and playback_urls:
            trailer_url = playback_urls[0].get("url")
        
        # Create embed URL from trailer URL if available
        if trailer_url:
            embed_url = trailer_url.replace("https://", "https://www.imdb.com/video/embed/")
        
        trailer = {
            "id": trailer_data.get("id"),
            "name": trailer_data.get("name", {}).get("value") if trailer_data.get("name") else None,
            "url": trailer_url,
            "embedUrl": embed_url,
            "thumbnail": trailer_data.get("thumbnail", {}).get("url") if trailer_data.get("thumbnail") else None,
            "duration": trailer_data.get("runtime", {}).get("value") if trailer_data.get("runtime") else None,
            "uploadDate": trailer_data.get("createdDate"),
            "contentType": trailer_data.get("contentType", {}).get("displayName", {}).get("value") if trailer_data.get("contentType") else None
        }
    
    # Reviews count
    reviews_data = title_data.get("reviews")
    review_count = reviews_data.get("total") if reviews_data else None
    
    # Connected titles (sequels, prequels, etc.)
    connections = []
    connection_data = title_data.get("connections")
    if connection_data and isinstance(connection_data, dict):
        connection_edges = connection_data.get("edges", [])
        for edge in connection_edges:
            if edge and edge.get("node"):
                node = edge["node"]
                associated_title = node.get("associatedTitle")
                if associated_title:
                    connections.append({
                        "id": associated_title.get("id"),
                        "title": associated_title.get("titleText", {}).get("text"),
                        "year": associated_title.get("releaseYear", {}).get("year"),
                        "relationship": node.get("category", {}).get("text")
                    })
    
    # More like this titles
    similar_titles = []
    similar_data = title_data.get("moreLikeThisTitles")
    if similar_data and isinstance(similar_data, dict):
        similar_edges = similar_data.get("edges", [])
        for edge in similar_edges[:5]:  # Limit to first 5
            if edge and edge.get("node"):
                node = edge["node"]
                image_data = node.get("primaryImage")
                poster_url = image_data.get("url") if image_data else None
                
                similar_titles.append({
                    "id": node.get("id"),
                    "title": node.get("titleText", {}).get("text"),
                    "year": node.get("releaseYear", {}).get("year"),
                    "rating": node.get("ratingsSummary", {}).get("aggregateRating"),
                    "poster_url": poster_url
                })
    
    # Additional title info
    is_adult = title_data.get("isAdult", False)
    is_ratable = title_data.get("canRate", {}).get("isRatable", False)
    
    # Awards (limited to what's available)
    nominations_data = title_data.get("nominations")
    total_nominations = nominations_data.get("total") if nominations_data else 0
    
    # Image gallery only (videos removed due to API limitations)
    image_gallery = []
    image_data = title_data.get("imageGallery")
    if image_data and isinstance(image_data, dict):
        image_edges = image_data.get("edges", [])
        for edge in image_edges:
            if edge and edge.get("node"):
                node = edge["node"]
                image_gallery.append({
                    "url": node.get("url"),
                    "caption": node.get("caption", {}).get("plainText") if node.get("caption") else None,
                    "width": node.get("width"),
                    "height": node.get("height")
                })
    
    video_gallery = []  # Removed due to API limitations
    
    # Trivia
    trivia_items = []
    trivia_data = title_data.get("trivia")
    if trivia_data and isinstance(trivia_data, dict):
        trivia_edges = trivia_data.get("edges", [])
        for edge in trivia_edges:
            if edge and edge.get("node"):
                text_data = edge["node"].get("text")
                if text_data and text_data.get("plainText"):
                    trivia_items.append(text_data["plainText"])
    
    # Goofs
    goof_items = []
    goof_data = title_data.get("goofs")
    if goof_data and isinstance(goof_data, dict):
        goof_edges = goof_data.get("edges", [])
        for edge in goof_edges:
            if edge and edge.get("node"):
                text_data = edge["node"].get("text")
                if text_data and text_data.get("plainText"):
                    goof_items.append(text_data["plainText"])
    
    # Removed episode navigation fields due to API limitations
    next_ep_info = None
    prev_ep_info = None
    parent_info = None
    
    # Enhanced actors/directors from credits
    enhanced_actors = []
    enhanced_directors = []
    enhanced_creators = []
    
    for credit_group in principal_credits:
        category = credit_group.get("category", {}).get("text", "")
        credits = credit_group.get("credits", [])
        
        for credit in credits:
            name_info = credit.get("name", {})
            name = name_info.get("nameText", {}).get("text")
            name_id = name_info.get("id")
            profile_image = name_info.get("primaryImage", {}).get("url") if name_info.get("primaryImage") else None
            
            if name:
                person_data = {
                    "name": name,
                    "url": f"https://www.imdb.com/name/{name_id}/" if name_id else None,
                    "profile_image": profile_image
                }
                
                if category == "Stars":
                    characters = []
                    if "characters" in credit:
                        for char in credit.get("characters", []):
                            if char.get("name"):
                                characters.append(char.get("name"))
                    person_data["characters"] = characters
                    enhanced_actors.append(person_data)
                elif category == "Director":
                    enhanced_directors.append(person_data)
                elif category in ["Writers", "Creator"]:
                    person_data["type"] = category
                    enhanced_creators.append(person_data)
    
    # Removed problematic fields due to API limitations
    alt_titles = []
    locations = []
    budget = None
    lifetime_gross = None
    worldwide_gross = None
    opening_weekend = None
    
    # AKAs (Also Known As)
    akas = []
    aka_data = title_data.get("akas")
    if aka_data and isinstance(aka_data, dict):
        aka_edges = aka_data.get("edges", [])
        for edge in aka_edges:
            if not edge:
                continue
            node = edge.get("node", {})
            if not node:
                continue
            title_text = node.get("text")
            country_data = node.get("country")
            country_text = country_data.get("text") if country_data else None
            
            if title_text:
                akas.append({
                    "title": title_text,
                    "country": country_text
                })
    
    return {
        "id": movie_id,
        "title": title,
        "original_title": original_title,
        "title_type": title_type,
        "release_year": release_year,
        "release_date": full_release_date,
        "runtime_minutes": runtime_minutes,
        "rating": rating,
        "vote_count": vote_count,
        "metascore": metascore,
        "genres": genres,
        "plot": plot,
        "poster_url": poster_url,
        "image_dimensions": {"width": image_width, "height": image_height} if image_width and image_height else None,
        "image_count": image_count,
        "video_count": video_count,
        "certificate": certificate,
        "languages": languages,
        "countries": countries,
        "production_status": production_status,
        "is_series": is_series,
        "series_info": series_info,
        "episode_count": episode_count,
        "credits": credits_by_category,
        "companies": companies,
        "technical_specs": {
            "sound_mixes": sound_mixes,
            "aspect_ratios": aspect_ratios,
            "colorations": colorations
        },

        "akas": akas,
        "current_rank": current_rank,
        "keywords": keywords,
        "trailer": trailer,
        "review_count": review_count,
        "enhanced_actors": enhanced_actors,
        "enhanced_directors": enhanced_directors,
        "enhanced_creators": enhanced_creators,
        "imdb_url": f"https://www.imdb.com/title/{movie_id}/" if movie_id else None,
        "connections": connections,
        "similar_titles": similar_titles,
        "is_adult": is_adult,
        "is_ratable": is_ratable,
        "total_nominations": total_nominations,
        "image_gallery": image_gallery,
        "trivia_items": trivia_items,
        "goof_items": goof_items

    }

def save_movie_data(movie_data, filename):
    """Save movie data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movie_data, f, indent=2, ensure_ascii=False)
    print(f"Movie data saved to {filename}")

def display_movie_info(movie):
    """Display formatted movie information"""
    print(f"\n{movie['title']} ({movie['id']})")
    print("=" * 50)
    
    if movie.get('original_title') and movie['original_title'] != movie['title']:
        print(f"Original Title: {movie['original_title']}")
    
    if movie.get('title_type'):
        print(f"Type: {movie['title_type']}")
    
    if movie.get('release_year'):
        print(f"Year: {movie['release_year']}")
    
    if movie.get('release_date'):
        print(f"Release Date: {movie['release_date']}")
    
    if movie.get('runtime_minutes'):
        print(f"Runtime: {movie['runtime_minutes']} minutes")
    
    if movie.get('rating'):
        print(f"Rating: {movie['rating']}/10 ({movie.get('vote_count', 0):,} votes)")
    
    if movie.get('certificate'):
        print(f"Certificate: {movie['certificate']}")
    
    if movie.get('genres'):
        print(f"Genres: {', '.join(movie['genres'])}")
    
    if movie.get('languages'):
        print(f"Languages: {', '.join(movie['languages'])}")
    

    
    if movie.get('countries'):
        print(f"Countries: {', '.join(movie['countries'])}")
    
    if movie.get('production_status'):
        print(f"Production Status: {movie['production_status']}")
    
    if movie.get('is_series') and movie.get('episode_count'):
        print(f"Episodes: {movie['episode_count']}")
    
    if movie.get('plot'):
        print(f"\nPlot:\n{movie['plot']}")
    
    # Show credits by category
    credits = movie.get('credits', {})
    for category, people in credits.items():
        names = []
        for person in people[:5]:  # Show first 5
            if person.get('characters'):
                names.append(f"{person['name']} ({', '.join(person['characters'])})")
            else:
                names.append(person['name'])
        if names:
            print(f"\n{category}: {', '.join(names)}")
    
    if movie.get('metascore'):
        print(f"Metascore: {movie['metascore']}/100")
    
    # Movie description (plot) - moved to avoid duplication
    # Already displayed above in the plot section
    
    if movie.get('image_count'):
        print(f"Images: {movie['image_count']}")
    
    if movie.get('video_count'):
        print(f"Videos: {movie['video_count']}")
    
    # Technical specs
    tech_specs = movie.get('technical_specs', {})
    if any(tech_specs.values()):
        print("\nTechnical Specifications:")
        if tech_specs.get('sound_mixes'):
            print(f"  Sound: {', '.join(tech_specs['sound_mixes'])}")
        if tech_specs.get('aspect_ratios'):
            print(f"  Aspect Ratio: {', '.join(tech_specs['aspect_ratios'])}")
        if tech_specs.get('colorations'):
            print(f"  Color: {', '.join(tech_specs['colorations'])}")
    

    
    # Companies
    companies = movie.get('companies', {})
    for category, company_list in companies.items():
        if company_list:
            names = [comp['name'] for comp in company_list[:3]]
            print(f"\n{category}: {', '.join(names)}")
    

    
    # Rankings and keywords
    if movie.get('current_rank'):
        print(f"\nIMDb Rank: #{movie['current_rank']}")
    
    if movie.get('keywords'):
        print(f"\nKeywords: {', '.join(movie['keywords'][:10])}")
    
    # Trailer information
    trailer = movie.get('trailer')
    if trailer:
        print("\nTrailer:")
        if trailer.get('name'):
            print(f"  Name: {trailer['name']}")
        if trailer.get('duration'):
            print(f"  Duration: {trailer['duration']} seconds")
        if trailer.get('url'):
            print(f"  URL: {trailer['url']}")
        if trailer.get('embedUrl'):
            print(f"  Embed URL: {trailer['embedUrl']}")
        if trailer.get('thumbnail'):
            print(f"  Thumbnail: {trailer['thumbnail']}")
        if trailer.get('uploadDate'):
            print(f"  Upload Date: {trailer['uploadDate']}")
        if trailer.get('contentType'):
            print(f"  Content Type: {trailer['contentType']}")
    
    # Review count
    if movie.get('review_count'):
        print(f"\nReviews: {movie['review_count']} total")
    
    # Enhanced cast with characters
    enhanced_actors = movie.get('enhanced_actors', [])
    if enhanced_actors:
        print("\nMain Cast:")
        for actor in enhanced_actors[:5]:
            char_info = f" as {', '.join(actor['characters'])}" if actor.get('characters') else ""
            print(f"  {actor['name']}{char_info}")
    
    # Enhanced directors
    enhanced_directors = movie.get('enhanced_directors', [])
    if enhanced_directors:
        director_names = [d['name'] for d in enhanced_directors]
        print(f"\nDirectors: {', '.join(director_names)}")
    
    # Enhanced creators
    enhanced_creators = movie.get('enhanced_creators', [])
    if enhanced_creators:
        creator_names = [f"{c['name']} ({c.get('type', 'Creator')})" for c in enhanced_creators[:3]]
        print(f"\nCreators: {', '.join(creator_names)}")
    
    # Connected titles
    connections = movie.get('connections', [])
    if connections:
        print("\nConnected Titles:")
        for conn in connections[:5]:
            year_info = f" ({conn['year']})" if conn.get('year') else ""
            relationship = conn.get('relationship', 'Related')
            print(f"  {relationship}: {conn['title']}{year_info} ({conn['id']})")
    
    # Similar titles
    similar_titles = movie.get('similar_titles', [])
    if similar_titles:
        print("\nMore Like This:")
        for similar in similar_titles[:5]:
            year_info = f" ({similar['year']})" if similar.get('year') else ""
            rating_info = f" - {similar['rating']}/10" if similar.get('rating') else ""
            print(f"  {similar['title']}{year_info}{rating_info} ({similar['id']})")
    

    # Awards (limited)
    if movie.get('total_nominations'):
        print(f"\nNominations: {movie['total_nominations']} total")
    
    # Image gallery
    image_gallery = movie.get('image_gallery', [])
    if image_gallery:
        print(f"\nImage Gallery ({len(image_gallery)} images):")
        for i, image in enumerate(image_gallery[:3], 1):
            caption = f" - {image['caption']}" if image.get('caption') else ""
            dimensions = f" ({image['width']}x{image['height']})" if image.get('width') and image.get('height') else ""
            print(f"  {i}. Image{dimensions}{caption}")
    
    # Trivia
    trivia_items = movie.get('trivia_items', [])
    if trivia_items:
        print(f"\nTrivia ({len(trivia_items)} items):")
        for i, trivia in enumerate(trivia_items, 1):
            trivia_preview = trivia[:100] + "..." if len(trivia) > 100 else trivia
            print(f"  {i}. {trivia_preview}")
    
    # Goofs
    goof_items = movie.get('goof_items', [])
    if goof_items:
        print(f"\nGoofs ({len(goof_items)} items):")
        for i, goof in enumerate(goof_items, 1):
            goof_preview = goof[:100] + "..." if len(goof) > 100 else goof
            print(f"  {i}. {goof_preview}")
    
    # Additional flags
    flags = []
    if movie.get('is_adult'):
        flags.append("Adult Content")
    if movie.get('is_ratable'):
        flags.append("User Ratable")
    if flags:
        print(f"\nFlags: {', '.join(flags)}")
    
    if movie.get('imdb_url'):
        print(f"\nIMDb URL: {movie['imdb_url']}")
    
    if movie.get('poster_url'):
        print(f"\nPoster: {movie['poster_url']}")

def main():
    parser = argparse.ArgumentParser(description="Search movie by IMDb ID")
    parser.add_argument("movie_id", help="IMDb movie ID (e.g., tt0111161)")
    parser.add_argument("-o", "--output", help="Output JSON filename")
    parser.add_argument("--json-only", action="store_true", help="Only save JSON, don't display")
    
    args = parser.parse_args()
    
    print(f"Searching for movie: {args.movie_id}")
    
    try:
        data = get_movie_details(args.movie_id)
        movie = format_movie_details(data)
        
        if not movie:
            print("Movie not found or error in response")
            return
        
        if args.output:
            save_movie_data(movie, args.output)
        else:
            # Auto-save with movie ID as filename
            filename = f"{movie['id']}.json"
            save_movie_data(movie, filename)
        
        if not args.json_only:
            display_movie_info(movie)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()