import requests
import json
import os
from datetime import datetime

class NewsDataAPIFetcher:
    BASE_URL = "https://newsdata.io/api/1/news"

    def __init__(self, query, category):
        self.api_key = os.getenv("NEWSDATA_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set the 'NEWSDATA_API_KEY' environment variable.")
        
        self.query = query
        self.category = category
        self.output_file = self.generate_filename()

    def generate_filename(self):
        #MMDDYYYY
        today = datetime.today().strftime("%m%d%Y")
        return f"rawnews_{today}.json"

    def fetch_news(self):
        params = {
            'apikey': self.api_key,
            'q': self.query,
            'language': 'en',
            'category': self.category
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
                with open(self.output_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
                print(f"News data saved to '{self.output_file}'")
            except IOError as e:
                print(f"Failed to write to file: {e}")