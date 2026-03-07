# IMDb Movie Scraper

IMDb scraping toolkit for collecting titles, people, reviews, videos, images, trending data, and related metadata.

Live demo:
https://realimdb.netlify.app/

Related published resources:
- Apify actor: `direwolflabs/imdb-deep-crawler`
  https://apify.com/direwolflabs/imdb-deep-crawler
- Kaggle dataset: `IMDB dataset of 600k International movies`
  https://www.kaggle.com/datasets/pavan4kalyan/imdb-dataset-of-600k-international-movies

## What This Repo Includes

- Bulk title scraping with pagination and resume support
- Single-title lookup by IMDb ID
- Search by free text and filters
- People scraping
- Reviews, images, videos, seasons, news, and trending data
- JSON output suitable for downstream pipelines

## Main Workflows

### Bulk Titles

```bash
cd ImdbDataExtraction/pages_dowloader/

# Fetch 5 pages without saving
python3 scrape_all_movie_list.py --max-pages 5

# Save results and continue from the last downloaded page
python3 scrape_all_movie_list.py --save-files --resume --max-pages 100

# Save TV series into a separate folder and start fresh
python3 scrape_all_movie_list.py --save-files --no-resume --output-dir all_imdb_tv_series --title-types tvSeries --max-pages 25
```

For the full page downloader options, see:
[ImdbDataExtraction/pages_dowloader/README.md](/Users/pavankalyanreddythota/Desktop/imdb-movie-scraper/ImdbDataExtraction/pages_dowloader/README.md)

### Search and Lookup

```bash
# Search by IMDb ID
cd ImdbDataExtraction/search_by_id/
python3 search_movie.py tt0944947

# Search by text
cd ../search_by_string/
python3 search_by_string.py "batman" --limit 10

# Search with filters
cd ../search_by_filters/
python3 search_by_filters.py --genre Action --min-rating 7 --pages 2
```

### Trending, People, and Media

```bash
# Trending titles
cd ImdbDataExtraction/trending_downloader/
python3 trending_movies.py --count 10

# Bulk people data
cd ../people_downloader/
python3 scrape_all_people.py --max-pages 3

# Extract videos for a title
cd ../videos_downloader/
python3 extract_video_ids_from_gallery.py
```

## Project Structure

```text
ImdbDataExtraction/
├── pages_dowloader/          # Bulk movie/TV scraping with save and resume
├── search_by_id/             # Detailed single-title lookups
├── search_by_string/         # Text search
├── search_by_filters/        # Filtered title search
├── people_downloader/        # Person and people-media scraping
├── videos_downloader/        # Trailers and video assets
├── images_dowloader/         # Images and posters
├── review_downloader/        # Reviews
├── news_downloader/          # News
├── season_episodes/          # Episode data
├── streaming_availability/   # Streaming info
└── trending_downloader/      # Trending titles and trailers
```

## Installation

```bash
pip install -r requirements.txt
```

Optional:

```bash
brew install ffmpeg
```

`ffmpeg` is only needed for parts of the video download workflow.

## Output

Most scripts write JSON. The bulk page downloader:
- prints results without saving by default
- saves `imdb_page_<n>.json` files when `--save-files` is used
- resumes from the last saved cursor when `--resume` is enabled
- writes to `all_imdb_movies/` by default for the standard movie scrape

## Data Sources

- GraphQL: `https://caching.graphql.imdb.com/`
- Suggestions API: `https://v3.sg.media-imdb.com/suggestion`

## Notes

- This project is intended for educational and research use.
- Respect IMDb rate limits and terms of service.
