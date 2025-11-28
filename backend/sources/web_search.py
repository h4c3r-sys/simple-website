from googlesearch import search
import requests
from bs4 import BeautifulSoup
import logging
import asyncio

logger = logging.getLogger(__name__)

class WebSearcher:
    async def search_general(self, query: str, num_results: int = 5):
        """
        Searches Google for the query and returns titles and snippets.
        Note: googlesearch-python is synchronous, so we run it in a thread to avoid blocking.
        """
        logger.info(f"Searching web for: {query}")

        def _blocking_search():
            results = []
            try:
                # search() returns a generator of URLs
                urls = search(query, num_results=num_results, advanced=True)
                for result in urls:
                    results.append({
                        "title": result.title,
                        "url": result.url,
                        "description": result.description
                    })
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return [{"error": "Search limit reached or network error."}]
            return results

        return await asyncio.to_thread(_blocking_search)

    async def search_trends(self, niche: str):
        """
        Searches for 'trends in [niche] 2024/2025'
        """
        query = f"latest trends in {niche} 2024 2025 business"
        return await self.search_general(query, num_results=5)

    async def scrape_content(self, url: str):
        """
        Simple scraper to get text from a URL.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract paragraphs
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text() for p in paragraphs[:5]]) # First 5 paragraphs
            return text
        except Exception as e:
            return f"Failed to scrape {url}: {e}"
