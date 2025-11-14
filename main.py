from thenewsapi_fetcher import TheNewsAPIFetcher


def main():
    print("=== TheNewsAPI Demo ===")
    fetcher = TheNewsAPIFetcher(query="Artificial Intelligence")
    data = fetcher.fetch_news()

    if not data or "data" not in data:
        print("No data returned from TheNewsAPI.")
        return

    print(f"Total Articles: {len(data.get('data', []))}")
    for i, article in enumerate(data.get("data", [])[:3], 1):
        title = article.get("title")
        source = article.get("source")
        print(f"{i}. {title} — {source}")

    fetcher.save_news_to_file()


if __name__ == "__main__":
    main()
