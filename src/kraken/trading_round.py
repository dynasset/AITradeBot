"""
Voert een dynamische tradingronde uit op basis van actuele balances en analyse van Remon.
"""
import logging
from src.kraken.kraken_service import KrakenService

def remon_analyse(pair, balance):
    # Simpele analyse: koop als er saldo is, met SL/TP op 2% afstand
    service = KrakenService()
    ticker = service.get_ticker(pair)
    price = ticker['price'] if ticker and 'price' in ticker else None
    if price:
        return {
            'type': 'buy',
            'sl': round(price * 0.98, 2),
            'tp': round(price * 1.02, 2)
        }
    return None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_trading_round.log"),
        logging.StreamHandler()
    ]
)

service = KrakenService()
results = service.dynamic_trade(remon_analyse)
logging.info(f"Tradingronde resultaten: {results}")
print("Tradingronde resultaten:", results)
