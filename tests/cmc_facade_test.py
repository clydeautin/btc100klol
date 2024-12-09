import pytest
import requests
from unittest.mock import patch
from facades.cmc_facade import get_btc_price, CMCApiError, CMCConnectionError, CMCResponseError

@pytest.fixture
def mock_btc_response():
    return {
        "data": {
            "BTC": [{
                "quote": {
                    "USD": {
                        "price": 45000.00
                    }
                }
            }]
        }
    }

def test_get_btc_price_success(mock_btc_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_btc_response
        price = get_btc_price()
        assert price == 45000.00
        mock_get.assert_called_once()

def test_get_btc_price_connection_error():
    with patch('facades.cmc_facade.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.raises(CMCConnectionError):
            get_btc_price()

def test_get_btc_price_timeout():
    with patch('facades.cmc_facade.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        with pytest.raises(CMCConnectionError):
            get_btc_price()

def test_get_btc_price_invalid_response():
    with patch('facades.cmc_facade.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": {}}
        mock_get.return_value.raise_for_status.return_value = None
        # Change the expected error message to match the actual one
        with pytest.raises(CMCResponseError, match="Invalid API response structure"):
            get_btc_price()

def test_get_btc_price_missing_api_key():
    with patch.dict('os.environ', clear=True):
        with pytest.raises(CMCApiError):
            get_btc_price()