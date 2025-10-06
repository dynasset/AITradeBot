"""
Testscript: Plaatst een order op USDCUSD met minimaal volume en logt het volledige request/response.
"""
import logging
import krakenex
from src.config.kraken_config import KRAKEN_API_KEY, KRAKEN_API_SECRET

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_test_order.log"),
        logging.StreamHandler()
    ]
)

PAIR = 'USDCUSD'  # Probeer ook 'USDCZUSD' of 'XUSDCZUSD' indien nodig
VOLUME = 1.0      # Zo klein mogelijk, pas aan indien nodig
PRICE = 0.9998    # Huidige ask prijs, kan dynamisch opgehaald worden

k = krakenex.API()
k.key = KRAKEN_API_KEY
k.secret = KRAKEN_API_SECRET

order_data = {
    'pair': PAIR,
    'type': 'buy',
    'ordertype': 'limit',
    'volume': VOLUME,
    'price': PRICE
}

logging.info(f"Order request: {order_data}")
response = k.query_private('AddOrder', order_data)
logging.info(f"Order response: {response}")
print("Order response:", response)
