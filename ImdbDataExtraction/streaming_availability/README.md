# IMDb Streaming Availability

Fetch streaming and watch-option data for a title.

## Script

- `streaming_checker.py`

## Usage

```bash
python3 streaming_checker.py --title tt0899043
```

## Output

- Primary watch option
- Additional watch options count
- Watch options grouped by category
- Provider information and logos

## Notes

- Uses the `HERO_WATCH_BOX` GraphQL query.
- Requests are sent to `https://api.graphql.imdb.com/`.
