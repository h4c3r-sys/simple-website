import random
from duckduckgo_search import DDGS

def search_viral_trends():
    """
    Searches for viral tech products on various social media platforms using DuckDuckGo.
    Returns a list of dictionaries containing title, link, and snippet.
    """
    queries = [
        "viral tech gadgets tiktok 2025",
        "trending tech products instagram reels 2025",
        "best viral gadgets to buy now reddit",
        "amazon finds tiktok viral 2025"
    ]

    results = []
    try:
        with DDGS() as ddgs:
            for query in queries:
                # Fetching a small number of results per query to avoid rate limits and keep it fast
                search_results = list(ddgs.text(query, max_results=3))
                for r in search_results:
                    title = r.get("title", "")
                    # Basic filtering to remove dictionary definitions
                    if "Definition" in title or "Wikipedia" in title or "Meaning" in title:
                        continue

                    results.append({
                        "title": title,
                        "link": r.get("href"),
                        "snippet": r.get("body"),
                        "platform": "Social Media" # Generalized for now
                    })

        # If we found very few results, mix in mock data to ensure a good demo experience
        if len(results) < 3:
            print("Few results found, adding mock data...")
            results.extend(get_mock_trends())

    except Exception as e:
        print(f"Error during search: {e}")
        # Fallback to some mock data if search fails (good for offline dev)
        return get_mock_trends()

    return results

def get_mock_trends():
    """Returns mock data for testing when internet search fails."""
    return [
        {
            "title": "Viral Transparent Wireless Earbuds on TikTok",
            "link": "https://tiktok.com/example1",
            "snippet": "These new transparent earbuds are taking over TikTok. Everyone is asking where to buy them! #tech #viral",
            "platform": "TikTok"
        },
        {
            "title": "Levitating Moon Lamp - Instagram Reels Trend",
            "link": "https://instagram.com/example2",
            "snippet": "The coolest desk accessory I've found. It actually floats! Links in comments.",
            "platform": "Instagram"
        },
        {
            "title": "Portable Mini Printer for Students",
            "link": "https://youtube.com/shorts/example3",
            "snippet": "Stop writing notes by hand. This mini printer connects to your phone and prints sticky notes instantly.",
            "platform": "YouTube"
        }
    ]
