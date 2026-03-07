# IMDb Images Downloader

Download title images from IMDb using GraphQL pagination.

## Script

- `images_downloader.py`

## Usage

Edit the `IMDB_ID` constant in `images_downloader.py`, then run:

```bash
python3 images_downloader.py
```

Images are downloaded into a folder named like:

```bash
images_tt0944947
```

## Notes

- Uses the `TitleMediaIndexPagination` GraphQL query.
- Downloads image files, not just metadata.
- Current script configuration is constant-based rather than CLI-based.
