# Strategie Documentatie

Dit document beschrijft alle tradingstrategieën die in de AITradeBot zijn geïmplementeerd. Per strategie wordt de rationale, parameters en beslisregels uitgelegd.

---

## Template voor strategie-documentatie


### Strategie: [Naam van de strategie]

**Beschrijving:**

- Korte uitleg van de strategie en het doel.

**Rationale:**

- Waarom is deze strategie gekozen?
- Welke marktcondities zijn relevant?

**Parameters:**

- Overzicht van alle variabelen en instellingen (met uitleg).

**Beslisregels:**

- Uitleg van de logica en voorwaarden voor het plaatsen van trades.

**Voorbeeld:**

- (Optioneel) Voorbeeld van een trade of scenario.

---

## Strategieën


### Strategie: Scalper

**Beschrijving:**

- Mechanische strategie gericht op snelle, kleine winsten met dynamische exits en money management.

**Rationale:**

- Geschikt voor markten met veel volatiliteit en korte trends.

**Parameters:**

- `risk_pct`: Percentage van het kapitaal dat per trade wordt ingezet.
- `entry`, `stop`, `tp`: Entryprijs, stoploss en take-profit niveau’s.

**Beslisregels:**

- Koop als prijs boven EMA en onder RSI-drempel.
- Verkoop als prijs onder EMA en boven RSI-drempel.

**Voorbeeld:**

- Zie code in `src/ai_tradebot/strategies/scalper.py`.

---

_Voeg hier nieuwe strategieën toe volgens het template._
