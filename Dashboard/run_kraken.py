from ai_tradebot.kraken.kraken_service import KrakenService

def main():
    # Hier kun je eventueel een healthcheck of een loop toevoegen
    print("KrakenService gestart.")
    # Dummy: alleen initialisatie
    service = KrakenService(api_key="", api_secret="")
    # Voeg hier echte logica toe

if __name__ == "__main__":
    main()
