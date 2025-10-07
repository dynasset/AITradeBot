"""
Strategy Workflow: dynamisch toepassen van alle strategieën op beschikbare Kraken pairs
"""

import importlib
from ai_tradebot.kraken.kraken_service import KrakenService
import pandas as pd

STRATEGY_MODULES = [
    "ai_tradebot.strategies.scalper",
]


def load_strategies():
    strategies = []
    for mod_name in STRATEGY_MODULES:
        mod = importlib.import_module(mod_name)
        for attr in dir(mod):
            if attr.startswith("analyse_"):
                strategies.append(getattr(mod, attr))
    return strategies


def fetch_kraken_ohlc_multi(pair, intervals=[1, 3, 5, 15, 60], limit=100):
    ks = KrakenService()
    dfs = {}
    for interval in intervals:
        df = ks.get_ohlc(pair, interval=interval, limit=limit)
        if df is not None:
            dfs[interval] = df
    return dfs


def main():
    from ai_tradebot.notifications.telegram_service import TelegramService

    TELEGRAM_TOKEN = "7685158113:AAGg4eCV-mLj90MuRKVudL7f3hN7OnM0SNo"
    TELEGRAM_CHAT_ID = 1577940521
    telegram = TelegramService(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

    ks = KrakenService()
    equity = float(ks.get_balances().get("USD", 10000))
    asset_pairs = ks.get_asset_pairs()
    strategies = load_strategies()
    results = {}
    intervals = [1, 3, 5, 15, 60]
    for pair in list(asset_pairs.keys())[:10]:
        multi_df = fetch_kraken_ohlc_multi(pair, intervals=intervals, limit=100)
        if not multi_df or not any(len(df) >= 20 for df in multi_df.values()):
            continue
        for strategy in strategies:
            res = strategy(multi_df, equity)
            if res and res.get("kans"):
                order_data = res.get("order")
                proposal_id = (
                    f"{pair}_{strategy.__name__}_{int(pd.Timestamp.now().timestamp())}"
                )
                msg = f"Order voorstel:\nPair: {pair}\nStrategie: {strategy.__name__}\nType: {order_data.get('type')}\nEntry: {order_data.get('entry')}\nStop: {order_data.get('stop')}\nTP: {order_data.get('tp')}\nVolume: {order_data.get('volume')}\nAntwoord met '{proposal_id} ja' of '{proposal_id} nee' om te bevestigen."
                telegram.send_message(msg)
                print(f"Telegram voorstel verstuurd: {msg}")
                approved = telegram.await_approval(proposal_id)
                if approved:
                    confirmation = ks.place_order(
                        pair=pair,
                        order_type=order_data.get("type"),
                        volume=order_data.get("volume"),
                        price=order_data.get("entry"),
                        stoploss=order_data.get("stop"),
                        take_profit=order_data.get("tp"),
                    )
                    telegram.send_message(f"Order geplaatst: {confirmation}")
                    print(f"Order geplaatst: {confirmation}")
                else:
                    telegram.send_message(
                        f"Order NIET geplaatst voor {pair} ({strategy.__name__})"
                    )
                    print(f"Order NIET geplaatst voor {pair} ({strategy.__name__})")
                results[(pair, strategy.__name__)] = res
            elif res and res.get("voorspelling"):
                print(
                    f"Voorspelling op {pair} ({strategy.__name__}): kans mogelijk binnen {res['voorspelling']['minuten']} minuten."
                )
            else:
                print(f"Geen kans op {pair} ({strategy.__name__}).")
    if not results:
        print("Geen kansen gevonden.")


if __name__ == "__main__":
    main()
