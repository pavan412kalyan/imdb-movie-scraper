# IMDB Scraper

This repo is for:
1) Scraping content on IMDB website
2) REST API for content of IMDB
   - Static data - hosted on MongoDB
   - Dynamic data - scraping from IMDB on Request

### Link for API and documentation: https://imdb-rest-api.herokuapp.com/
# IMDb Data Extraction Tools

Comprehensive IMDb scraping and data extraction toolkit for:
1) **Data Extraction**: Scraping content from IMDb website using modern GraphQL APIs
2) **REST API**: Legacy API for IMDb content
   - Static data - hosted on MongoDB
   - Dynamic data - scraping from IMDb on Request

### Link for API and documentation: https://imdb-rest-api.herokuapp.com/

## IMDb Data Extraction Tools (ImdbDataExtraction)

Modern IMDb data extraction toolkit using GraphQL APIs for fast and reliable scraping.

## Features

### 🎬 Movie & TV Data
- **Pages Downloader**: Bulk movie/TV show scraping with pagination
- **Movie Info**: Detailed metadata extraction by ID
- **Search by String**: Find movies and people by search terms
- **Trending Movies**: Get currently trending content

### 👥 People Data
- **People Downloader**: Bulk celebrity/crew data extraction
- **Search by ID**: Get detailed person information

### 🎥 Media Content
- **Video Downloader**: Extract and download video trailers/clips
- **Video Gallery**: Get all videos from movie/show pages
- **Images Downloader**: High-quality poster and still downloads
- **Reviews Downloader**: Complete review extraction

## Usage

### Movie & TV Data
```bash
# Get bulk movie data (20 movies per page)
cd ImdbDataExtraction/pages_dowloader/
python3 scrape_all_movie_list.py --max-pages 5

# Search for specific movie
cd ../search_by_id/
python3 search_movie.py tt0944947  # Game of Thrones

# Search by text
cd ../search_by_string/
python3 search_by_string.py "batman" --limit 10

# Get trending movies
cd ../trending_downloader/
python3 trending_movies.py --count 10
```

### People Data
```bash
# Get bulk people data
cd people_downloader/
python3 scrape_all_people.py --max-pages 3
```

### Video Content
```bash
# Extract all videos from a movie
cd videos_downloader/
python3 extract_video_ids_from_gallery.py

# Download specific video
python3 download_video_from_id.py
```

## Key Improvements

- ✅ **GraphQL APIs**: Direct API access (no HTML parsing)
- ⚡ **Pagination**: Handle large datasets efficiently
- 🛡️ **Rate Limiting**: Built-in delays to avoid blocking
- 📊 **Comprehensive Data**: Movies, people, videos, images, reviews
- 🔍 **Search Capabilities**: Text search, ID lookup, trending content
- 📝 **JSON Output**: Structured data format
- 🎯 **Multiple Endpoints**: GraphQL + Suggestions API

## Project Structure

```
ImdbDataExtraction/
├── pages_dowloader/           # Movie/TV bulk scraping
├── search_by_id/              # Individual lookups
├── search_by_string/          # Text-based search
├── people_downloader/         # Celebrity/crew data
├── videos_downloader/         # Video content
├── images_dowloader/          # Image content
├── review_downloader/         # Review extraction
└── trending_downloader/       # Trending content
```

## Installation

```bash
# Install dependencies
pip install requests

# Optional: For video downloads
brew install ffmpeg  # macOS
```



## API Endpoints

- **GraphQL**: `https://caching.graphql.imdb.com/`
- **Suggestions**: `https://v3.sg.media-imdb.com/suggestion`

## Data Output Examples

### Movie Data
```json
{
  "id": "tt0944947",
  "title": "Game of Thrones",
  "year": 2011,
  "rating": 9.2,
  "genres": ["Action", "Adventure", "Drama"],
  "cast": [...],
  "videos": [...]
}
```

### Person Data
```json
{
  "id": "nm0001191",
  "name": "Adam Sandler",
  "professions": ["Actor", "Producer"],
  "knownFor": [...],
  "birthDate": "1966-09-09"
}
```

## Legacy Movie Data API
id -->  ImdbId Example -  tt4154796
lan --> telugu,tamil,upcoming
```
Endpoint                     Methods  Rule
---------------------------  -------  --------------------------------------
home                         GET      /
ScrapMovieNow                GET      /api/livescraper/movie/<id>
SearchById                   GET      /api/imdbid/<id>
SearchImagesById             GET      /api/images/<id>
genre                        GET      /api/genre/<genre>
movie                        GET      /api/movie/<movie>
scrapeReviewsNow             GET      /api/livescraper/reviews/<id>
scrapeReviewsNowAndDownload  GET      /api/livescraper/download/reviews/<id>
scrapeSearchByTitle          GET      /api/livescraper/title/<title>
scrapeTvshow                 GET      /api/livescraper/tv/<id>
scrapeTvshowAndDownload      GET      /api/livescraper/download/tv/<id>
trendingIndia                GET      /api/livescraper/trendingIndia/<lan>
```

## Legal Notice

This tool is for educational and research purposes. Respect IMDb's terms of service and rate limits.





   