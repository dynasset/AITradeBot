# Teststrategie

## Nieuwe unit/integration tests
- Schrijf tests voor alle kritieke modules: kraken_service, telegram_service, main, strategies, indicators
- Gebruik pytest
- Zorg voor edge cases en foutafhandeling

## Regressietests
- Automatiseer regressietests in CI pipeline
- Voeg een testmatrix toe voor verschillende scenario's

## Performance tests
- Voeg pytest-benchmark of custom performance tests toe
- Meet responstijd van API endpoints en tradingroutines

## Status
- Testbestanden zijn aangemaakt en geautomatiseerd
- Testuitvoering is onderdeel van CI/CD
