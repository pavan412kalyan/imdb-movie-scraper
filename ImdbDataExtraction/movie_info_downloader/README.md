# IMDb Movie Info Downloader

Fetch a single title page and extract structured JSON-LD metadata from IMDb.

## Script

- `download_movie_info.py`

## Usage

Edit the `movie_id` value inside the script, then run:

```bash
python3 download_movie_info.py
```

It saves output to:

```bash
<movie_id>_info.json
```

## Extracted Data

- title
- description
- image
- publish date
- duration
- genres
- keywords
- aggregate rating
- actors
- directors
- creators
- trailer
- review

## Notes

- This script uses the IMDb title HTML page and extracts the JSON-LD block.
- It is page-based extraction, not GraphQL-based.
