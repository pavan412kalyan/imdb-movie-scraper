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
- `--save-files` - Save data to JSON files
- `--resume` - Resume from last scraped page (default: True)


### Output

Data is saved to `all_imdb_movies/` folder as:
- `imdb_page_1.json`
- `imdb_page_2.json`
- etc.

Each file contains 20 items with complete metadata including cast, crew, ratings, and technical specifications.

### Processing Data

After scraping, process the raw data into organized batches:

```bash
python3 process_movies.py
```

This creates `processed_movies/` folder with files containing 1,000 movies each.