# IMDb Search By Filters

Search IMDb titles with GraphQL constraints such as genre, year, rating, language, and title type.

## Script

- `search_by_filters.py`

## Usage

```bash
python3 search_by_filters.py --genre Action
python3 search_by_filters.py --genre Drama --min-year 2000 --max-year 2020
python3 search_by_filters.py --genre Thriller --min-rating 7 --pages 2
python3 search_by_filters.py --type tvSeries --languages en hi
```

## Output

- Prints matching titles and summary information
- Supports multi-page fetching with `--pages`

## Notes

- Uses `AdvancedTitleSearch`.
- Returns a lighter result shape than `search_by_id` or `pages_dowloader`.
