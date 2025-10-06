# Configuratie voor het laden van environment variables
from dotenv import load_dotenv
import os

load_dotenv()

KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")
