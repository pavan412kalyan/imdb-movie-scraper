import requests
import json
import argparse

BASE_URL = "https://caching.graphql.imdb.com/"

HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36'
}

def build_episode_fields(include_extended):
    if include_extended:
        return """
                    id
                    titleText { text }
                    originalTitleText { text }
                    titleType { text id }
                    releaseYear { year }
                    releaseDate { day month year }
                    ratingsSummary { aggregateRating voteCount }
                    plot { plotText { plainText } }
                    primaryImage { url width height }
                    runtime { seconds }
                    genres { genres { text id } }
                    certificate { rating }
                    canHaveEpisodes
                    isAdult
                    series {
                      episodeNumber {
                        episodeNumber
                        seasonNumber
                      }
                    }
        """

    return """
                    id
                    titleText { text }
                    releaseDate { day month year }
                    ratingsSummary { aggregateRating }
                    plot { plotText { plainText } }
                    primaryImage { url }
                    runtime { seconds }
                    series {
                      episodeNumber {
                        episodeNumber
                        seasonNumber
                      }
                    }
    """

def get_season_episodes(series_id, after_cursor=None, limit=50, include_extended=True):
    """Get episodes for a TV series (all seasons, paginated)"""
    variables = {"id": series_id, "first": limit}
    if after_cursor:
        variables["after"] = after_cursor

    episode_fields = build_episode_fields(include_extended)

    query = (
        "query GetSeasonEpisodes($id: ID!, $first: Int!, $after: ID) {\n"
        "  title(id: $id) {\n"
        "    episodes {\n"
        "      episodes(first: $first, after: $after) {\n"
        "        edges {\n"
        "          node {\n"
        f"{episode_fields}"
        "          }\n"
        "        }\n"
        "        pageInfo {\n"
        "          hasNextPage\n"
        "          endCursor\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
    )

    payload = {
        "query": query,
        "operationName": "GetSeasonEpisodes",
        "variables": variables
    }
    
    print(f"📊 Variables: {json.dumps(variables, indent=2)}")
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"❌ GraphQL errors: {data['errors']}")
        episodes_container = data.get("data", {}).get("title", {}).get("episodes", {})
        episodes_info = episodes_container.get("episodes", {})
        episodes_data = episodes_info.get("edges", [])
        page_info = episodes_info.get("pageInfo", {})
        
        # Return all episodes without season filtering
        episodes = []
        for edge in episodes_data:
            episode = edge.get("node", {})
            episodes.append(episode)
        
        return episodes, page_info
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📄 Response text: {response.text}")
        return [], {}

def main():
    parser = argparse.ArgumentParser(description="Get episodes for a TV series season")
    parser.add_argument("series_id", help="IMDb series ID (e.g., tt0944947)")
    parser.add_argument("season", type=int, nargs="?", help="Season number to filter (optional)")
    parser.add_argument("--basic", action="store_true", help="Use basic fields only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--pages", type=int, help="Number of pages to fetch (default: fetch all)")
    parser.add_argument("--limit", type=int, default=50, help="Episodes per page")
    
    args = parser.parse_args()
    
    all_episodes = []
    after_cursor = None
    page = 1
    
    include_extended = not args.basic

    while True:
        episodes, page_info = get_season_episodes(
            args.series_id,
            after_cursor,
            args.limit,
            include_extended=include_extended
        )
        all_episodes.extend(episodes)
        
        print(f"Page {page}: Found {len(episodes)} episodes")
        
        if not page_info.get("hasNextPage"):
            print(f"Reached end of episodes after page {page}")
            break
            
        # Stop if user specified max pages
        if args.pages and page >= args.pages:
            print(f"Reached specified page limit: {args.pages}")
            break
            
        after_cursor = page_info.get("endCursor")
        page += 1
    
    if args.season:
        all_episodes = [
            episode for episode in all_episodes
            if (episode.get("series") or {}).get("episodeNumber", {}).get("seasonNumber") == args.season
        ]

    if args.json:
        print(json.dumps(all_episodes, indent=2))
    else:
        print(f"\n📺 All Episodes for {args.series_id}:")
        print(f"Total found: {len(all_episodes)} episodes\n")
        
        for episode_data in all_episodes:
            
            # Safe extraction with None checks
            title_data = episode_data.get("titleText")
            title = title_data.get("text", "N/A") if title_data else "N/A"
            
            series_data = episode_data.get("series")
            episode_info = series_data.get("episodeNumber") if series_data else None
            episode_num = episode_info.get("episodeNumber", "N/A") if episode_info else "N/A"
            season_num = episode_info.get("seasonNumber", "N/A") if episode_info else "N/A"
            
            ratings_data = episode_data.get("ratingsSummary")
            rating = ratings_data.get("aggregateRating", "N/A") if ratings_data else "N/A"
            vote_count = ratings_data.get("voteCount") if ratings_data else None
            
            # Runtime
            runtime_data = episode_data.get("runtime")
            runtime_seconds = runtime_data.get("seconds") if runtime_data else None
            runtime = f"{runtime_seconds // 60}min" if runtime_seconds else "N/A"
            
            # Release date
            release_date = episode_data.get("releaseDate")
            if release_date:
                year = release_date.get("year", "")
                month = release_date.get("month", "")
                day = release_date.get("day", "")
                date_str = f"{year}-{month:02d}-{day:02d}" if all([year, month, day]) else "N/A"
            else:
                date_str = "N/A"
            
            print(f"S{season_num}E{episode_num:02d}. {title}" if isinstance(episode_num, int) else f"S{season_num}E{episode_num}. {title}")
            rating_line = f"     📅 {date_str} | ⭐ {rating}"
            if vote_count is not None:
                rating_line += f" ({vote_count} votes)"
            rating_line += f" | ⏱️ {runtime}"
            print(rating_line)

            # Genres
            genres_data = episode_data.get("genres", {}).get("genres", []) if episode_data.get("genres") else []
            genres = [genre.get("text") for genre in genres_data if genre and genre.get("text")]
            if genres:
                print(f"     🎭 {', '.join(genres)}")
            
            # Plot
            plot_data = episode_data.get("plot")
            plot = ""
            if plot_data and plot_data.get("plotText"):
                plot = plot_data.get("plotText", {}).get("plainText", "") if plot_data.get("plotText") else ""
            
            if plot:
                plot_short = plot[:100] + "..." if len(plot) > 100 else plot
                print(f"     📝 {plot_short}")
            print()

if __name__ == "__main__":
    main()
