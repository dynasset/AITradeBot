"""
Healthcheck voor KrakenService: controleert verbinding en API-status.
Logt resultaten in centrale logging.
"""
import logging
from src.kraken.kraken_service import KrakenService

def healthcheck():
    service = KrakenService()
    result = service.get_ticker('XBTUSD')
    if result and result.get('price'):
        logging.info(f"Healthcheck OK: Kraken API bereikbaar, prijs XBTUSD = {result['price']}")
        return True
    else:
        logging.error("Healthcheck FAIL: Kraken API niet bereikbaar of geen prijsdata.")
        return False

if __name__ == "__main__":
    healthcheck()
