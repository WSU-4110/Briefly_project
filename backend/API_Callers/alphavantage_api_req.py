import requests
import json
import os
from datetime import datetime

from news_fetcher_strategy import NewsFetcherStrategy

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
        #MMDDYYYY
        today = datetime.today().strftime("%m%d%Y")
        return f"stockdata_{self.symbol}_{today}.json"
    
    def fetch_news(self, ticker):
        params = {
            "function": self.function,
            "symbol": self.symbol,
            "apikey": self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"An error occured: {e}")
            return None
        
    def save_news_to_file(self):
        data = self.fetch_news()
        if data:
            try:
                with open(self.output_file, 'w', encoding="utf-8") as file:
                    json.dump(data, file, indent=4)
                print(f"Stock data saved to '{self.output_file}'")
            except IOError as e:
                print(f"Failed to write to file: {e}")