import requests
import locale
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_btc_price():
  url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

  parameters = {
    'symbol': 'BTC'
  }

  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY')
  }
  try: 
    response = requests.get(url, params=parameters, headers=headers)
    response.raise_for_status() # Raise an HTTPError for bad responses
    price = response.json()['data']['BTC'][0]['quote']['USD']['price']
    return price
  except requests.exceptions.RequestException as e:
    raise Exception("Failed to fetch BTC price") from e