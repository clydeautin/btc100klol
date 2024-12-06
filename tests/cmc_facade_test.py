import pytest
import requests
from unittest.mock import patch
from facades.cmc_facade import get_btc_price

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

def test_get_btc_price_api_error():
    with patch('facades.cmc_facade.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        with pytest.raises(Exception) as exc_info:
            get_btc_price()
        assert "Failed to fetch BTC price" in str(exc_info.value)
