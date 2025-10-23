# 📰 NewsAPI Python Client

A clean, GitHub-ready Python client for [NewsAPI.org](https://newsapi.org/).

## Features
- Simple `NewsAPIClient` class using header auth (`X-Api-Key`)
- Endpoints: `top_headlines`, `everything`, `sources`
- Pagination helper for `everything`
- `.env` support with `python-dotenv`
- Minimal example script

## Quickstart

```bash
# 1) Clone or unzip this project and cd into it
pip install -r requirements.txt

# 2) Add your real key (do NOT commit it)
cp .env.example .env
# then edit .env and paste your real key
# NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 3) Run example
python src/example_main.py
```

## Usage in code

```python
from newsapi_client import NewsAPIClient
api = NewsAPIClient()  # reads NEWS_API_KEY from environment or .env
res = api.top_headlines(country="us", page_size=5)
print(res["articles"][0]["title"])
```

## Security
Never hardcode your API key in code. Keep `.env` out of Git with the included `.gitignore`.

## License
MIT
