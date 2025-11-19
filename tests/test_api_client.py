import os
import sys

import json
import tempfile
import pytest
from datetime import datetime
from unittest import mock

import requests

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from backend.API_Callers.newsdata_api_req import NewsDataAPIFetcher

#USES METHOD BEFORE AND AFTER EVERY TEST
@pytest.fixture(autouse=True)
def clear_env_api_key():
    #Ensure NEWSDATA_API_KEY is cleared before each test.
    if "NEWSDATA_API_KEY" in os.environ:
        del os.environ["NEWSDATA_API_KEY"]
    yield
    #Ensure NEWSDATA_API_KEY is cleared after each test.
    if "NEWSDATA_API_KEY" in os.environ:
        del os.environ["NEWSDATA_API_KEY"]

def test_init_without_api_key_raises():
    with pytest.raises(ValueError) as excinfo:  #excinfo is Exception Info
        NewsDataAPIFetcher(query="inflation", category="economy")
    #test to see if error message includes "API key not found"
    assert "API key not found" in str(excinfo.value)

def test_generate_filename_contains_today_date(monkeypatch):
    # Set environment key so __init__ works
    os.environ["NEWSDATA_API_KEY"] = "fake_key"
    fetcher = NewsDataAPIFetcher(query="inflation", category="economy")
    # Monkeypatch date to predictable value
    fixed_date = datetime(2020, 1, 15)
    # Replaces datetime method with temporary monkeypatch mock
    monkeypatch.setattr("newsdata_api_req.datetime", mock.Mock(today=mock.Mock(return_value=fixed_date)))
    filename = fetcher.generate_filename()
    # Tests if file name is created correclty
    assert filename == "rawnews_01152020.json"

def test_fetch_news_success(monkeypatch):
    os.environ["NEWSDATA_API_KEY"] = "fake_key"
    fetcher = NewsDataAPIFetcher(query="inflation", category="economy")

    fake_response = mock.Mock()
    fake_response.raise_for_status = mock.Mock(return_value=None)
    fake_response.json = mock.Mock(return_value={"status": "ok", "results": []})
    # Replaces requests.get() with temporary monkeypatch mock
    monkeypatch.setattr(requests, "get", mock.Mock(return_value=fake_response))

    data = fetcher.fetch_news()
    assert data == {"status": "ok", "results": []}
    # also verify requests.get was called with correct URL & params
    requests.get.assert_called_once_with(
        NewsDataAPIFetcher.BASE_URL,
        params={
            'apikey': "fake_key",
            'q': "inflation",
            'language': 'en',
            'category': "economy"
        }
    )

def test_fetch_news_failure(monkeypatch):
    os.environ["NEWSDATA_API_KEY"] = "fake_key"
    fetcher = NewsDataAPIFetcher(query="inflation", category="economy")

    # Simulate requests.get raising an exception
    monkeypatch.setattr(requests, "get", mock.Mock(side_effect=requests.exceptions.RequestException("fail")))
    data = fetcher.fetch_news()
    assert data is None

def test_save_news_to_file_success(tmp_path, monkeypatch):
    os.environ["NEWSDATA_API_KEY"] = "fake_key"
    fetcher = NewsDataAPIFetcher(query="inflation", category="economy")
    # Override output_file to a file in tmp_path
    fetcher.output_file = tmp_path / "testfile.json"

    fake_data = {"status": "ok", "results": [1,2,3]}
    monkeypatch.setattr(fetcher, "fetch_news", mock.Mock(return_value=fake_data))

    fetcher.save_news_to_file()

    # Check file exists and contains the JSON
    content = json.loads((tmp_path / "testfile.json").read_text(encoding="utf-8"))
    assert content == fake_data

def test_save_news_to_file_io_error(monkeypatch, tmp_path, capsys):
    os.environ["NEWSDATA_API_KEY"] = "fake_key"
    fetcher = NewsDataAPIFetcher(query="inflation", category="economy")
    # Set output_file to a path where writing will fail (e.g., directory instead of file)
    fetcher.output_file = tmp_path  # directory rather than file

    fake_data = {"status": "ok", "results": []}
    monkeypatch.setattr(fetcher, "fetch_news", mock.Mock(return_value=fake_data))

    # Run save
    fetcher.save_news_to_file()

    # Capture printed output
    captured = capsys.readouterr()
    assert "Failed to write to file" in captured.out