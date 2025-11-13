import requests
import json
import os
from datetime import datetime
from news_fetcher_strategy import NewsFetcherStrategy


class NewsAPIFetcher(NewsFetcherStrategy):
    BASE_URL = "https://newsapi.org/v2/everything"

    def __init__(self, query, language="en", sort_by="publishedAt"):
        """Concrete strategy to fetch news articles from NewsAPI."""
        self.api_key = os.getenv("NEWSAPI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set the 'NEWSAPI_API_KEY' environment variable.")
        self.query = query
        self.language = language
        self.sort_by = sort_by
        self.output_file = self.generate_filename()

    def generate_filename(self):
        today = datetime.today().strftime("%m%d%Y")
        safe_query = "".join(c if c.isalnum() else "_" for c in self.query)
        return f"news_{safe_query}_{today}.json"

    def fetch_news(self, ticker=None):
        params = {
            "q": self.query,
            "language": self.language,
            "sortBy": self.sort_by,
            "apiKey": self.api_key
        }
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching news: {e}")
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
