# JustWatch Downloader

Fetch popular titles from JustWatch by provider and country using the JustWatch GraphQL API.

## Scripts

- `justwatch_popular.py` — fetch popular titles for one or more streaming providers

## Usage

### List available providers for a country

```bash
python3 justwatch_popular.py --list-providers --country IN
python3 justwatch_popular.py --list-providers --country US
```

### Fetch popular titles

```bash
# Netflix India
python3 justwatch_popular.py --country IN --providers nfx

# Netflix + Prime Video India, IMDb rating >= 7
python3 justwatch_popular.py --country IN --providers nfx amp --min-rating 7

# HBO Max US, movies only, 3 pages, save to file
python3 justwatch_popular.py --country US --providers hoc --type MOVIE --pages 3 --output hbo_us.json

# Disney+ shows in the UK, print as JSON
python3 justwatch_popular.py --country GB --providers dnp --type SHOW --json

# Multiple providers with delay between requests
python3 justwatch_popular.py --country US --providers nfx amp hoc --delay 0.5 --limit 200
```

## Filters

| Flag            | Description                                      |
|-----------------|--------------------------------------------------|
| `--country`     | Country code (default: `US`)                     |
| `--providers`   | One or more provider short names (e.g. `nfx amp`)|
| `--type`        | `MOVIE` or `SHOW`                                |
| `--min-rating`  | Minimum IMDb score (e.g. `7.5`)                  |
| `--max-rating`  | Maximum IMDb score                               |
| `--pages`       | Max pages to fetch                               |
| `--page-size`   | Results per page (default: `100`)                |
| `--limit`       | Max total titles to return                       |
| `--delay`       | Seconds to wait between page requests            |
| `--language`    | Language code (default: `en`)                    |
| `--output`      | Save results to a JSON file                      |
| `--json`        | Print results as JSON to stdout                  |

## Common Provider Short Names

| Short Name | Provider         |
|------------|------------------|
| `nfx`      | Netflix          |
| `amp`      | Prime Video      |
| `hoc`      | HBO Max          |
| `dnp`      | Disney+          |
| `hlu`      | Hulu             |
| `ppe`      | Apple TV+        |
| `pct`      | Paramount+       |
| `pck`      | Peacock          |
| `tbs`      | Tubi             |
| `mbi`      | MUBI             |

> Run `--list-providers --country IN` (or any country code) to get the full list for your region.

## Output

Each title record includes: `id`, `type`, `title`, `year`, `runtime_minutes`, `description`, `poster_url`, `imdb_score`, `imdb_votes`, `tmdb_score`, `tmdb_popularity`, `tomato_meter`, `certified_fresh`, `jw_rating`, `watch_url`, `monetization_type`, `presentation_type`, `price`, `currency`, `provider_name`, `provider_short`, `jw_path`.

## Notes

- Uses `https://apis.justwatch.com/graphql` — no API key required.
- `--list-providers` uses the `GetPackages` query which is fully country-aware, unlike the IMDb `watchProviders` query.
- Pagination is cursor-based; IMDb caps results but JustWatch supports full catalog traversal.
- Filters `--min-rating` / `--max-rating` are applied client-side on the IMDb score field.
