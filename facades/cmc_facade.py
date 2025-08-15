import requests  # type: ignore
import os
import json
import logging
from dotenv import load_dotenv  # change this to pull in API key from Const file

load_dotenv()


def get_btc_price():
    # Fetches current BTC price from CoinMarketCap API
    # Returns: float price in USD
    # Raises: CMCApiError and its subclasses

    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

    parameters = {"symbol": "BTC"}

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv("CMC_API_KEY"),
    }

    if not os.getenv("CMC_API_KEY"):
        raise CMCApiError("CMC API Key not found in environment variables")

    try:
        response = requests.get(url, params=parameters, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()

        # Validate response structure
        if "data" not in data or "BTC" not in data["data"]:
            raise CMCResponseError("Invalid API response structure")

        if not data["data"]["BTC"]:
            raise CMCResponseError("No BTC data found in response")

        price = response.json()["data"]["BTC"][0]["quote"]["USD"]["price"]

        if not isinstance(price, (int, float)):
            raise CMCResponseError("Invalid price format received")

        return float(price)

    except requests.exceptions.Timeout:
        logging.error("Timeout error occurred while connecting to CMC API")
        raise CMCConnectionError("Failed to connect to CMC API")

    except requests.exceptions.ConnectionError:
        logging.error("Failed to connect to CMC API")
        raise CMCConnectionError("Failed to establish connection to CMC API")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to CMC API failed: {str(e)}")
        raise CMCConnectionError(f"Request failed: {str(e)}")

    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"Error parsing CMC API response: {str(e)}")
        raise CMCResponseError(f"Failed to parse API response: {str(e)}")

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON response from CMC API: {str(e)}")
        raise CMCResponseError("Invalid JSON response from API")


class CMCApiError(Exception):
    """Base exception for CMC API related errors"""

    pass


class CMCConnectionError(CMCApiError):
    """Exception for network/connection related errors"""

    pass


class CMCResponseError(CMCApiError):
    """Exception for invalid API responses"""

    pass
