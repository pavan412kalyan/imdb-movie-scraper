# Rotten Tomatoes Downloader

Fetch Rotten Tomatoes discovery modules, title page metadata, site-search results, and reviews.

## Included Scripts

- `rt_discovery_sidebar.py`
  Download title data from endpoints like:
  `https://www.rottentomatoes.com/cnapi/modules/discovery-sidebar/tvSeries/AIRING`

- `rt_title_page.py`
  Extract title data from Rotten Tomatoes movie, TV series, season, or episode URLs.

- `rt_reviews.py`
  Download paginated critic or audience reviews from Rotten Tomatoes title URLs.

- `rt_search.py`
  Search Rotten Tomatoes content and people through the public Algolia endpoint used by site search.

- `rt_reviews_by_imdb.py`
  Resolve an IMDb title ID to a Rotten Tomatoes title, then download critic or audience reviews.

## Examples

```bash
# TV series currently airing
python3 rt_discovery_sidebar.py

# Save airing TV series to JSON
python3 rt_discovery_sidebar.py --media-type tvSeries --status AIRING --output rt_airing_tv.json

# Print the normalized JSON
python3 rt_discovery_sidebar.py --json

# Print the raw Rotten Tomatoes response
python3 rt_discovery_sidebar.py --raw --json

# Extract title details from a Rotten Tomatoes page URL
python3 rt_title_page.py https://www.rottentomatoes.com/tv/margos_got_money_troubles

# Save full page-derived metadata
python3 rt_title_page.py https://www.rottentomatoes.com/m/finding_nemo --output rt_finding_nemo.json

# Critic reviews
python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type critic --limit 25 --output finding_nemo_critics.json

# Audience reviews
python3 rt_reviews.py https://www.rottentomatoes.com/m/finding_nemo --type audience --limit 50 --output finding_nemo_audience.json

# Top critic reviews for a TV season
python3 rt_reviews.py https://www.rottentomatoes.com/tv/margos_got_money_troubles/s01 --top-only --json

# Search Rotten Tomatoes titles
python3 rt_search.py "finding nemo" --hits-per-page 5 --json

# Inspect RT candidates for an IMDb title ID
python3 rt_reviews_by_imdb.py tt0266543 --show-candidates

# Download Rotten Tomatoes critic reviews by IMDb title ID
python3 rt_reviews_by_imdb.py tt0266543 --type critic --limit 25 --output finding_nemo_rt_critics.json

# Download Rotten Tomatoes audience reviews by IMDb title ID
python3 rt_reviews_by_imdb.py tt0266543 --type audience --limit 50 --json
```

## Discovery Sidebar Output

The normalized output includes common fields when available:

- `id`
- `title`
- `year`
- `section`
- `list`
- `details_url`
- `url`
- `poster_url`
- `tomatometer_score`
- `audience_score`
- `synopsis`
- `raw`

The `raw` field preserves the original item payload because Rotten Tomatoes can change module response fields.

## Title Page Output

`rt_title_page.py` extracts page-level data exposed in JSON-LD, meta tags, and Rotten Tomatoes page context:

- `name`
- `type`
- `ems_id`
- `url`
- `description`
- `image`
- `genre`
- `release_date`
- `runtime`
- `rating`
- `cast`
- `directors`
- `producers`
- `creators`
- `seasons`
- `trailer`
- `meta`
- `rt_context` (`dtm_data`, `bk_data`, `video`, `video_clips`, `review`)
- `raw_json_ld`

## Reviews Output

`rt_reviews.py` uses Rotten Tomatoes' current review pagination endpoint:
`/napi/rtcf/v1/{movies|tv/seasons|tv/episodes}/{ems_id}/reviews`

Critic reviews include:

- `id`
- `quote`
- `score_sentiment`
- `original_score`
- `date`
- `language`
- `url`
- `critic`
- `publication`
- `raw`

Audience reviews include:

- `id`
- `review`
- `rating`
- `rating_number`
- `date`
- `display_name`
- `is_verified`
- `is_super_reviewer`
- `has_spoilers`
- `has_profanity`
- `user`
- `raw`

For TV series URLs, the script resolves the first listed season and fetches season reviews. Use a season URL directly when you need a specific season.

## Search and IMDb ID Review Lookup

`rt_search.py` uses Rotten Tomatoes' Algolia site-search endpoint. Content hits can include:

- `ems_id`
- `ems_version_id`
- `type`
- `title`
- `vanity`
- `url`
- `release_year`
- `runtime_minutes`
- `rating`
- `genres`
- `poster_url`
- `critics_score`
- `audience_score`
- `description`
- `raw`

`rt_reviews_by_imdb.py` gets the IMDb title name, year, and type, searches Rotten Tomatoes, ranks candidates, and reuses `rt_reviews.py` for review pagination. If the match is ambiguous, run `--show-candidates` and pass the exact Rotten Tomatoes URL with `--rt-url`.

## Notes

- Browser cookies from copied `curl` commands are intentionally not used.
- The script sends normal browser-like request headers and accepts configurable `media-type` and `status` path segments.
- The Algolia key used by `rt_search.py` is the public search key exposed by Rotten Tomatoes' frontend.
