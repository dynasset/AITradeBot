# Interface Inventarisatie – 7 oktober 2025

Dit document bevat een overzicht van alle publieke functies en klassen in de AITradeBot codebase die nog geen type hints of interfacebeschrijving hebben.

## Overzicht per module

| Bestand | Functie/Klasse | Type hints | Interfacebeschrijving | Laatste wijziging |
|---------|----------------|------------|----------------------|-------------------|
| src/ai_tradebot/notifications/telegram/order_proposal.py | render_order_proposal | Nee | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/notifications/telegram_service.py | TelegramService | Gedeeltelijk | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/kraken/kraken_service.py | KrakenService | Gedeeltelijk | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/main.py | start_bot, stop_bot, approve_order, reject_order, analyse_and_push_opportunity | Nee | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/strategies/strategy_workflow.py | load_strategies, fetch_kraken_ohlc_multi, main | Nee | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/strategies/indicators.py | ema, bollinger_bands, rsi | Nee | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/strategies/scalper.py | analyse_remon, analyse_scalper | Gedeeltelijk | Nee | 2025-10-07 10:16 |
| src/ai_tradebot/strategies/smc_cotton.py | analyse_breaker_block_reversal, analyse_liquidity_sweep_momentum | Nee | Nee | 2025-10-07 10:16 |

_Voeg hier nieuwe modules/functies toe als ze gevonden worden._
