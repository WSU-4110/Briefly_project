# api_handlers.py
from request_handler import RequestHandler
from newsapi_fetcher import NewsAPIFetcher

class ValidationHandler(RequestHandler):
    """Ensures the API request is valid before proceeding."""
    def handle(self, request):
        query = request.get("query", "").strip()
        if not query:
            raise ValueError("Invalid request: 'query' cannot be empty.")
        print(f"[ValidationHandler] ✅ Query '{query}' validated successfully.")
        return super().handle(request)


class CacheHandler(RequestHandler):
    """Checks cache before making API calls."""
    _cache = {}

    def handle(self, request):
        query = request["query"]
        if query in CacheHandler._cache:
            print(f"[CacheHandler] ⚡ Using cached results for '{query}'.")
            request["articles"] = CacheHandler._cache[query]
            return request

        print(f"[CacheHandler] No cache found for '{query}', passing to next handler...")
        result = super().handle(request)
        CacheHandler._cache[query] = result.get("articles", [])
        print(f"[CacheHandler] 🗄️ Cached {len(CacheHandler._cache[query])} articles for '{query}'.")
        return result


class FetchHandler(RequestHandler):
    """Fetches articles from the NewsAPI."""
    def __init__(self):
        super().__init__()
        self.fetcher = NewsAPIFetcher()  

    def handle(self, request):
        query = request["query"]
        print(f"[FetchHandler] 🌐 Fetching new articles for '{query}' from NewsAPI...")
        data = self.fetcher.fetch_news(query)
        articles = data.get("articles", [])
        request["articles"] = articles
        print(f"[FetchHandler] 📦 Retrieved {len(articles)} articles.")
        return super().handle(request)
