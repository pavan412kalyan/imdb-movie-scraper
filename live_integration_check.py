#!/usr/bin/env python3
"""
Run bounded live integration checks against IMDb.

These checks intentionally hit real IMDb endpoints. They are not unit tests and
can fail when IMDb blocks or changes an endpoint.
"""
import argparse
import os
import subprocess
import sys
from dataclasses import dataclass


ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TIMEOUT = 25
BLOCKED_MARKERS = (
    "403 Forbidden",
    "HTTP error from IMDb GraphQL: 403",
    "403 Client Error",
)
ERROR_MARKERS = (
    "Traceback (most recent call last)",
    "ImportError:",
    "ModuleNotFoundError:",
)


@dataclass
class Check:
    name: str
    command: list[str]
    expect: tuple[str, ...] = ()
    reject: tuple[str, ...] = ()
    timeout: int = DEFAULT_TIMEOUT


def run_check(check: Check) -> tuple[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT + os.pathsep + env.get("PYTHONPATH", "")

    try:
        proc = subprocess.run(
            check.command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=check.timeout,
        )
    except subprocess.TimeoutExpired as e:
        output = e.stdout or ""
        return "FAIL", f"timed out after {check.timeout}s\n{output}"

    output = proc.stdout or ""
    for marker in BLOCKED_MARKERS:
        if marker in output:
            return "BLOCKED", output

    if proc.returncode != 0:
        return "FAIL", output

    for marker in ERROR_MARKERS + check.reject:
        if marker in output:
            return "FAIL", output

    for marker in check.expect:
        if marker not in output:
            return "FAIL", f"missing expected marker {marker!r}\n{output}"

    return "PASS", output


def py_expr(code: str) -> list[str]:
    return [sys.executable, "-c", code]


def build_checks() -> list[Check]:
    return [
        Check(
            name="suggestion search",
            command=[
                sys.executable,
                "ImdbDataExtraction/search_by_string/search_by_string.py",
                "batman",
                "--limit",
                "1",
            ],
            expect=("Found 1 results",),
        ),
        Check(
            name="filtered title search",
            command=[
                sys.executable,
                "ImdbDataExtraction/search_by_filters/search_by_filters.py",
                "--type",
                "movie",
                "--limit",
                "1",
                "--pages",
                "1",
            ],
            expect=("Total found:",),
        ),
        Check(
            name="bulk title page",
            command=[
                sys.executable,
                "ImdbDataExtraction/pages_dowloader/scrape_all_movie_list.py",
                "--max-pages",
                "1",
                "--title-types",
                "movie",
            ],
            expect=("Fetched",),
        ),
        Check(
            name="people page",
            command=[
                sys.executable,
                "ImdbDataExtraction/people_downloader/scrape_all_people.py",
                "--max-pages",
                "1",
                "--no-save",
            ],
            expect=("Fetched",),
            reject=("Fetched 0 people",),
        ),
        Check(
            name="search by title id",
            command=py_expr(
                "from ImdbDataExtraction.search_by_id.search_movie "
                "import get_movie_details, format_movie_details; "
                "movie = format_movie_details(get_movie_details('tt0944947')); "
                "assert movie and movie.get('id') == 'tt0944947', movie; "
                "print(movie['id'])"
            ),
            expect=("tt0944947",),
        ),
        Check(
            name="reviews",
            command=py_expr(
                "from ImdbDataExtraction.review_downloader.reviews import fetch_page; "
                "data = fetch_page('tt0944947', None); "
                "reviews = data.get('data', {}).get('title', {}).get('reviews', {}); "
                "assert reviews.get('edges'), reviews; "
                "print(f\"reviews={len(reviews['edges'])}\")"
            ),
            expect=("reviews=",),
        ),
        Check(
            name="season episodes",
            command=[
                sys.executable,
                "ImdbDataExtraction/season_episodes/get_season_episodes.py",
                "tt0944947",
                "1",
                "--pages",
                "1",
                "--limit",
                "2",
            ],
            expect=("Total found:",),
            reject=("Total found: 0 episodes",),
        ),
        Check(
            name="trending movies",
            command=[
                sys.executable,
                "ImdbDataExtraction/trending_downloader/trending_movies.py",
                "--count",
                "1",
                "--ids-only",
            ],
            expect=("Trending Movie IDs",),
        ),
        Check(
            name="trending trailers",
            command=[
                sys.executable,
                "ImdbDataExtraction/trending_downloader/trending_trailers.py",
                "--limit",
                "1",
            ],
            expect=("Found 1 trailers",),
        ),
        Check(
            name="streaming availability",
            command=[
                sys.executable,
                "ImdbDataExtraction/streaming_availability/streaming_checker.py",
                "--title",
                "tt0944947",
            ],
            expect=("watchOptions",),
        ),
        Check(
            name="movie info page parse",
            command=py_expr(
                "from ImdbDataExtraction.movie_info_downloader.download_movie_info "
                "import get_movie_info; "
                "info = get_movie_info('tt0944947'); "
                "assert info and info.get('title'), info; "
                "print(info['title'])"
            ),
        ),
        Check(
            name="person videos page",
            command=py_expr(
                "from ImdbDataExtraction.people_downloader.person_videos_downloader "
                "import fetch_page, extract_videos; "
                "videos = extract_videos(fetch_page('nm0001191')); "
                "assert videos, videos; "
                "print(f'videos={len(videos)}')"
            ),
            expect=("videos=",),
        ),
        Check(
            name="person images page",
            command=py_expr(
                "from ImdbDataExtraction.people_downloader.person_images_downloader "
                "import fetch_page, extract_images; "
                "images = extract_images(fetch_page('nm0001191')); "
                "assert images, images; "
                "print(f'images={len(images)}')"
            ),
            expect=("images=",),
        ),
        Check(
            name="title images page",
            command=py_expr(
                "from ImdbDataExtraction.images_dowloader.images_downloader "
                "import fetch_page, extract_images; "
                "images = extract_images(fetch_page('tt0944947', '')); "
                "assert images, images; "
                "print(f'images={len(images)}')"
            ),
            expect=("images=",),
        ),
        Check(
            name="single video playback",
            command=py_expr(
                "from ImdbDataExtraction.videos_downloader.download_video_from_id "
                "import get_video_data_graphql; "
                "urls, title = get_video_data_graphql('vi59490329'); "
                "assert urls and title, (urls, title); "
                "print(f'video={title} urls={len(urls)}')"
            ),
            expect=("urls=",),
        ),
        Check(
            name="bulk video downloader imports",
            command=py_expr(
                "import sys; "
                "sys.path.insert(0, 'ImdbDataExtraction/videos_downloader'); "
                "import bulk_video_downloader; "
                "print('import-ok')"
            ),
            expect=("import-ok",),
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live IMDb integration checks")
    parser.add_argument("--only", help="Run checks whose name contains this text")
    parser.add_argument("--show-output", action="store_true", help="Print full output for passing checks")
    args = parser.parse_args()

    checks = build_checks()
    if args.only:
        checks = [check for check in checks if args.only.lower() in check.name.lower()]

    if not checks:
        print("No checks matched.")
        return 2

    counts = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    for check in checks:
        status, output = run_check(check)
        counts[status] += 1
        first_line = next((line for line in output.splitlines() if line.strip()), "")
        print(f"{status:7} {check.name}")
        if status != "PASS" or args.show_output:
            detail = output.strip() or first_line
            if detail:
                print(indent(detail[:1200]))

    print(
        f"\nSummary: {counts['PASS']} passed, "
        f"{counts['BLOCKED']} blocked, {counts['FAIL']} failed"
    )
    return 1 if counts["BLOCKED"] or counts["FAIL"] else 0


def indent(text: str) -> str:
    return "\n".join(f"  {line}" for line in text.splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
