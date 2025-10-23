"""
news_fetcher_strategy.py
------------------------
Example unified fetcher using TheNewsAPI.
"""

from thenewsapi_req import get_top_headlines, search_news

def fetch_news(source="thenewsapi", query=None):
    if source == "thenewsapi":
        if query:
            return search_news(query)
        else:
            return get_top_headlines()
    else:
        raise ValueError(f"Unsupported source: {source}")

if __name__ == "__main__":
    news = fetch_news(query="technology")
    for article in news.get("data", [])[:5]:
        print(article.get("title"))
