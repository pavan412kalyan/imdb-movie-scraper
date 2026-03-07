import argparse
import glob
import json
import os
import time

import requests

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "AdvancedTitleSearch"
DEFAULT_OUTPUT_DIR = "all_imdb_movies"
DEFAULT_TITLE_TYPES = ["movie"]
DEFAULT_PAGE_SIZE = 20
DEFAULT_TIMEOUT = 30

HEADERS = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "priority": "u=1, i",
}

ADVANCED_TITLE_SEARCH_QUERY = """query AdvancedTitleSearch($after: String, $first: Int!, $constraints: AdvancedTitleSearchConstraints) {
  advancedTitleSearch(after: $after, first: $first, constraints: $constraints) {
    edges {
      node {
        title {
          id
          titleText {
            text
          }
          originalTitleText {
            text
          }
          titleType {
            text
            id
          }
          releaseYear {
            year
          }
          releaseDate {
            day
            month
            year
          }
          runtime {
            seconds
          }
          ratingsSummary {
            aggregateRating
            voteCount
          }
          genres {
            genres {
              text
              id
            }
          }
          plot {
            plotText {
              plainText
            }
            language {
              id
            }
          }
          primaryImage {
            url
            width
            height
            caption {
              plainText
            }
          }
          metacritic {
            metascore {
              score
            }
          }
          principalCredits {
            category {
              text
              id
            }
            credits {
              name {
                id
                nameText {
                  text
                }
                primaryImage {
                  url
                }
              }
              ... on Cast {
                characters {
                  name
                }
              }
              attributes {
                text
              }
            }
          }
          certificate {
            rating
            country {
              text
            }
          }
          spokenLanguages {
            spokenLanguages {
              text
              id
            }
          }
          countriesOfOrigin {
            countries {
              text
              id
            }
          }
          canHaveEpisodes
          isAdult
          latestTrailer {
            id
            name {
              value
            }
            thumbnail {
              url
            }
            runtime {
              value
            }
            playbackURLs {
              displayName {
                value
              }
              url
            }
            contentType {
              displayName {
                value
              }
            }
            createdDate
          }
          productionStatus {
            currentProductionStage {
              text
              id
            }
          }
          series {
            series {
              id
              titleText {
                text
              }
              releaseYear {
                year
              }
            }
          }
          episodes {
            episodes {
              total
            }
          }
          technicalSpecifications {
            soundMixes {
              items {
                text
              }
            }
            aspectRatios {
              items {
                aspectRatio
              }
            }
            colorations {
              items {
                text
              }
            }
          }
          meterRanking {
            currentRank
            rankChange {
              changeDirection
              difference
            }
          }
          reviews(first: 1) {
            total
          }
          keywords(first: 5) {
            edges {
              node {
                text
                id
              }
            }
          }
          akas(first: 5) {
            edges {
              node {
                text
                country {
                  text
                  id
                }
              }
            }
          }
          companyCredits(first: 5) {
            edges {
              node {
                company {
                  id
                  companyText {
                    text
                  }
                }
                category {
                  text
                  id
                }
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    total
  }
}"""


def normalize_to_list(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item]
    return [value]


def create_filters(
    genres=None,
    release_year_min=None,
    release_year_max=None,
    rating_min=None,
    rating_max=None,
    countries=None,
    languages=None,
):
    filters = {}

    genre_list = normalize_to_list(genres)
    if genre_list:
        filters["genres"] = genre_list

    if release_year_min is not None:
        filters["release_year_min"] = release_year_min

    if release_year_max is not None:
        filters["release_year_max"] = release_year_max

    if rating_min is not None:
        filters["rating_min"] = rating_min

    if rating_max is not None:
        filters["rating_max"] = rating_max

    country_list = normalize_to_list(countries)
    if country_list:
        filters["countries"] = country_list

    language_list = normalize_to_list(languages)
    if language_list:
        filters["languages"] = language_list

    return filters


