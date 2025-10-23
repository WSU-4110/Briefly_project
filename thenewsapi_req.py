"""
thenewsapi_req.py
-----------------
Python client for fetching headlines from TheNewsAPI (https://www.thenewsapi.com/).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

API_KEY = os.getenv("THENEWSAPI_KEY")
BASE_URL = "https://api.thenewsapi.com/v1"

if not API_KEY:
    raise ValueError("❌ Missing THENEWSAPI_KEY in .env file")

def get_top_headlines(locale="us", limit=5):
    """Fetch top headlines from TheNewsAPI."""
    url = f"{BASE_URL}/news/top"
    params = {"api_token": API_KEY, "locale": locale, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def search_news(query, locale="us", limit=5):
    """Search news articles by keyword."""
    url = f"{BASE_URL}/news/all"
    params = {"api_token": API_KEY, "search": query, "locale": locale, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    data = get_top_headlines()
    for article in data.get("data", [])[:5]:
        print(article.get("title"))
