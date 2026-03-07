# IMDb Trending Downloader

Fetch trending titles and trending trailers from IMDb.

## Included Scripts

- `trending_movies.py`
  Download trending title data

- `trending_trailers.py`
  Download trending trailer metadata

## Examples

```bash
# Trending titles
python3 trending_movies.py --count 10

# Trending trailers
python3 trending_trailers.py --limit 25

# Save trending trailers to JSON
python3 trending_trailers.py --limit 25 --output trending_trailers.json
```

## Notes

- `trending_movies.py` uses the `topTrendingTitles` GraphQL query.
- `trending_trailers.py` uses the `trendingTitles` GraphQL query.
