# IMDb Chart And List Downloader

Download IMDb chart pages and IMDb lists using GraphQL-backed extractors.

## Included Scripts

- `chart_titles.py`
  Fetches chart-based title collections such as Top 250, Top TV, Bottom 100, and popularity charts.

- `list_titles.py`
  Fetches IMDb list pages such as `/list/ls039852437/` using the `TitleListMainPage` GraphQL operation.

## Chart Downloader

### Supported Charts

- `top` - Top rated movies
- `toptv` - Top rated TV shows
- `bottom` - Lowest rated movies
- `moviemeter` - Most popular movies
- `tvmeter` - Most popular TV shows

### Examples

```bash
# Print the top 5 movies
python3 chart_titles.py --chart top --limit 5

# Save the Top 250 movies
python3 chart_titles.py --chart top --limit 250 --output top_250.json

# Save the most popular TV chart
python3 chart_titles.py --chart tvmeter --limit 100 --output popular_tv.json
```

### Output Fields

Each title item includes normalized fields such as:

- `rank`
- `id`
- `title`
- `original_title`
- `title_type`
- `year`
- `release_date`
- `runtime_minutes`
- `rating`
- `vote_count`
- `certificate`
- `genres`
- `plot`
- `image_url`
- `latest_trailer_id`
- `production_stage`

## List Downloader

### Examples

```bash
# Fetch a list and print list metadata plus titles
python3 list_titles.py ls039852437

# Fetch only the normalized title items
python3 list_titles.py ls039852437 --titles-only

# Save the full list to JSON
python3 list_titles.py ls039852437 --output imdb_list.json

# Limit the number of returned items
python3 list_titles.py ls039852437 --limit 250 --output imdb_list_250.json
```

### Output Shape

Default output:

```json
{
  "list": {
    "id": "ls039852437",
    "name": "IMDb top 250 on Netflix",
    "item_total": 35
  },
  "titles": [
    {
      "id": "tt0111161",
      "title": "The Shawshank Redemption"
    }
  ]
}
```

With `--titles-only`, only the normalized title array is returned.

By default, `list_titles.py` fetches the full list. Use `--limit` only when you want to cap the number of returned items.

## Notes

- These scripts are intended for data extraction and JSON export.
- `chart_titles.py` uses the `chartTitles` GraphQL field.
- `list_titles.py` uses the persisted `TitleListMainPage` GraphQL operation.
- Install Python dependencies from the repo root with:

```bash
pip install -r requirements.txt
```
