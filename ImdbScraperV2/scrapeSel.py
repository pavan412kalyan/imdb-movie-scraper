from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import requests
from urllib.parse import urlparse, parse_qs, unquote

# Setup Chrome with performance logging
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=options)

# Load IMDb page
driver.get("https://www.imdb.com/search/title/?title_type=feature")
time.sleep(5)  # let all network requests settle

logs = driver.get_log("performance")

# Track matched requests
match_count = 0

print("\n🔍 Scanning network logs for GraphQL requests...\n")

for entry in logs:
    try:
        message = json.loads(entry["message"])["message"]
        if message["method"] == "Network.requestWillBeSent":
            request = message["params"]["request"]
            url = request.get("url", "")
            headers = request.get("headers", {})

            if "caching.graphql.imdb.com" in url:
                match_count += 1
                print(f"\n🎯 Match #{match_count}: {url}")

                # Clean headers
                filtered_headers = {
                    k: v for k, v in headers.items()
                    if k.lower() not in ["cookie", "host", "content-length"]
                }

                # Decode query parameters
                parsed_url = urlparse(url)
                params = parse_qs(parsed_url.query)

                # Decode variables
                if 'variables' in params:
                    try:
                        variables_json = json.loads(unquote(params['variables'][0]))
                        print("\n📦 Decoded Variables:")
                        print(json.dumps(variables_json, indent=2))
                    except Exception as e:
                        print("⚠️ Failed to decode variables:", e)

                # Decode persisted query info
                if 'extensions' in params:
                    try:
                        extensions_json = json.loads(unquote(params['extensions'][0]))
                        print("\n🔑 Persisted Query Info:")
                        print(json.dumps(extensions_json, indent=2))
                    except Exception as e:
                        print("⚠️ Failed to decode extensions:", e)

                # Replay the request
                response = requests.get(url, headers=filtered_headers)
                print("\n🧾 Status:", response.status_code)
                print("🧾 Response Preview:")
                print(response.text[:1000])  # truncate for readability
    except Exception:
        continue

driver.quit()

if match_count == 0:
    print("❌ No GraphQL requests to caching.graphql.imdb.com found.")
else:
    print(f"\n✅ Done. Total matches: {match_count}")
