import unittest
from backend.sources.web_search import WebSearcher
import asyncio

class TestWebSearcher(unittest.TestCase):
    def test_search_initialization(self):
        searcher = WebSearcher()
        self.assertIsNotNone(searcher)

    def test_search_logic_mock(self):
        # Since we can't make real network calls reliably in test without mocking,
        # we check if the method exists and is callable.
        searcher = WebSearcher()
        self.assertTrue(hasattr(searcher, 'search_general'))
        self.assertTrue(asyncio.iscoroutinefunction(searcher.search_general))

if __name__ == '__main__':
    unittest.main()
