# IMDB Scraper

This repo is for:
1) Scraping content on IMDB website
2) REST API for content of IMDB
   - Static data - hosted on MongoDB
   - Dynamic data - scraping from IMDB on Request

### Link for API and documentation: https://imdb-rest-api.herokuapp.com/

## V2 Scraper

Modern IMDB content scraper using GraphQL APIs for fast and reliable data extraction.

## Features

### 🖼️ Images Downloader
- Download high-quality images with GraphQL pagination
- Multi-threaded downloads for faster processing
- Automatic folder organization

### 🎬 Videos Downloader
- Extract video URLs from IMDB pages
- Single video download by video ID
- Bulk video download with multi-threading
- Video gallery extraction from movie pages

### 📝 Reviews Downloader
- Complete review extraction with pagination
- GraphQL API integration
- Structured JSON output

### 📄 Pages Downloader
- Bulk movie list scraping from search results
- Advanced title search with GraphQL
- Pagination support for large datasets

### 🎭 Movie Info Downloader
- Comprehensive movie metadata extraction
- JSON-LD structured data parsing
- Complete cast, crew, and production details

## Usage

```bash
# Images downloader
cd ImdbScraperV2/images_dowloader/
python3 images_downloader.py

# Video downloader - single video
cd ../videos_downloader/
python3 download_video_from_id.py

# Video downloader - bulk download with threading
python3 bulk_video_downloader.py

# Extract video IDs from movie gallery
python3 extract_video_ids_from_gallery.py

# Reviews downloader
cd ../review_downloader/
python3 reviews.py

# Pages downloader
cd ../pages_dowloader/
python3 scrape_all_movie_list.py

# Movie info downloader
cd ../movie_info_downloader/
python3 download_movie_info.py
```

## Key Improvements

- ✅ **No PERSISTED_QUERY_HASH required**: Uses full GraphQL queries
- ⚡ **Multi-threading support**: Faster downloads with concurrent processing
- 🛡️ **Better error handling**: Robust error handling and retry mechanisms
- 📊 **Comprehensive data**: Extracts all available metadata including JSON-LD
- 🔄 **Pagination support**: Handles large datasets efficiently



## Movie Data API
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





   