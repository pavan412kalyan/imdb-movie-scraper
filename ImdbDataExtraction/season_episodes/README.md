# IMDb Season Episodes Downloader

Fetch episode data for a TV series using GraphQL pagination.

## Script

- `get_season_episodes.py`

## Usage

```bash
python3 get_season_episodes.py tt0944947
```

Optional flags:

```bash
python3 get_season_episodes.py tt0944947 --basic
python3 get_season_episodes.py tt0944947 --json
```

## Output

- Returns episode items across the series episode connection
- Supports basic or extended field sets

## Notes

- Despite the script name, it currently fetches paginated episodes from the series-level episode connection.
- Series ids look like `tt0944947`.
