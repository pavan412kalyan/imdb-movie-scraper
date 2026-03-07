# IMDb Pages Downloader

Scrape comprehensive movie and TV show data from IMDb using their GraphQL API.

## Usage

### Basic Commands

```bash
# Scrape movies (default)
python3 scrape_all_movie_list.py --save-files --max-pages 100

# Scrape TV series
python3 scrape_all_movie_list.py --title-types tvSeries --save-files --max-pages 100

# Scrape both movies and TV series
python3 scrape_all_movie_list.py --title-types movie tvSeries --save-files --max-pages 100

# Scrape all content types
python3 scrape_all_movie_list.py --title-types movie tvSeries tvMiniSeries tvSpecial tvShort --save-files --max-pages 100

# Filter by genre, year, and rating
python3 scrape_all_movie_list.py --genre Action --year-min 2015 --rating-min 7 --save-files

# Scrape non-default title types into a specific folder without resuming
python3 scrape_all_movie_list.py --title-types tvSeries --output-dir all_imdb_tv_series --no-resume --save-files
```

### Available Title Types

- `movie` - Feature films
- `tvSeries` - TV series
- `tvMiniSeries` - Mini series
- `tvSpecial` - TV specials
- `tvShort` - TV shorts
- `short` - Short films
- `video` - Videos
- `tvMovie` - TV movies

### Command Line Options

- `--title-types` - Specify content types to scrape (default: movie)
- `--max-pages` - Maximum pages to scrape (default: 5)
- `--page-size` - Titles per page (default: 20)
- `--save-files` - Save data to JSON files
- `--output-dir` - Save output to a custom directory
- `--resume` - Resume from the last saved page (default: True)
- `--no-resume` - Force a fresh scrape from page 1
- `--start-cursor` - Start from a specific pagination cursor
- `--start-page` - Set the displayed starting page number
- `--genre` - Require one or more genre IDs
- `--year-min` / `--year-max` - Filter by release year range
- `--rating-min` / `--rating-max` - Filter by IMDb rating range
- `--countries` - Require one or more country IDs
- `--languages` - Require one or more language IDs
- `--request-delay` - Delay between page requests in seconds
- `--timeout` - HTTP timeout in seconds


### Output

Default movie output is saved to `all_imdb_movies/` as:
- `imdb_page_1.json`
- `imdb_page_2.json`
- etc.

When you scrape with non-default title types or filters, the script automatically derives a more specific output directory name unless you pass `--output-dir`.

Each file contains 20 items with complete metadata including cast, crew, ratings, and technical specifications.

### Processing Data

After scraping, process the raw data into organized batches:

```bash
python3 process_movies.py
```

This creates `processed_movies/` folder with files containing 1,000 movies each.
