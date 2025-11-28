import logging
from .web_search import WebSearcher

logger = logging.getLogger(__name__)

class SocialMediaScanner:
    def __init__(self):
        # We reuse the web searcher to "scrape" social media via Google
        # (e.g. site:reddit.com)
        self.searcher = WebSearcher()

    async def scan_sentiment(self, topic: str):
        """
        Scans Reddit and Twitter via Google Search for discussions.
        """
        logger.info(f"Scanning social media for: {topic}")

        platforms = [
            ("Reddit", f"site:reddit.com {topic}"),
            ("Twitter/X", f"site:twitter.com {topic}"),
            ("Instagram", f"site:instagram.com {topic}")
        ]

        aggregated_data = {}

        for platform_name, query in platforms:
            results = await self.searcher.search_general(query, num_results=3)
            # Simple format: Just list the titles/descriptions found
            texts = [f"{r.get('title', '')}: {r.get('description', '')}" for r in results if isinstance(r, dict)]
            aggregated_data[platform_name] = texts

        return aggregated_data
