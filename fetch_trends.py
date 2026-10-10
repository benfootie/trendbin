import os
import json
import datetime
import requests

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
#SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
#SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

# Matching the 3 countries in your index.html dropdown
COUNTRIES = {"US": "United States", "IN": "India", "GB": "United Kingdom"}

def fetch_youtube(code):
    if not YOUTUBE_API_KEY: return []
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "snippet,statistics", "chart": "mostPopular", "regionCode": code, "maxResults": 50, "key": YOUTUBE_API_KEY}
    try:
        res = requests.get(url, params=params, timeout=10)
        videos = []
        for item in res.json().get("items", []):
            snippet = item.get("snippet", {})
            thumbs = snippet.get("thumbnails", {})
            thumb = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url", "")
            views = int(item.get("statistics", {}).get("viewCount", 0))
            videos.append({
                "title": snippet.get("title", "Untitled"),
                "channel": snippet.get("channelTitle", "YouTube"),
                "metrics": f"{views:,} views",
                "url": f"https://www.youtube.com/watch?v={item.get('id')}",
                "thumbnail": thumb
            })
        return videos
    except: return []



def fetch_github():
    try:
        last_week = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"https://api.github.com/search/repositories?q=created:>{last_week}&sort=stars&order=desc&per_page=20"
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token: headers["Authorization"] = f"Bearer {token}"
        res = requests.get(url, headers=headers, timeout=10)
        trends = []
        for repo in res.json().get("items", []):
            trends.append({
                "title": repo.get("full_name"), "channel": repo.get("language") or "Mixed",
                "metrics": f"{repo.get('stargazers_count'):,} stars", "url": repo.get("html_url"),
                "thumbnail": repo.get("owner", {}).get("avatar_url", "")
            })
        return trends
    except: return []

def fetch_bluesky():
    try:
        res = requests.get("https://public.api.bsky.app/xrpc/app.bsky.unspecced.getTrendingTopics", timeout=10)
        trends = []
        for topic in res.json().get("topics", [])[:20]:
            title = topic.get("displayName") or topic.get("topic")
            trends.append({
                "title": title, "channel": "Bluesky Trending", "metrics": "Trending Topic",
                "url": topic.get("link", f"https://bsky.app/search?q={title}"), "thumbnail": ""
            })
        return trends
    except: return []

def main():
    os.makedirs("data", exist_ok=True)
    payload = {"updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "countries": {}, "global": {}}
    
    for code, name in COUNTRIES.items():
        payload["countries"][code] = {"name": name, "youtube": fetch_youtube(code)}
        
    payload["global"] = { "github": fetch_github(), "bluesky": fetch_bluesky()}

    with open("data/trends.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()