def build_constraints(filters=None, title_types=None):
    constraints = {}

    normalized_title_types = normalize_to_list(title_types) or DEFAULT_TITLE_TYPES
    constraints["titleTypeConstraint"] = {"anyTitleTypeIds": normalized_title_types}

    if not filters:
        return constraints

    if filters.get("genres"):
        constraints["genreConstraint"] = {"allGenreIds": filters["genres"]}

    if filters.get("release_year_min") is not None or filters.get("release_year_max") is not None:
        constraints["releaseDateConstraint"] = {
            "releaseDateRange": {
                "start": f"{filters.get('release_year_min', 1900)}-01-01",
                "end": f"{filters.get('release_year_max', 2030)}-12-31",
            }
        }

    if filters.get("rating_min") is not None or filters.get("rating_max") is not None:
        rating_range = {}
        if filters.get("rating_min") is not None:
            rating_range["min"] = filters["rating_min"]
        if filters.get("rating_max") is not None:
            rating_range["max"] = filters["rating_max"]
        constraints["userRatingsConstraint"] = {"aggregateRatingRange": rating_range}

    if filters.get("countries"):
        constraints["originCountryConstraint"] = {"allCountries": filters["countries"]}

    if filters.get("languages"):
        constraints["languageConstraint"] = {"allLanguages": filters["languages"]}

    return constraints


def get_variables(after_cursor=None, filters=None, title_types=None, page_size=DEFAULT_PAGE_SIZE):
    variables = {
        "first": page_size,
        "constraints": build_constraints(filters=filters, title_types=title_types),
    }
    if after_cursor:
        variables["after"] = after_cursor
    return variables


def fetch_page(after_cursor=None, filters=None, title_types=None, page_size=DEFAULT_PAGE_SIZE, timeout=DEFAULT_TIMEOUT):
    payload = {
        "query": ADVANCED_TITLE_SEARCH_QUERY,
        "operationName": OPERATION_NAME,
        "variables": get_variables(
            after_cursor=after_cursor,
            filters=filters,
            title_types=title_types,
            page_size=page_size,
        ),
    }

    response = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=timeout)
    if not response.ok:
        response_text = response.text[:2000]
        raise RuntimeError(f"HTTP {response.status_code} from IMDb GraphQL: {response_text}")
    data = response.json()

    if data.get("errors"):
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    return data


def extract_titles(data):
    edges = data.get("data", {}).get("advancedTitleSearch", {}).get("edges", [])
    return [
        edge.get("node", {}).get("title", {}).get("titleText", {}).get("text")
        for edge in edges
        if edge.get("node", {}).get("title", {}).get("titleText")
    ]


def get_output_dir(output_dir=None, title_types=None, filters=None):
    if output_dir:
        return output_dir

    normalized_title_types = normalize_to_list(title_types) or DEFAULT_TITLE_TYPES
    if normalized_title_types == DEFAULT_TITLE_TYPES and not filters:
        return DEFAULT_OUTPUT_DIR

    name_parts = ["all_imdb"] + normalized_title_types
    if filters:
        if filters.get("genres"):
            name_parts.extend(["genre"] + filters["genres"])
        if filters.get("release_year_min") is not None or filters.get("release_year_max") is not None:
            name_parts.append(
                f"years_{filters.get('release_year_min', 'min')}_{filters.get('release_year_max', 'max')}"
            )
        if filters.get("rating_min") is not None or filters.get("rating_max") is not None:
            name_parts.append(
                f"rating_{filters.get('rating_min', 'min')}_{filters.get('rating_max', 'max')}"
            )
        if filters.get("countries"):
            name_parts.extend(["countries"] + filters["countries"])
        if filters.get("languages"):
            name_parts.extend(["languages"] + filters["languages"])

    sanitized = "_".join(str(part).strip().replace(" ", "_") for part in name_parts if str(part).strip())
    return "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in sanitized)


