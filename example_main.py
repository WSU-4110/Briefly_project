"""
Example usage of the NewsAPI Python client.
Run:
    pip install -r requirements.txt
    # Set your key in environment or .env
    python src/example_main.py
"""
import os
from newsapi_client import NewsAPIClient

def main():
    # NEWS_API_KEY is read automatically by the client if present in environment or .env
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("❌ Missing NEWS_API_KEY. Set it in your environment or create a .env file.")
        return

    client = NewsAPIClient(api_key=api_key)
    data = client.top_headlines(country="us", page_size=5)
    for i, a in enumerate(data.get("articles", []), start=1):
        print(f"{i}. {a.get('title')}")

if __name__ == "__main__":
    main()
