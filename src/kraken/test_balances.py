import logging
import krakenex
from src.config.kraken_config import KRAKEN_API_KEY, KRAKEN_API_SECRET

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("kraken_test_balances.log"),
        logging.StreamHandler()
    ]
)

k = krakenex.API()
k.key = KRAKEN_API_KEY
k.secret = KRAKEN_API_SECRET

logging.info("Ophalen van ruwe balances via Kraken API...")
response = k.query_private('Balance')
logging.info(f"Ruwe balances response: {response}")
print("Ruwe balances response:", response)
