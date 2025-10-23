# File: raw_news.py
# Purpose:
#   - Collect business/finance news from 4 APIs
#   - Normalize shape, lightly validate, deduplicate
#   - Save to RAW_NEWS_MMDDYYYY.json


import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests



API_KEYS = {
    "newsapi":       "4250ef418f764a9ebdc675c0178af484",
    "thenewsapi":    "a3zJgKafN7XzCJM33W83xxzoDvJgONLCLYrK3yPK",
    "newsdata":      "pub_60f773cbc64b4ac49525727dfe268cca",
    "alphavantage":  "IQ82KVHO45RDP77C",
}

DEFAULT_QUERIES = ["finance", "economy", "federal reserve", "market", "business"]

def _today_filename(prefix: str = "RAW_NEWS", ext: str = "json") -> str:
    # teammate style (MMDDYYYY), but with RAW_NEWS name
    stamp = datetime.today().strftime("%m%d%Y")
    return f"{prefix}_{stamp}.{ext}"

def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        net = urlparse(url).netloc.lower()
        return net.replace("www.", "")
    except Exception:
        return "unknown"

def _normalize(
    *, source_name: str, title: str, url: str, description: str = "", published: str = "", image_url: str = "", language: str = "en", raw: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "title": title or "",
        "description": description or "",
        "url": url or "",
        "source": source_name or "",
        "published_at": published or "",
        "api_source": source_name.lower(),
        "source_domain": _extract_domain(url or ""),
        "image_url": image_url or "",
        "language": language or "en",
        "raw_api_data": raw or {},
    }

def _basic_valid(a: Dict[str, Any]) -> bool:
    # Minimal guardrails only
    if not a.get("title") or not a.get("url"):
        return False
    t = (a.get("title") or "").lower()
    # keep it broad; just avoid obvious junk
    banned = ["celebrity", "horoscope", "lottery", "gossip"]
    if any(b in t for b in banned):
        return False
    return True

