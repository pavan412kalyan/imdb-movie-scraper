# IMDb Search By ID

Fetch detailed title information for a specific IMDb id.

## Script

- `search_movie.py`

## Usage

```bash
python3 search_movie.py tt0944947
```

## Output

The script returns detailed title metadata such as:

- title and original title
- release year and release date
- runtime
- ratings and vote count
- genres
- plot
- image
- principal credits
- certificate
- spoken languages
- countries of origin
- company credits
- technical specifications
- trailer info
- review count

## Notes

- Uses a detailed GraphQL `title(id: ...)` query.
- Good choice when you need richer metadata for a single title.
