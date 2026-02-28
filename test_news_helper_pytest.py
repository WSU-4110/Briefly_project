import pytest
from datetime import datetime
from raw_news_helper import NewsHelper

@pytest.fixture
def helper():
    return NewsHelper()

def test_extract_domain_valid(helper):
    url = "https://www.cnn.com/finance/article"
    assert helper._extract_domain(url) == "cnn.com"

def test_normalize_structure(helper):
    data = helper._normalize("newsapi", "Title", "https://cnn.com/article")
    assert "title" in data
    assert data["api_source"] == "newsapi"
    assert data["source_domain"] == "cnn.com"

def test_basic_valid_good_article(helper):
    art = {"title": "Stock market update", "url": "http://example.com"}
    assert helper._basic_valid(art) is True

def test_basic_valid_banned_title(helper):
    art = {"title": "Celebrity gossip show", "url": "http://cnn.com"}
    assert helper._basic_valid(art) is False

def test_dedup_removes_duplicates(helper):
    articles = [
        {"title": "A", "url": "http://a.com"},
        {"title": "A", "url": "http://a.com"},
        {"title": "B", "url": "http://b.com"}
    ]
    result = helper._dedup(articles)
    assert len(result) == 2

def test_today_filename_format(helper):
    today = datetime.today().strftime("%m%d%Y")
    expected = f"RAW_NEWS_{today}.json"
    assert helper._today_filename() == expected
