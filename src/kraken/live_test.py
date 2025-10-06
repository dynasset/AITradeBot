"""
Live testscript voor minimale buy order op Kraken met stoploss en take profit.
Advies Product Owner: minimale hoeveelheid, veilig testen.
"""

import logging
from src.kraken.kraken_service import KrakenService

# Configureer logging voor het testscript
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_live_test.log"),
        logging.StreamHandler()
    ]
)

PAIR = 'XBTUSD'
ORDER_TYPE = 'buy'
VOLUME = 0.0001  # Minimale hoeveelheid

# Livedata ophalen
service = KrakenService()
ticker = service.get_ticker(PAIR)
current_price = ticker['price'] if ticker and 'price' in ticker else None

if current_price:
    stoploss = round(current_price * 0.98, 2)  # 2% onder huidige prijs
    take_profit = round(current_price * 1.02, 2)  # 2% boven huidige prijs
    logging.info(f"Plaats order: {ORDER_TYPE} {VOLUME} {PAIR} @ {current_price} SL: {stoploss} TP: {take_profit}")
    result = service.place_order(PAIR, ORDER_TYPE, VOLUME, price=current_price, stoploss=stoploss, take_profit=take_profit)
    logging.info(f"Order resultaat: {result}")
else:
    logging.error("Kan huidige prijs niet ophalen, test afgebroken.")