def get_last_page_info(folder):
    if not os.path.exists(folder):
        return 0, None

    page_files = glob.glob(os.path.join(folder, "imdb_page_*.json"))
    if not page_files:
        return 0, None

    page_numbers = []
    for file_path in page_files:
        try:
            page_num = int(file_path.split("_")[-1].split(".")[0])
            page_numbers.append((page_num, file_path))
        except (ValueError, IndexError):
            continue

    if not page_numbers:
        return 0, None

    last_page_num, last_file = max(page_numbers, key=lambda item: item[0])

    try:
        with open(last_file, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
    except (json.JSONDecodeError, FileNotFoundError):
        return last_page_num, None

    cursor = data.get("data", {}).get("advancedTitleSearch", {}).get("pageInfo", {}).get("endCursor")
    return last_page_num, cursor


def main(
    max_pages=5,
    save_files=False,
    start_cursor=None,
    process_callback=None,
    start_page=1,
    resume=True,
    filters=None,
    title_types=None,
    output_dir=None,
    page_size=DEFAULT_PAGE_SIZE,
    request_delay=0.0,
    timeout=DEFAULT_TIMEOUT,
):
    folder = get_output_dir(output_dir=output_dir, title_types=title_types, filters=filters)

    if resume and start_cursor is None:
        last_page, cursor_token = get_last_page_info(folder)
        if last_page > 0:
            print(f"Resuming from page {last_page + 1} using {folder}/")
            if cursor_token:
                start_cursor = cursor_token
                start_page = last_page + 1
            else:
                print("No cursor token found in the latest page file. Starting from page 1.")
        else:
            print(f"Starting fresh in {folder}/")

    after_cursor = start_cursor
    if save_files and not os.path.exists(folder):
        os.makedirs(folder)

    page_count = start_page

    for _ in range(max_pages):
        print(f"\nFetching page {page_count}...")
        data = fetch_page(
            after_cursor=after_cursor,
            filters=filters,
            title_types=title_types,
            page_size=page_size,
            timeout=timeout,
        )

        if save_files:
            file_path = os.path.join(folder, f"imdb_page_{page_count}.json")
            with open(file_path, "w", encoding="utf-8") as file_handle:
                json.dump(data, file_handle, indent=2)

        if process_callback and callable(process_callback):
            process_callback(data, page_count)

        titles = extract_titles(data)
        search_data = data.get("data", {}).get("advancedTitleSearch", {})
        page_info = search_data.get("pageInfo", {})
        total = search_data.get("total")
        total_label = f" / total available: {total}" if total is not None else ""
        print(f"Fetched {len(titles)} titles{total_label}")

        if not page_info.get("hasNextPage"):
            print("No more pages.")
            break

        after_cursor = page_info.get("endCursor")
        if not after_cursor:
            print("No end cursor found, cannot continue pagination.")
            break

        page_count += 1
        if request_delay > 0:
            time.sleep(request_delay)


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape IMDb title data with optional filters.")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to scrape")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="Titles per page")
    parser.add_argument("--save-files", action="store_true", help="Save each page as JSON")
    parser.add_argument("--output-dir", help="Directory to store JSON page files")
    parser.add_argument("--start-cursor", help="Start from a specific GraphQL cursor")
    parser.add_argument("--start-page", type=int, default=1, help="Page number label for the first fetch")
    parser.add_argument(
        "--title-types",
        nargs="+",
        default=list(DEFAULT_TITLE_TYPES),
        help="Title types to scrape (movie, tvSeries, tvMiniSeries, etc.)",
    )
    parser.add_argument("--genre", nargs="+", help="Genre IDs to require")
    parser.add_argument("--year-min", type=int, help="Minimum release year")
    parser.add_argument("--year-max", type=int, help="Maximum release year")
    parser.add_argument("--rating-min", type=float, help="Minimum IMDb rating")
    parser.add_argument("--rating-max", type=float, help="Maximum IMDb rating")
    parser.add_argument("--countries", nargs="+", help="Country IDs to require")
    parser.add_argument("--languages", nargs="+", help="Language IDs to require")
    parser.add_argument("--request-delay", type=float, default=0.0, help="Delay between page requests in seconds")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")

    resume_group = parser.add_mutually_exclusive_group()
    resume_group.add_argument("--resume", dest="resume", action="store_true", help="Resume from the last saved page")
    resume_group.add_argument("--no-resume", dest="resume", action="store_false", help="Always start from page 1")
    parser.set_defaults(resume=True)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    filters = create_filters(
        genres=args.genre,
        release_year_min=args.year_min,
        release_year_max=args.year_max,
        rating_min=args.rating_min,
        rating_max=args.rating_max,
        countries=args.countries,
        languages=args.languages,
    )

    main(
        max_pages=args.max_pages,
        save_files=args.save_files,
        start_cursor=args.start_cursor,
        start_page=args.start_page,
        resume=args.resume,
        filters=filters,
        title_types=args.title_types,
        output_dir=args.output_dir,
        page_size=args.page_size,
        request_delay=args.request_delay,
        timeout=args.timeout,
    )
