from newsapi_fetcher import NewsAPIFetcher


def main():
    print("=== NewsAPI Demo ===")
    fetcher = NewsAPIFetcher(query="Artificial Intelligence")
    data = fetcher.fetch_news()

    if not data:
        print("No data returned from NewsAPI.")
        return

    print(f"Total Results: {data.get('totalResults', 0)}")
    for i, article in enumerate(data.get("articles", [])[:3], 1):
        title = article.get("title")
        source = article.get("source", {}).get("name")
        print(f"{i}. {title} — {source}")

    fetcher.save_news_to_file()


if __name__ == "__main__":
    main()
