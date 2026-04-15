# IMDb Streaming Availability

Fetch streaming and watch-option data for a title, or list all titles on a streaming provider.

## Scripts

- `streaming_checker.py` — look up watch options for a single title
- `titles_by_provider.py` — list all titles on a provider (forward search: provider → titles)

## Usage

### Check streaming options for a single title

```bash
python3 streaming_checker.py --title tt0899043
```

### List all titles on a provider

```bash
# All titles on Netflix in the US
python3 titles_by_provider.py netflix

# Movies on Netflix with rating >= 7
python3 titles_by_provider.py netflix --type movie --min-rating 7

# TV series on Prime Video in the UK, save to file
python3 titles_by_provider.py amazon_prime_video --country GB --type tvSeries --output prime_uk.json

# Disney+ movies rated 7.5+, print as JSON
python3 titles_by_provider.py disney_plus --type movie --min-rating 7.5 --json

# Fetch with pagination control and delay
python3 titles_by_provider.py netflix --max-pages 10 --page-size 50 --request-delay 0.5

# Limit total results
python3 titles_by_provider.py netflix --limit 100 --output netflix_top100.json

# List ALL available providers for a country
python3 titles_by_provider.py --list-all-providers --country US

# Discover providers available for a specific title
python3 titles_by_provider.py --list-providers tt10919420 --country US
```

### Filters

| Flag              | Description                                          |
|-------------------|------------------------------------------------------|
| `--type`          | Title type: `movie`, `tvSeries`, `tvMiniSeries`, etc.|
| `--genre`         | Genre: `Action`, `Drama`, `Comedy`, `Animation`, etc.|
| `--min-rating`    | Minimum IMDb rating (e.g. `7.5`)                     |
| `--max-rating`    | Maximum IMDb rating                                  |
| `--min-year`      | Minimum release year                                 |
| `--max-year`      | Maximum release year                                 |
| `--limit`         | Maximum total titles to return                       |
| `--max-pages`     | Maximum pages to fetch                               |
| `--page-size`     | Titles per page (default: 50)                        |
| `--country`       | Country code for availability (default: US)          |

## All Available Providers (US)

Popular providers (pass the short name or full ID):

| Short name / Full ID                              | Name              | Category     |
|---------------------------------------------------|-------------------|--------------|
| `netflix`                                         | Netflix           | SUBSCRIPTION |
| `amazon_prime_video` / `prime_video.PRIME`        | Prime Video       | SUBSCRIPTION |
| `disney_plus` / `disneyplus`                      | Disney+           | SUBSCRIPTION |
| `hulu`                                            | Hulu              | SUBSCRIPTION |
| `max` / `hbo_max`                                 | HBO Max           | SUBSCRIPTION |
| `apple_tv_plus` / `appletv`                       | Apple TV          | SUBSCRIPTION |
| `paramount_plus` / `cbs_aa`                       | Paramount+        | SUBSCRIPTION |
| `peacock`                                         | Peacock           | SUBSCRIPTION |
| `starz`                                           | STARZ             | SUBSCRIPTION |
| `roku` / `rokuchannel`                            | The Roku Channel  | SUBSCRIPTION |
| `discoveryplus`                                   | discovery+        | SUBSCRIPTION |

All providers (44 total for US):