def _dedup(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    seen_urls = set()
    seen_title_pub = set()
    for it in items:
        link = (it.get("url") or "").strip().lower()
        key2 = ((it.get("title") or "").strip().lower(), (it.get("published_at") or "").strip())
        if link:
            if link in seen_urls:
                continue
            seen_urls.add(link)
            out.append(it)
        else:
            if key2 in seen_title_pub:
                continue
            seen_title_pub.add(key2)
            out.append(it)
    return out


def fetch_newsapi(queries: List[str]) -> List[Dict[str, Any]]:
    key = API_KEYS.get("newsapi")
    if not key:
        return []
    url = "https://newsapi.org/v2/everything"
    out = []
    since = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d")
    for q in queries:
        try:
            resp = requests.get(
                url,
                params={
                    "apiKey": key,
                    "q": q,
                    "language": "en",
                    "from": since,
                    "sortBy": "relevancy",
                    "pageSize": 30,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for a in data.get("articles", []):
                # newsapi shape
                title = a.get("title") or ""
                if title == "[Removed]":
                    continue
                item = _normalize(
                    source_name="newsapi",
                    title=title,
                    url=a.get("url") or "",
                    description=a.get("description") or "",
                    published=a.get("publishedAt") or "",
                    image_url=a.get("urlToImage") or "",
                    language="en",
                    raw=a,
                )
                if _basic_valid(item):
                    out.append(item)
            time.sleep(0.5)
        except Exception:
            continue
    return out

def fetch_thenewsapi(queries: List[str]) -> List[Dict[str, Any]]:
    key = API_KEYS.get("thenewsapi")
    if not key:
        return []
    url = "https://api.thenewsapi.com/v1/news/all"
    out = []
    for q in queries:
        try:
            resp = requests.get(
                url,
                params={
                    "api_token": key,
                    "search": q,
                    "language": "en",
                    "categories": "business",
                    "limit": 50,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for a in data.get("data", []):
                item = _normalize(
                    source_name="thenewsapi",
                    title=a.get("title") or "",
                    url=a.get("url") or "",
                    description=a.get("description") or "",
                    published=a.get("published_at") or "",
                    image_url=a.get("image_url") or "",
                    language=a.get("language") or "en",
                    raw=a,
                )
                if _basic_valid(item):
                    out.append(item)
            time.sleep(0.5)
        except Exception:
            continue
    return out

def fetch_newsdata(queries: List[str], max_pages: int = 1) -> List[Dict[str, Any]]:
    # merge style from teammate: simple params + optional pagination
    key = API_KEYS.get("newsdata")
    if not key:
        return []
    base_url = "https://newsdata.io/api/1/latest"
    out = []
    for q in queries:
        next_page = None
        for _ in range(max_pages):
            try:
                params = {
                    "apikey": key,
                    "q": q,
                    "category": "business",
                    "language": "en",
                    "size": 10,
                }
                if next_page:
                    params["page"] = next_page
                resp = requests.get(base_url, params=params, timeout=15)
                if resp.status_code != 200:
                    break
                data = resp.json()
                if data.get("status") not in ("success", "ok"):
                    break
                for a in data.get("results", []):
                    item = _normalize(
                        source_name="newsdata",
                        title=a.get("title") or "",
                        url=a.get("link") or "",
                        description=a.get("description") or "",
                        published=a.get("pubDate") or "",
                        image_url=a.get("image_url") or "",
                        language=a.get("language") or "en",
                        raw=a,
                    )
                    if _basic_valid(item):
                        out.append(item)
                next_page = data.get("nextPage")
                if not next_page:
                    break
                time.sleep(0.8)
            except Exception:
                break
        time.sleep(0.5)
    return out

def fetch_alphavantage() -> List[Dict[str, Any]]:
    key = API_KEYS.get("alphavantage")
    if not key:
        return []
    url = "https://www.alphavantage.co/query"
    topics = ["financial_markets", "economy_fiscal", "earnings"]
    out = []
    for t in topics:
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "apikey": key,
                "topics": t,
                "time_from": (datetime.utcnow() - timedelta(hours=24)).strftime("%Y%m%dT%H%M"),
                "limit": 40,
                "sort": "RELEVANCE",
            }
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if "feed" not in data:
                # respect rate limiting if present
                if "Note" in data:
                    time.sleep(20)
                continue
            for a in data.get("feed", [])[:20]:
                item = _normalize(
                    source_name="alphavantage",
                    title=a.get("title") or "",
                    url=a.get("url") or "",
                    description=(a.get("summary") or "")[:500],
                    published=a.get("time_published") or "",
                    image_url=a.get("banner_image") or "",
                    language="en",
                    raw=a,
                )
                if _basic_valid(item):
                    out.append(item)
            time.sleep(1.0)
        except Exception:
            continue
    return out


def collect_news(target_count: int = 100) -> List[Dict[str, Any]]:
    # Phase 1: fetch
    items: List[Dict[str, Any]] = []
    items += fetch_newsapi(DEFAULT_QUERIES)
    items += fetch_thenewsapi(DEFAULT_QUERIES)
    items += fetch_newsdata(DEFAULT_QUERIES, max_pages=1)
    items += fetch_alphavantage()

    # Phase 2: dedup + trim
    unique = _dedup(items)
    # keep it simple: just cap count
    final = unique[:target_count]

    # add simple sequential ids
    for i, it in enumerate(final, 1):
        it["id"] = i

    return final

def save_json_articles(articles: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    if not filename:
        filename = _today_filename(prefix="RAW_NEWS", ext="json")
    out = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_articles": len(articles),
            "sources": list({a.get("api_source") for a in articles}),
        },
        "articles": articles,
    }
    path = os.path.join("/tmp", filename) if os.environ.get("AWS_EXECUTION_ENV") else filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[IO] saved -> {path}")
    return path


def main():
    print("NEWS Collector — minimal, multi-source, deduped")
    arts = collect_news(target_count=100)
    save_json_articles(arts)  # RAW_NEWS_MMDDYYYY.json

if __name__ == "__main__":
    main()


def lambda_handler(event, context):
    import boto3
    try:
        arts = collect_news(target_count=100)
        local_path = save_json_articles(arts)  # /tmp/RAW_NEWS_MMDDYYYY.json
        base_name = os.path.basename(local_path)

        # Use env var if provided; otherwise a generic name (no MQV trail)
        bucket = os.environ.get("RAW_NEWS_BUCKET", "rawnews-bucket")
        key = f"daily/{base_name}"

        s3 = boto3.client("s3")
        s3.upload_file(local_path, bucket, key)
        return {"statusCode": 200, "body": f"Uploaded {base_name} to s3://{bucket}/{key}"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {e}"}
