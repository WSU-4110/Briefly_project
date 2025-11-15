import requests

import pytest
from unittest.mock import patch, MagicMock
from news_api_client import NewsAPIClient


#method 1: make_params()

def test_make_params_basic():
    client = NewsAPIClient("us")
    params = client.make_params()
    assert params["country"] == "us"
    assert params["apiKey"] == client.API_KEY
    assert "category" not in params

def test_make_params_with_category():
    client = NewsAPIClient("us")
    params = client.make_params("business")
    assert params["category"] == "business"


# method 2: validate_country()

def test_validate_country_valid():
    client = NewsAPIClient("us")
    assert client.validate_country() is True

def test_validate_country_wrong_length():
    client = NewsAPIClient("usa")
    with pytest.raises(ValueError):
        client.validate_country()

def test_validate_country_wrong_type():
    client = NewsAPIClient(123)
    with pytest.raises(TypeError):
        client.validate_country()


# method 3: send_request()

@patch("requests.get")
def test_send_request_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"articles": []}
    mock_get.return_value = mock_response

    client = NewsAPIClient()
    data = client.send_request()

    assert "articles" in data
    mock_get.assert_called_once()

@patch("requests.get")
def test_send_request_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    client = NewsAPIClient()
    with pytest.raises(RuntimeError):
        client.send_request()


# method 4: extract_titles()

def test_extract_titles_normal():
    client = NewsAPIClient()
    sample = {
        "articles": [
            {"title": "Hello"},
            {"title": None},
            {}
        ]
    }
    assert client.extract_titles(sample) == ["Hello", "Untitled", "Untitled"]

def test_extract_titles_missing_key():
    client = NewsAPIClient()
    with pytest.raises(KeyError):
        client.extract_titles({})


# method 5: count_articles()

def test_count_articles_present():
    client = NewsAPIClient()
    sample = {"articles": [{"a": 1}, {"a": 2}]}
    assert client.count_articles(sample) == 2

def test_count_articles_missing():
    client = NewsAPIClient()
    assert client.count_articles({}) == 0


# method 6: is_empty()

def test_is_empty_true():
    client = NewsAPIClient()
    assert client.is_empty({"articles": []}) is True
    assert client.is_empty({}) is True

def test_is_empty_false():
    client = NewsAPIClient()
    assert client.is_empty({"articles": [{"title": "X"}]}) is False
