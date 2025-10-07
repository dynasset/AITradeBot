# Actieplan: Live Daytraden met AITradeBot

## 1. API keys en live credentials
- Controleer of geldige Kraken API keys en secrets aanwezig zijn in `.env`
- Zet test/live API keys apart en documenteer het verschil
- Test verbinding met Kraken live endpoint

## 2. Live trading flow activeren
- Controleer of de bot in live modus kan draaien (geen testmode)
- Zet een duidelijke switch in de configuratie voor live/test
- Voer een dry-run uit met kleine bedragen

## 3. Monitoring en logging
- Zorg dat alle live trades worden gelogd (orders, balances, errors)
- Activeer alerts bij grote verliezen, errors of ongebruikelijke activiteit
- Monitor via Prometheus/Grafana en Telegram notificaties

## 4. Risicobeheer en limieten
- Stel limieten in voor maximale trade size, daily loss, exposure
- Implementeer een stop-loss en noodstop
- Documenteer risicoparameters in README en config

## 5. Deployment en uptime
- Zorg dat de bot 24/7 kan draaien (server, cloud, Docker)
- Implementeer automatische herstart bij crash
- Test failover en recovery

## 6. Validatie en test
- Voer een end-to-end test uit met een kleine live trade
- Controleer of alle logging, monitoring en limieten werken
- Review alle code en settings voor livegang

## 7. Go-live
- Communiceer livegang naar het team
- Monitor eerste trades actief
- Evalueer en optimaliseer na de eerste dag

Team: Product Owner, Architect, Developers, DevOps, QA
Datum: 2025-10-07
