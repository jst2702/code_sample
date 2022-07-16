from TinyTitans.src.backtesting.polygon_api.polygon_api_credentials import api_key
import requests
from datetime import datetime


def get_last_close(ticker: str) -> float:
    """ Get the last minute close

    Args:
        ticker (str): ticker

    Returns:
        Dict[str, float]: A dictionary with the last bid and ask prices of the ticker.
    """
    date = str(datetime.today().date())
    endpoint = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{date}/{date}?adjusted=false&sort=asc&limit=1&apiKey={api_key}'
    response = requests.get(endpoint)
    assert response.status_code == 200
    return response.json()['results'][0]['c']
