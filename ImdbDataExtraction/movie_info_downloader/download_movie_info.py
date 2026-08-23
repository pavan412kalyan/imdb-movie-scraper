import requests
import json
import re

GRAPHQL_URLS = (
    "https://caching.graphql.imdb.com/",
    "https://api.graphql.imdb.com/",
    "https://graphql.imdb.com/",
)
HEADERS = {
    "accept": "application/graphql+json, application/json",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "referer": "https://www.imdb.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def _person_url(person_id):
    return f"https://www.imdb.com/name/{person_id}/" if person_id else None


def _format_date(date_data):
    if not date_data or not date_data.get("year"):
        return None
    parts = [str(date_data["year"])]
    if date_data.get("month"):
        parts.append(f'{date_data["month"]:02d}')
    if date_data.get("month") and date_data.get("day"):
        parts.append(f'{date_data["day"]:02d}')
    return "-".join(parts)


def _format_duration(runtime):
    seconds = (runtime or {}).get("seconds")
    if not seconds:
        return None
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    value = "PT"
    if hours:
        value += f"{hours}H"
    if minutes:
        value += f"{minutes}M"
    if seconds:
        value += f"{seconds}S"
    return value


def _movie_info_from_graphql(movie_id):
    payload = {
        "operationName": "MovieInfo",
        "query": """query MovieInfo($id: ID!) {
          title(id: $id) {
            id
            titleText { text }
            plot { plotText { plainText } }
            primaryImage { url }
            releaseDate { day month year }
            runtime { seconds }
            genres { genres { text } }
            ratingsSummary { aggregateRating voteCount }
            principalCredits {
              category { id text }
              credits { name { id nameText { text } } }
            }
            latestTrailer {
              id
              name { value }
              thumbnail { url }
              runtime { value }
              createdDate
            }
          }
        }""",
        "variables": {"id": movie_id},
    }
    failures = []
    data = None
    for url in GRAPHQL_URLS:
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()
            data = (result.get("data") or {}).get("title")
            if data and (data.get("titleText") or {}).get("text"):
                break
            failures.append(f"{url}: {result.get('errors') or 'title was null'}")
        except (requests.RequestException, ValueError) as exc:
            failures.append(f"{url}: {exc}")
    else:
        raise RuntimeError("IMDb movie-info request failed: " + "; ".join(failures))

    credits = {}
    for group in data.get("principalCredits") or []:
        category = (group.get("category") or {}).get("id")
        credits[category] = [
            {
                "name": (credit.get("name", {}).get("nameText") or {}).get("text"),
                "url": _person_url(credit.get("name", {}).get("id")),
            }
            for credit in group.get("credits") or []
            if credit.get("name")
        ]

    rating = data.get("ratingsSummary") or {}
    trailer = data.get("latestTrailer") or {}
    trailer_id = trailer.get("id")
    return {
        "id": movie_id,
        "title": (data.get("titleText") or {}).get("text"),
        "description": ((data.get("plot") or {}).get("plotText") or {}).get("plainText"),
        "image": (data.get("primaryImage") or {}).get("url"),
        "url": f"https://www.imdb.com/title/{movie_id}/",
        "datePublished": _format_date(data.get("releaseDate")),
        "duration": _format_duration(data.get("runtime")),
        "genre": [genre.get("text") for genre in (data.get("genres") or {}).get("genres", [])],
        "keywords": None,
        "aggregateRating": {
            "ratingValue": rating.get("aggregateRating"),
            "ratingCount": rating.get("voteCount"),
        },
        "actors": credits.get("cast", []),
        "directors": credits.get("director", []),
        "creators": credits.get("writer", []),
        "trailer": {
            "name": (trailer.get("name") or {}).get("value"),
            "url": f"https://www.imdb.com/video/{trailer_id}/" if trailer_id else None,
            "embedUrl": f"https://www.imdb.com/video/{trailer_id}/" if trailer_id else None,
            "thumbnail": (trailer.get("thumbnail") or {}).get("url"),
            "duration": (trailer.get("runtime") or {}).get("value"),
            "uploadDate": trailer.get("createdDate"),
        },
        "review": {},
    }


def get_movie_info(movie_id):
    """Extract movie information from JSON-LD, falling back to GraphQL."""
    imdb_url = f"https://www.imdb.com/title/{movie_id}/"
    response = requests.get(imdb_url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    
    # Find the JSON-LD script tag
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*({.*?})\s*</script>'
    match = re.search(pattern, response.text, re.DOTALL | re.IGNORECASE)
    
    if not match:
        return _movie_info_from_graphql(movie_id)
    
    try:
        data = json.loads(match.group(1))
        
        # Extract all available info from JSON-LD
        info = {
            'id': movie_id,
            'title': data.get('name'),
            'description': data.get('description'),
            'image': data.get('image'),
            'url': data.get('url'),
            'datePublished': data.get('datePublished'),
            'duration': data.get('duration'),
            'genre': data.get('genre', []),
            'keywords': data.get('keywords'),
            'aggregateRating': data.get('aggregateRating', {}),
            'actors': [{'name': actor.get('name'), 'url': actor.get('url')} for actor in data.get('actor', [])],
            'directors': [{'name': director.get('name'), 'url': director.get('url')} for director in data.get('director', [])],
            'creators': [{'name': creator.get('name'), 'url': creator.get('url'), 'type': creator.get('@type')} for creator in data.get('creator', [])],
            'trailer': {
                'name': data.get('trailer', {}).get('name'),
                'url': data.get('trailer', {}).get('url'),
                'embedUrl': data.get('trailer', {}).get('embedUrl'),
                'thumbnail': data.get('trailer', {}).get('thumbnail', {}).get('contentUrl'),
                'duration': data.get('trailer', {}).get('duration'),
                'uploadDate': data.get('trailer', {}).get('uploadDate')
            },
            'review': data.get('review', {})
        }
        
        if info.get("title"):
            return info
    except (AttributeError, KeyError, TypeError, json.JSONDecodeError):
        pass

    return _movie_info_from_graphql(movie_id)

def save_movie_info(movie_info, filename):
    """Save movie info to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movie_info, f, indent=2, ensure_ascii=False)
    print(f"Movie info saved to {filename}")

if __name__ == "__main__":
    # Example movie ID
    movie_id = "tt23849204"
    
    print(f"Fetching movie info for {movie_id}...")
    movie_info = get_movie_info(movie_id)
    
    if movie_info:
        filename = f"{movie_id}_info.json"
        save_movie_info(movie_info, filename)
        
        print(f"\nMovie: {movie_info.get('title')}")
        print(f"Release date: {movie_info.get('datePublished')}")
        print(f"Rating: {movie_info.get('aggregateRating', {}).get('ratingValue')}")
        print(f"Genres: {', '.join(movie_info.get('genre', []))}")
    else:
        print("Failed to extract movie information")
