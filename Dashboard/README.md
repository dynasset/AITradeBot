
# AITradeBot Dashboard

Dit dashboard biedt live monitoring en controle over alle services van de tradingbot.

## Functionaliteit

- **Status per service**: Zie direct of Kraken, Telegram en Strategy actief zijn.
- **Start/Stop knoppen**: Start of stop elke service individueel via het dashboard.
- **Error logging**: Bekijk recente errors uit alle logbestanden.

## Best practice workflow

- Elke service draait in een eigen proces via runner scripts (`run_kraken.py`, `run_telegram.py`, `run_strategy.py`).
- Status wordt bepaald op basis van actieve processen.
- Errors worden uit de logs per service getoond.
- Secrets en configuratie staan in `.env` (nooit in git).

## Gebruik

1. Start het dashboard:

   ```bash
   cd Dashboard
   /workspaces/AITradeBot/.venv/bin/python app.py
   ```

2. Open in je browser: [http://localhost:5000](http://localhost:5000) (of via Codespaces poort-forwarding).

3. Gebruik de knoppen om services te starten/stoppen en monitor errors.

## Teamverantwoordelijkheid

- Stephanie (Code Reviewer) ziet toe op naleving van deze best practices.
- Alle teamleden volgen deze workflow voor monitoring en beheer.

## Uitbreiding

- Koppel runner scripts aan echte service-logica.
- Voeg healthchecks, metrics en notificaties toe.
- Documenteer wijzigingen direct in deze README.
