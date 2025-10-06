# KrakenService

Veilige koppeling met de Kraken API voor AITradeBot.

## Installatie

1. Installeer dependencies:
   ```bash
   pip install python-dotenv requests
   ```
2. Maak een `.env` bestand aan in de root met:
   ```
   KRAKEN_API_KEY=your_api_key_here
   KRAKEN_API_SECRET=your_api_secret_here
   ```
3. Zorg dat `.env` in `.gitignore` staat.

## Gebruik

Importeer en initialiseer de service:
```python
from src.kraken.kraken_service import KrakenService
service = KrakenService()
```

### Methodes
- `get_ticker(pair: str) -> dict`: Haalt ticker info op voor een trading pair.
- `place_order(pair: str, order_type: str, volume: float, price: float = None) -> dict`: Plaatst een order.
- `get_account_info() -> dict`: Haalt accountinformatie op.

Alle functionaliteit werkt via parameters. Credentials worden alleen uit environment geladen.

## Veiligheid
- Credentials staan nooit in de broncode, alleen in `.env`.
- `.env` wordt niet gecommit.
- Constructor valideert op ontbrekende of lege credentials.

## Testen
- Unit tests staan in `src/tests/test_kraken_service.py`.
- Tests mocken environment variables en controleren methodesignatures en exception handling.
- Draai tests met:
  ```bash
  python3 -m unittest src/tests/test_kraken_service.py
  ```

## Doorontwikkeling
- Functionele code mag alleen veranderen bij expliciete doorontwikkeling.
- Runtime gedrag is volledig te sturen via configuratie en environment.