| Full Provider ID                                   | Name              | refTagFragment    |
|----------------------------------------------------|-------------------|-------------------|
| `amzn1.imdb.w2w.provider.adultswim`               | adultswim         | ad_sw             |
| `amzn1.imdb.w2w.provider.amcplus`                 | AMC+              | amc_plus          |
| `amzn1.imdb.w2w.provider.angel_studios`           | Angel             | angel_studios     |
| `amzn1.imdb.w2w.provider.an_pl`                   | Animal Planet     | an_pl             |
| `amzn1.imdb.w2w.provider.appletv`                 | Apple TV          | appletv           |
| `amzn1.imdb.w2w.provider.betplus`                 | BET+              | bet_plus          |
| `amzn1.imdb.w2w.provider.bravo`                   | Bravo Now         | bravo             |
| `amzn1.imdb.w2w.provider.cartoon`                 | Cartoon Network   | cartoon           |
| `amzn1.imdb.w2w.provider.prime_video.crunchyroll` | Crunchyroll       | pvc_crunchyroll   |
| `amzn1.imdb.w2w.provider.discoveryplus`           | discovery+        | discoveryplus     |
| `amzn1.imdb.w2w.provider.disneyplus`              | Disney+           | disneyplus        |
| `amzn1.imdb.w2w.provider.disneynow`               | DisneyNow         | disney_now        |
| `amzn1.imdb.w2w.provider.e_now`                   | E! Now            | e_now             |
| `amzn1.imdb.w2w.provider.espn`                    | ESPN+             | espn              |
| `amzn1.imdb.w2w.provider.fawesome_in`             | Fawesome          | fawesome_in       |
| `amzn1.imdb.w2w.provider.food`                    | Food Network      | food              |
| `amzn1.imdb.w2w.provider.fox`                     | FOX NOW           | fox               |
| `amzn1.imdb.w2w.provider.hbo_max`                 | HBO Max           | hbomax            |
| `amzn1.imdb.w2w.provider.hgtv`                    | HGTV              | hgtv              |
| `amzn1.imdb.w2w.provider.history`                 | History           | history           |
| `amzn1.imdb.w2w.provider.hopster`                 | Hopster           | hopster           |
| `amzn1.imdb.w2w.provider.hulu`                    | Hulu              | hulu              |
| `amzn1.imdb.w2w.provider.epix`                    | MGM+              | epix              |
| `amzn1.imdb.w2w.provider.nbc`                     | NBC               | nbc               |
| `amzn1.imdb.w2w.provider.netflix`                 | Netflix           | netflix           |
| `amzn1.imdb.w2w.provider.cbs_aa`                  | Paramount+        | paramount+        |
| `amzn1.imdb.w2w.provider.pbs`                     | PBS               | pbs               |
| `amzn1.imdb.w2w.provider.peacock`                 | Peacock           | peacock           |
| `amzn1.imdb.w2w.provider.plex`                    | Plex              | _plex             |
| `amzn1.imdb.w2w.provider.pluto`                   | Pluto TV          | pluto             |
| `amzn1.imdb.w2w.provider.prime_video`             | Prime Video       | pvt_aiv           |
| `amzn1.imdb.w2w.provider.prime_video.PRIME`       | Prime Video       | pvs_piv           |
| `amzn1.imdb.w2w.provider.redbulltv`               | Red Bull TV       | redbulltv         |
| `amzn1.imdb.w2w.provider.starz`                   | STARZ             | starz             |
| `amzn1.imdb.w2w.provider.syfy`                    | Syfy Now          | syfy              |
| `amzn1.imdb.w2w.provider.tbs`                     | TBS               | tbs               |
| `amzn1.imdb.w2w.provider.telemundo`               | Telemundo Now     | telemundo         |
| `amzn1.imdb.w2w.provider.cw`                      | The CW            | cw                |
| `amzn1.imdb.w2w.provider.rokuchannel`             | The Roku Channel  | rokuchannel       |
| `amzn1.imdb.w2w.provider.tlc`                     | TLC               | tlc               |
| `amzn1.imdb.w2w.provider.tnt`                     | TNT               | tnt               |
| `amzn1.imdb.w2w.provider.tubi`                    | Tubi              | tubi              |
| `amzn1.imdb.w2w.provider.viki`                    | Viki              | viki              |
| `amzn1.imdb.w2w.provider.vix`                     | Vix               | vix               |

> Note: provider availability varies by country. Run `--list-all-providers --country GB` to see UK providers, etc.

## Output

Each title record includes: `id`, `title`, `original_title`, `title_type`, `year`, `release_date`, `runtime_minutes`, `rating`, `vote_count`, `certificate`, `genres`, `plot`, `image_url`, `latest_trailer_id`.

## Notes

- `titles_by_provider.py` uses the `streamingTitles` GraphQL query on `https://api.graphql.imdb.com/` — returns ~49 recently added / featured titles per provider. IMDb caps this at one page; it is not a full catalog. No per-title lookups needed.
- Filters (`--type`, `--genre`, `--min-rating`, etc.) are applied client-side on the returned set.
- Provider availability is country-sensitive — use `--country` to match your region.
- `streaming_checker.py` uses the `HERO_WATCH_BOX` GraphQL query on `https://api.graphql.imdb.com/`.
