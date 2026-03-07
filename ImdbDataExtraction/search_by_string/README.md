# IMDb Search By String

Search IMDb titles and people using the suggestion API.

## Script

- `search_by_string.py`

## Usage

```bash
python3 search_by_string.py "batman"
python3 search_by_string.py "christopher nolan" --limit 20
python3 search_by_string.py "game of thrones" --json
```

## Output

- Supports titles and people in the same result set
- Can print readable results or JSON

## Notes

- Uses the IMDb suggestions endpoint, not GraphQL.
- Result ids typically start with `tt` for titles and `nm` for people.
