import requests
import json
import os
from datetime import datetime
from news_fetcher_strategy import NewsFetcherStrategy


class TheNewsAPIFetcher(NewsFetcherStrategy):
    BASE_URL = "https://api.thenewsapi.com/v1/news/all"

    def __init__(self, query, language="en", sort="published_at"):
        """Concrete strategy to fetch news from TheNewsAPI."""
        self.api_key = os.getenv("THENEWSAPI_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set the 'THENEWSAPI_KEY' environment variable.")
        self.query = query
        self.language = language
        self.sort = sort
        self.output_file = self.generate_filename()

    def generate_filename(self):
        today = datetime.today().strftime("%m%d%Y")
        safe_query = ''.join(c if c.isalnum() else '_' for c in self.query)
        return f"thenewsapi_{safe_query}_{today}.json"

    def fetch_news(self, ticker=None):
        params = {
            "api_token": self.api_key,
            "search": self.query,
            "language": self.language,
            "sort": self.sort,
            "limit": 20
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching news from TheNewsAPI: {e}")
            return None

    def save_news_to_file(self):
        data = self.fetch_news()
        if data:
            try:
                with open(self.output_file, "w", encoding="utf-8") as file:
                    json.dump(data, file, indent=4)
                print(f"News data saved to '{self.output_file}'")
            except IOError as e:
                print(f"Failed to write to file: {e}")
