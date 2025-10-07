# Deployment instructies

## Lokale installatie
1. Clone de repository: `git clone <repo-url>`
2. Installeer Python 3.12 en pip
3. Installeer dependencies: `pip install -r requirements.txt`
4. Start de bot: `python src/ai_tradebot/main.py`

## Productie deployment
1. Zorg voor een veilige opslag van API keys (env of secrets)
2. Gebruik de CI-pipeline voor automatische linting en testen
3. Deploy naar server of cloud (Docker, VM, etc.)
4. Monitor logs en alerts via logging-bestanden

## Secrets Management
- Gebruik een `.env` bestand voor lokale ontwikkeling. Zie `.env.example` voor een template.
- Voeg secrets toe aan GitHub Actions via Settings > Secrets and variables > Actions.
- Gebruik secrets in workflows met `${{ secrets.SECRET_NAME }}`.
- Zorg dat `.env` en gevoelige bestanden in `.gitignore` staan.
- Commit nooit echte secrets naar de repository.

## Monitoring
- Controleer regelmatig de logbestanden in de `logs/` map
- Gebruik externe monitoring voor uptime en errors

## CI/CD
- Elke push naar `main` triggert linting en tests via GitHub Actions
- Alleen bij een succesvolle run mag code gedeployed worden

_Voeg hier specifieke deployment- of monitoringstappen toe voor jouw omgeving._
