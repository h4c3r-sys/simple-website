from duckduckgo_search import DDGS

def find_aliexpress_links(product_name):
    """
    Searches for the product on AliExpress using DuckDuckGo to find direct product links.
    Returns a list of potential links.
    """
    if not product_name or product_name == "Unknown Product":
        return []

    query = f"site:aliexpress.com buy {product_name}"
    links = []

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            for r in results:
                links.append({
                    "title": r.get("title"),
                    "link": r.get("href"),
                    "price_estimate": "Check Link" # DDG doesn't reliably give price in snippets
                })
    except Exception as e:
        print(f"Sourcing Error: {e}")

    return links
