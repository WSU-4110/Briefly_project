import os
import sys

# This makes sure Python can find alphavantage_api_req.py
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

import pytest
from unittest.mock import patch, MagicMock, mock_open

from backend.API_Callers.alphavantage_api_req import AlphaVantageAPIFetcher


# ---------- TEST 1: Constructor ERROR when API key missing ----------
def test_init_missing_api_key(monkeypatch):
    monkeypatch.delenv("ALPHAVANTAGE_API_KEY", raising=False)

    with pytest.raises(ValueError):
        AlphaVantageAPIFetcher("AAPL")


# ---------- TEST 2: Constructor initializes correctly ----------
def test_init_success(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")

    fetcher = AlphaVantageAPIFetcher("AAPL")

    assert fetcher.symbol == "AAPL"
    assert fetcher.function == "TIME_SERIES_DAILY"
    assert "stockdata_AAPL_" in fetcher.output_file


# ---------- TEST 3: generate_filename produces correct format ----------
def test_generate_filename(monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")
    fetcher = AlphaVantageAPIFetcher("AAPL")

    filename = fetcher.generate_filename()

    today = __import__("datetime").datetime.today().strftime("%m%d%Y")
    assert filename.endswith("stockdata_AAPL_{today}.json")


# ---------- TEST 4: fetch_news returns data when API succeeds ----------
@patch("backend.API_Callers.alphavantage_api_req.requests.get")
def test_fetch_news_success(mock_get, monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")

    fake_response = {"Time Series (Daily)": {"value": 123}}

    mock_resp = MagicMock()
    mock_resp.json.return_value = fake_response
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    fetcher = AlphaVantageAPIFetcher("AAPL")
    data = fetcher.fetch_news("AAPL")

    assert data == fake_response
    mock_get.assert_called_once()


# ---------- TEST 5: fetch_news handles API failure ----------
@patch("backend.API_Callers.alphavantage_api_req.requests.get")
def test_fetch_news_failure(mock_get, monkeypatch):
    from requests.exceptions import RequestException

    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")
    mock_get.side_effect = RequestException("Network failed")

    fetcher = AlphaVantageAPIFetcher("AAPL")
    result = fetcher.fetch_news("AAPL")

    assert result is None


# ---------- TEST 6: save_news_to_file writes file when data exists ----------
@patch("backend.API_Callers.alphavantage_api_req.open", new_callable=mock_open)
@patch("backend.API_Callers.alphavantage_api_req.AlphaVantageAPIFetcher.fetch_news")
def test_save_news_to_file_success(mock_fetch_news, mock_file, monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")

    mock_fetch_news.return_value = {"test": 123}

    fetcher = AlphaVantageAPIFetcher("AAPL")
    fetcher.save_news_to_file()

    mock_fetch_news.assert_called_once_with("AAPL")
    mock_file.assert_called_once()


# ---------- TEST 7: save_news_to_file does nothing when fetch returns None ----------
@patch("backend.API_Callers.alphavantage_api_req.AlphaVantageAPIFetcher.fetch_news")
def test_save_news_to_file_no_data(mock_fetch_news, monkeypatch):
    monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "dummykey")

    mock_fetch_news.return_value = None

    fetcher = AlphaVantageAPIFetcher("AAPL")
    result = fetcher.save_news_to_file()

    assert result is None
    mock_fetch_news.assert_called_once_with("AAPL")
