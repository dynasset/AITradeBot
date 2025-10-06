"""
Plaatst een live buy order op Kraken met input van Remon (Product Owner).
"""
import logging
from src.kraken.kraken_service import KrakenService

PAIR = 'XBTUSD'
ORDER_TYPE = 'buy'
VOLUME = 0.0001
PRICE = 123287.6
STOPLOSS = 120821
TAKE_PROFIT = 125753

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_live_order.log"),
        logging.StreamHandler()
    ]
)

service = KrakenService()
logging.info(f"Plaats live order: {ORDER_TYPE} {VOLUME} {PAIR} @ {PRICE} SL: {STOPLOSS} TP: {TAKE_PROFIT}")
result = service.place_order(PAIR, ORDER_TYPE, VOLUME, price=PRICE, stoploss=STOPLOSS, take_profit=TAKE_PROFIT)
logging.info(f"Order resultaat: {result}")
print("Order resultaat:", result)
