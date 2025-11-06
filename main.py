# main.py
from api_pipeline import build_api_pipeline

def main():
    print("=== Chain of Responsibility: API Request Processing ===")

    #Create the chain pipeline
    pipeline = build_api_pipeline()

    #Example request
    request = {"query": "Artificial Intelligence"}

    #Process the request
    result = pipeline.handle(request)

    #Display output
    articles = result.get("articles", [])
    print(f"\n[Client] ✅ Final result: {len(articles)} articles returned.")
    if articles:
        print(f"[Client] Example article title: {articles[0].get('title', 'N/A')}")

    print("\n=== Second call to demonstrate cache ===")
    pipeline.handle({"query": "Artificial Intelligence"})


if __name__ == "__main__":
    main()
