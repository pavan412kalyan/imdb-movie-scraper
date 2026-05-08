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
- Streaming availability and provider lookup (Netflix, Prime Video, Disney+, and 40+ more)
- JustWatch-style provider → titles search with filters
- JustWatch popular titles by provider and country (direct JustWatch GraphQL API, full catalog)
- Rotten Tomatoes discovery-sidebar title modules, title search, and reviews
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
[ImdbDataExtraction/pages_dowloader/README.md](ImdbDataExtraction/pages_dowloader/README.md)

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

### Streaming Availability

```bash
cd ImdbDataExtraction/streaming_availability/

# Check where a title is streaming (JustWatch-style lookup)
python3 streaming_checker.py --title tt0899043

# All titles on Netflix in the US
python3 titles_by_provider.py netflix

# Movies on Prime Video in the UK with rating >= 7, save to file
python3 titles_by_provider.py amazon_prime_video --country GB --type movie --min-rating 7 --output prime_uk.json

# Disney+ TV series, print as JSON
python3 titles_by_provider.py disney_plus --type tvSeries --json

# List all available providers for a country
python3 titles_by_provider.py --list-all-providers --country US

# Discover which providers carry a specific title
python3 titles_by_provider.py --list-providers tt10919420 --country US
```

Supported short provider names: `netflix`, `amazon_prime_video`, `disney_plus`, `hulu`, `max`, `apple_tv_plus`, `paramount_plus`, `peacock`, `starz`, `roku`, and more. See [streaming_availability/README.md](ImdbDataExtraction/streaming_availability/README.md) for the full provider list and filter options.

### JustWatch

```bash
cd ImdbDataExtraction/justwatch_downloader/

# List available providers for a country
python3 justwatch_popular.py --list-providers --country US
python3 justwatch_popular.py --list-providers --country IN

# Popular titles on Netflix India
python3 justwatch_popular.py --country IN --providers nfx

# Netflix + Prime Video India, IMDb rating >= 7
python3 justwatch_popular.py --country IN --providers nfx amp --min-rating 7

# HBO Max US, movies only, 3 pages, save to file
python3 justwatch_popular.py --country US --providers hoc --type MOVIE --pages 3 --output hbo_us.json

# Disney+ TV series in the UK, print as JSON
python3 justwatch_popular.py --country GB --providers dnp --type SHOW --json
```

Common provider short names: `nfx` (Netflix), `amp` (Prime Video), `hoc` (HBO Max), `dnp` (Disney+), `hlu` (Hulu), `ppe` (Apple TV+), `pct` (Paramount+). See [justwatch_downloader/README.md](ImdbDataExtraction/justwatch_downloader/README.md) for the full list.

> Unlike the IMDb streaming availability scripts, this uses the JustWatch

### Rotten Tomatoes

```bash
cd ImdbDataExtraction/rottentomatoes_downloader/

# Discovery sidebar: TV series currently airing
python3 rt_discovery_sidebar.py

# Save airing TV series to JSON
python3 rt_discovery_sidebar.py --media-type tvSeries --status AIRING --output rt_airing_tv.json

# Print the raw cnapi response
python3 rt_discovery_sidebar.py --raw --json

# URL-based title extraction
python3 rt_title_page.py https://www.rottentomatoes.com/tv/margos_got_money_troubles --json

# Rotten Tomatoes site search
python3 rt_search.py "finding nemo" --hits-per-page 5 --json

# Rotten Tomatoes reviews
python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type critic --limit 25 --output finding_nemo_critics.json
python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type audience --limit 50 --output finding_nemo_audience.json

# Rotten Tomatoes reviews from an IMDb title ID
python3 rt_reviews_by_imdb.py tt0266543 --show-candidates
python3 rt_reviews_by_imdb.py tt0266543 --type critic --limit 25 --output finding_nemo_rt_critics.json
```

### Trending, People, and Media

```bash
# Top chart titles
cd ImdbDataExtraction/chart_downloader/
python3 chart_titles.py --chart top

# IMDb list titles
python3 list_titles.py ls039852437

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
├── chart_downloader/         # IMDb chart pages like Top 250 and popularity charts
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
├── streaming_availability/   # Streaming availability and provider lookup via IMDb
├── justwatch_downloader/     # Popular titles by provider via JustWatch
├── rottentomatoes_downloader/ # Rotten Tomatoes cnapi modules, title pages, search, reviews
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

## Notes

- This project is intended for educational and research use.
- Respect IMDb rate limits and terms of service.
