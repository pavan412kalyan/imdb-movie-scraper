# IMDb People Downloader

Download people data and person-related media from IMDb.

## Included Scripts

- `scrape_all_people.py`
  Bulk people/name extraction using `AdvancedNameSearch`

- `person_images_downloader.py`
  Download images for a person by IMDb name id

- `person_videos_downloader.py`
  Download video metadata for a person by IMDb name id

## Examples

```bash
# Bulk people scraping
python3 scrape_all_people.py

# Person images
python3 person_images_downloader.py nm0001191

# Person videos
python3 person_videos_downloader.py nm0001191
```

## Notes

- Person ids look like `nm0001191`.
- Bulk people scraping is GraphQL-based and paginated.
- Image and video scripts create output folders per person.
