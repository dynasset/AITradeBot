"""
Live Kraken workflow: scalper strategie op alle dynamisch beschikbare pairs
"""
import pandas as pd
from src.strategies.scalper import analyse_scalper
from src.kraken.kraken_service import KrakenService

def fetch_kraken_ohlc(pair, interval=1, limit=100):
    url = "https://api.kraken.com/0/public/OHLC"
    params = {"pair": pair, "interval": interval}
    import requests
    resp = requests.get(url, params=params)
    data = resp.json()
    result = data.get("result", {})
    ohlc = None
    for k in result:
        if k != "last":
            ohlc = result[k]
            break
    if not ohlc:
        return None
    df = pd.DataFrame(ohlc, columns=["time","open","high","low","close","vwap","volume","count"])
    df = df.tail(limit)
    df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)
    return df

def main():
    ks = KrakenService()
    equity = float(ks.get_balances().get("USD", 10000))
    asset_pairs = ks.get_asset_pairs()
    results = {}
    for pair in asset_pairs.keys():
        df = fetch_kraken_ohlc(pair)
        if df is None or len(df) < 20:
            continue
        signal = analyse_scalper(df, equity)
        if signal:
            print(f"Trade signaal voor {pair}: {signal}")
            results[pair] = signal
    if not results:
        print("Geen trade signalen gevonden.")

if __name__ == "__main__":
    main()
