import requests

class NewsAPIClient:
    BASE_URL = "https://newsapi.org/v2/top-headlines"
    API_KEY = "NEWSAPI_KEY"

    def __init__(self, country="us"):
        self.country = country

    #method 1
    def make_params(self, category=None):
        """Build request parameters."""
        params = {
            "country": self.country,
            "apiKey": self.API_KEY
        }
        if category:
            params["category"] = category
        return params

    #method 2
    def validate_country(self):
        """Check if country code is valid."""
        if not isinstance(self.country, str):
            raise TypeError("Country must be a string")
        if len(self.country) != 2:
            raise ValueError("Country code must be exactly 2 characters")
        return True

    #method 3
    def send_request(self, category=None):
        """Perform the API request."""
        params = self.make_params(category)
        response = requests.get(self.BASE_URL, params=params)

        if response.status_code != 200:
            raise RuntimeError("API request failed")

        return response.json()

    #method 4 -- after fixing it
    def extract_titles(self, json_data):
        """Return list of titles."""
        if "articles" not in json_data:
            raise KeyError("Missing articles")

        titles = []
        for item in json_data["articles"]:
            title = item.get("title", "Untitled")
            if title is None:
                title = "Untitled"
            titles.append(title)

        return titles

    #method 5
    def count_articles(self, json_data):
        """Return number of articles."""
        if "articles" not in json_data:
            return 0
        return len(json_data["articles"])

    #method 6
    def is_empty(self, json_data):
        """Check if no articles are present."""
        articles = json_data.get("articles", [])
        return len(articles) == 0
