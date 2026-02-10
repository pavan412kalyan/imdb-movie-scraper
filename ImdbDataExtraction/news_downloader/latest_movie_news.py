import argparse
import html
import json
import re
from urllib.parse import urlencode

import requests

BASE_URL = "https://caching.graphql.imdb.com/"
OPERATION_NAME = "NewsCategorySubPagePagination"
NEWS_QUERY = """
query NewsCategorySubPagePagination(
  $after: String,
  $category: NewsCategory!,
  $first: Int!
) {
  news(
    after: $after,
    category: $category,
    first: $first
  ) {
    total
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        articleTitle {
          plainText
        }
        externalUrl
        source {
          homepage {
            label
            url
          }
          trustedSource
        }
        date
        text {
          plaidHtml
        }
        image {
          url
          height
          width
          caption {
            plainText
          }
        }
        byline
      }
    }
  }
}
"""

HEADERS = {
    "accept": "application/graphql+json, application/json",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "referer": "https://www.imdb.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "x-imdb-client-name": "imdb-web-next-localized",
    "x-imdb-user-country": "US",
    "x-imdb-user-language": "en-US",
}

TAG_RE = re.compile(r"<[^>]+>")


def build_variables(after, limit, category_filter, locale, original_title_text):
    variables = {
        "after": after or "",
        "category": category_filter,
        "first": limit,
    }
    return variables


def fetch_news_page(after, limit, category_filter, locale, original_title_text):
    variables = build_variables(after, limit, category_filter, locale, original_title_text)
    payload = {
        "operationName": OPERATION_NAME,
        "query": NEWS_QUERY,
        "variables": variables,
    }
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text[:200]}")
        return None
    return response.json()


def html_to_text(value):
    if not value:
        return ""
    value = value.replace("<br/>", "\n").replace("<br />", "\n")
    return html.unescape(TAG_RE.sub("", value)).strip()


def extract_news_items(data, plain_text=False):
    items = []
    edges = data.get("data", {}).get("news", {}).get("edges", []) if data.get("data", {}).get("news") else []
    for edge in edges:
        node = edge.get("node", {})
        article_title = node.get("articleTitle", {}).get("plainText") if node.get("articleTitle") else None
        source = node.get("source", {}).get("homepage", {}) if node.get("source") else {}
        text_html = (node.get("text") or {}).get("plaidHtml")

        item = {
            "id": node.get("id"),
            "title": article_title,
            "url": node.get("externalUrl"),
            "source_label": source.get("label"),
            "source_url": source.get("url"),
            "source_trusted": node.get("source", {}).get("trustedSource") if node.get("source") else None,
            "published_at": node.get("date"),
            "byline": node.get("byline"),
            "text_html": text_html,
            "text_plain": html_to_text(text_html) if plain_text else None,
            "image": node.get("image"),
        }
        items.append(item)
    return items


def main():
    parser = argparse.ArgumentParser(description="Fetch IMDb news for movies")
    parser.add_argument("--limit", type=int, default=50, help="Items per page")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch")
    parser.add_argument("--after", help="Pagination cursor to start from")
    parser.add_argument("--filter", default="MOVIE", help="Category filter (MOVIE, TV, CELEB, etc.)")
    parser.add_argument("--locale", default="en-US", help="Locale (default: en-US)")
    parser.add_argument("--original-title-text", action="store_true", help="Use original title text")
    parser.add_argument("--plain-text", action="store_true", help="Include text_plain field")
    parser.add_argument("--output", help="Output JSON file path")

    args = parser.parse_args()

    all_items = []
    after = args.after

    for page in range(1, args.pages + 1):
        print(f"Fetching page {page}...")
        data = fetch_news_page(
            after,
            args.limit,
            args.filter,
            args.locale,
            args.original_title_text,
        )
        if not data:
            break

        items = extract_news_items(data, plain_text=args.plain_text)
        all_items.extend(items)
        print(f"Found {len(items)} items")

        page_info = data.get("data", {}).get("news", {}).get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break

        after = page_info.get("endCursor")
        if not after:
            break

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=2, ensure_ascii=False)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(all_items, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
