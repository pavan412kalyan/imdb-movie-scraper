# IMDb Review Downloader

Download title reviews from IMDb using GraphQL pagination.

## Script

- `reviews.py`

## Usage

```bash
python3 reviews.py tt0944947
```

Common options:

```bash
python3 reviews.py tt0944947 --max-pages 5
python3 reviews.py tt0944947 --sort-by HELPFULNESS_SCORE --sort-order DESC
python3 reviews.py tt0944947 --delay 1
```

## Output

- Saves raw review pages as JSON files
- Supports pagination
- Supports configurable sort order

## Notes

- Uses the `TitleReviewsRefine` GraphQL query.
- Review output is organized per title id.
