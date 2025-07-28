import requests
import json
import re

def get_movie_info(movie_id):
    """Extract movie information from IMDb page"""
    imdb_url = f"https://www.imdb.com/title/{movie_id}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(imdb_url, headers=headers)
    response.raise_for_status()
    
    # Find the JSON-LD script tag
    pattern = r'<script type="application/ld\+json">\s*({.*?})\s*</script>'
    match = re.search(pattern, response.text, re.DOTALL)
    
    if not match:
        return None
    
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
        
        return info
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing data: {e}")
        return None

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
        print(f"Year: {movie_info.get('year')}")
        print(f"Rating: {movie_info.get('rating')}")
        print(f"Genres: {', '.join(movie_info.get('genres', []))}")
    else:
        print("Failed to extract movie information")