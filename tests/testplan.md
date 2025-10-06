
# Testplan AITradeBot

Dit document beschrijft de teststrategie en de benodigde testcases voor een robuust, veilig en schaalbaar AITradeBot project.

## 1. Unit tests

- **KrakenService**: Test alle methodes (get_balances, get_asset_pairs, get_ohlc, get_open_orders, place_order) met mock-data.

- **TelegramService**: Test versturen van berichten en error logging.

- **Strategieën**: Test analyse-functies met dummy data.

## 2. Integratietests

- Test samenwerking tussen services (strategie → order → Telegram).

- Test bot-scheduler: periodiek ophalen en verwerken van data.

## 3. API-endpoint tests

- Test alle Flask-routes, inclusief error-afhandeling en edge cases (bot al actief, geen data beschikbaar).

## 4. Frontend tests

- Test of dashboard correct data ophaalt en weergeeft (bijv. met Selenium/Playwright).

- Test interactie met knoppen (Start/Stop Bot) en visuele feedback.

## 5. End-to-end tests

- Simuleer volledige workflow: bot starten, data ophalen, strategie uitvoeren, order plaatsen, feedback tonen.

## 6. Security & permission tests

- Test of gevoelige data (API keys, .env) niet uitlekt via logs of endpoints.

- Test rate limiting en foutafhandeling bij API-calls.

## 7. Performance tests

- Test snelheid en stabiliteit van dashboard en backend bij veel data of meerdere gebruikers.

## 8. Automatisering

- Alle tests worden automatisch uitgevoerd via pytest en CI/CD (bijv. GitHub Actions).

- Smoke test: importeer alle modules en controleer op importfouten.

- Integration test: start dashboard en controleer op errors.

## Uitbreiding

- Testcases worden per feature en bugfix aangevuld.

- Testresultaten worden vastgelegd en besproken in het team.
