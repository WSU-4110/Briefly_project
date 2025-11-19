import json
import re
import os
from datetime import datetime

class NewsFilter:
    def __init__(self):
        self.stock_tips_keywords = [
            "buy recommendation", "sell recommendation", "strong buy", "strong sell",
            "analyst rating", "analyst upgrade", "analyst downgrade", "price target",
            "price prediction", "forecast", "earnings estimate", "earnings preview",
            "earnings outlook", "dividend forecast", "market tip", "stock tip",
            "tip for investors", "short squeeze", "long position"
        ]

        self.earnings_keywords = [
            "quarterly earnings preview", "earnings", "profit forecast",
            "revenue guidance", "results preview", "eps forecast"
        ]

        self.local_news_keywords = [
            "local community", "regional office", "branch opening", "small business announcement",
            "town hall meeting", "company picnic", "employee event", "corporate anniversary",
            "generic press release", "company statement", "product launch—region", 
            "plant closure", "city council partnership", "small contract award"
        ]

        self.non_us_keywords = [
            "asia pacific region", "latin america region", "middle east region",
            "emerging markets only", "non‑us operations", "overseas subsidiary",
            "foreign exchange only", "china market focus", "india market expansion",
            "european union only", "non‑us investor", "ASEAN"
        ]

    def contains_keywords(self, text, keywords):
        if not text:
            return False
        text_lower = text.lower()
        return any(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower)
                   for keyword in keywords)

    def exclude(self, article):
        combined_text = (
            article.get('title', '') + ' ' +
            article.get('description', '')
        ).lower()

        if (self.contains_keywords(combined_text, self.stock_tips_keywords) or
            self.contains_keywords(combined_text, self.earnings_keywords) or
            self.contains_keywords(combined_text, self.local_news_keywords) or
            self.contains_keywords(combined_text, self.non_us_keywords)):
            return True

        return False

    def filter_articles(self, articles):
        return [article for article in articles if not self.exclude(article)]


if __name__ == "__main__":
    # Daily file names
    # Will need to be updated to be able to look for files in
    # correct folder
    today = datetime.today().strftime("%m%d%Y")
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    input_filename = f"rawnews_{today}.json"
    output_filename = f"filtered_news_{today}.json"

    input_file = os.path.join(data_dir, input_filename)
    output_file = os.path.join(data_dir, output_filename)

    with open(input_file, "r", encoding="utf-8") as file_in:
        data = json.load(file_in)

    articles = data.get("results", [])

    # Filter
    filter = NewsFilter()
    filtered_articles = filter.filter_articles(articles)

    # Save filtered articles to a new JSON file
    with open(output_file, "w", encoding="utf-8") as file_out:
        json.dump(filtered_articles, file_out, indent=2, ensure_ascii=False)