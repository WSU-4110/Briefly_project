"""
NewsAPI Python Client
---------------------
Lightweight client for https://newsapi.org/

Usage:
    from newsapi_client import NewsAPIClient
    api = NewsAPIClient()  # reads NEWS_API_KEY from environment or .env
    print(api.top_headlines(country="us"))
"""

from __future__ import annotations
import os
import typing as t
import requests

try:
    # Optional: load .env if present
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


class NewsAPIError(Exception):
    """Raised when the NewsAPI returns an error response."""


class NewsAPIClient:
    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: t.Optional[str] = None, timeout: int = 15) -> None:
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY not set. Set an environment variable or pass api_key to NewsAPIClient(...)."
            )
        self.timeout = timeout
        self.session = requests.Session()
        # Use header auth (preferred by NewsAPI)
        self.session.headers.update({"X-Api-Key": self.api_key})

    def _get(self, path: str, params: t.Optional[dict] = None) -> dict:
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params or {}, timeout=self.timeout)
        # Raise for transport errors, then parse JSON and handle API-level errors
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Try to include API error payload if available
            try:
                data = resp.json()
                msg = data.get("message") or data.get("error") or str(e)
            except Exception:
                msg = str(e)
            raise NewsAPIError(f"HTTP {resp.status_code}: {msg}") from e

        data = resp.json()
        # NewsAPI returns status: "ok" or "error"
        if isinstance(data, dict) and data.get("status") == "error":
            code = data.get("code", "unknown_error")
            message = data.get("message", "Unknown error")
            raise NewsAPIError(f"{code}: {message}")
        return data

    # ---------- Public endpoints ----------

    def top_headlines(
        self,
        *,
        country: t.Optional[str] = None,
        category: t.Optional[str] = None,
        sources: t.Optional[str] = None,
        q: t.Optional[str] = None,
        page_size: int = 20,
        page: int = 1,
    ) -> dict:
        """Get live top and breaking headlines."""
        params = {
            "country": country,
            "category": category,
            "sources": sources,
            "q": q,
            "pageSize": page_size,
            "page": page,
        }
        # remove None values
        params = {k: v for k, v in params.items() if v is not None}
        return self._get("top-headlines", params=params)

    def everything(
        self,
        q: t.Optional[str] = None,
        *,
        q_in_title: t.Optional[str] = None,
        sources: t.Optional[str] = None,
        domains: t.Optional[str] = None,
        exclude_domains: t.Optional[str] = None,
        from_param: t.Optional[str] = None,
        to: t.Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20,
        page: int = 1,
        search_in: t.Optional[str] = None,
    ) -> dict:
        """Search across millions of articles from many sources."""
        params = {
            "q": q,
            "qInTitle": q_in_title,
            "sources": sources,
            "domains": domains,
            "excludeDomains": exclude_domains,
            "from": from_param,
            "to": to,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
            "searchIn": search_in,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._get("everything", params=params)

    def sources(self, *, category: t.Optional[str] = None, language: t.Optional[str] = "en", country: t.Optional[str] = None) -> dict:
        """List the news sources available on NewsAPI."""
        params = {"category": category, "language": language, "country": country}
        params = {k: v for k, v in params.items() if v is not None}
        return self._get("top-headlines/sources", params=params)

    # ---------- Convenience helpers ----------

    def paginate_everything(self, q: str, pages: int = 3, **kwargs) -> t.Iterable[dict]:
        """Generator that yields articles across multiple pages for `everything`."""
        for p in range(1, pages + 1):
            data = self.everything(q=q, page=p, **kwargs)
            for article in data.get("articles", []):
                yield article
            # Stop early if fewer than requested page size returned
            if len(data.get("articles", [])) < kwargs.get("page_size", 20):
                break
