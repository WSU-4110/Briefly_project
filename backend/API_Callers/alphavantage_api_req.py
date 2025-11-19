import requests
import json
import os
from datetime import datetime

from backend.API_Callers.news_fetcher_strategy import NewsFetcherStrategy

class AlphaVantageAPIFetcher(NewsFetcherStrategy):
    BASE_URL = 'https://www.alphavantage.co/query'

    def __init__(self, symbol, function="TIME_SERIES_DAILY"):
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set the 'ALPHAVANTAGE_API_KEY' environment variable.")
        
        self.symbol = symbol
        self.function = function
        self.output_file = self.generate_filename()

    def generate_filename(self):
        today = datetime.today().strftime("%m%d%Y")
        filename = f"stockdata_{self.symbol}_{today}.json"

        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        data_dir = os.path.abspath(data_dir)

        os.makedirs(data_dir, exist_ok=True)

        return os.path.join(data_dir, filename)
    
    def fetch_news(self, ticker):
        params = {
            "function": self.function,
            "symbol": ticker,
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        
    def save_news_to_file(self):
        data = self.fetch_news(self.symbol)
        if data:
            try:
                with open(self.output_file, 'w', encoding="utf-8") as file:
                    json.dump(data, file, indent=4)
                print(f"Stock data saved to '{self.output_file}'")
            except IOError as e:
                print(f"Failed to write to file: {e}")
