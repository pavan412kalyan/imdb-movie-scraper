# IMDb Movie News Downloader

Fetch the latest IMDb movie news items via GraphQL and output JSON.

## Usage

```bash
# Basic usage (prints JSON to stdout)
python3 latest_movie_news.py --limit 10 --pages 1

# Save to a file
python3 latest_movie_news.py --limit 50 --pages 2 --output movie_news.json

# Include plain-text article body (HTML stripped)
python3 latest_movie_news.py --plain-text --limit 5 --pages 1
```

## Options

- `--limit` items per page (default: 50)
- `--pages` number of pages to fetch (default: 1)
- `--after` cursor token to start from
- `--filter` category filter (default: `MOVIE`)
- `--locale` locale (default: `en-US`)
- `--original-title-text` use original title text
- `--plain-text` include `text_plain` (HTML stripped)
- `--output` output JSON file path
