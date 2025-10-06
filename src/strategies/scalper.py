"""
Strategie: Remon
Beschrijving: Voorbeeld van een analysefunctie die gebruikt wordt door de trading bot.
Deze functie bepaalt op basis van marktdata en balans of er een order geplaatst moet worden.
"""

def analyse_remon(pair: str, balance: float) -> dict:
    # Voorbeeld: dummy strategie
    # Plaats een buy order als er voldoende balans is, anders geen order
    if balance > 0:
        return {
            'type': 'buy',
            'sl': None,  # Vul hier je stoploss logica in
            'tp': None   # Vul hier je take profit logica in
        }
    return None

"""
Scalper Strategie: Mechanisch, high-winrate, dynamische exits & money management
"""
import pandas as pd
from ai_tradebot.strategies.indicators import ema, bollinger_bands, rsi


def analyse_scalper(multi_df: dict, equity: float) -> dict:
    """
    Multi-timeframe scalper: trendfilter op 1h/15m, entry trigger op 5m/3m/1m
    multi_df: dict {interval: df}
    """
    # Trendfilter: EMA100 op 1h en 15m
    df_1h = multi_df.get(60)
    df_15m = multi_df.get(15)
    df_5m = multi_df.get(5)
    df_3m = multi_df.get(3)
    df_1m = multi_df.get(1)
    if df_1h is None or df_15m is None or df_5m is None:
        return {'kans': False}
    price_5m = df_5m['close'].iloc[-1]
    ema_100_1h = ema(df_1h['close'], 100).iloc[-1]
    ema_100_15m = ema(df_15m['close'], 100).iloc[-1]
    trend_up = price_5m > ema_100_1h and price_5m > ema_100_15m
    trend_down = price_5m < ema_100_1h and price_5m < ema_100_15m
    # Entry trigger: BB/RSI op 5m, 3m, 1m
    for tf, df in [(5, df_5m), (3, df_3m), (1, df_1m)]:
        if df is None or len(df) < 20:
            continue
        upper_bb, lower_bb = bollinger_bands(df['close'], 20, 2)
        upper_bb = upper_bb.iloc[-1]
        lower_bb = lower_bb.iloc[-1]
        rsi_val = rsi(df['close'], 4).iloc[-1]
        price = df['close'].iloc[-1]
        risk_pct = 0.03
        # Long
        if trend_up and price <= lower_bb and rsi_val < 20:
            entry = price
            stop = min(df['low'].iloc[-5:].min(), lower_bb)
            risk = entry - stop
            if risk <= 0:
                continue
            position_size = (equity * risk_pct) / risk
            tp1 = entry + risk
            order = {
                'pair': None,  # wordt ingevuld door workflow
                'type': 'buy',
                'entry': entry,
                'stop': stop,
                'tp': tp1,
                'volume': position_size
            }
            return {'kans': True, 'order': order}
        # Short
        if trend_down and price >= upper_bb and rsi_val > 80:
            entry = price
            stop = max(df['high'].iloc[-5:].max(), upper_bb)
            risk = stop - entry
            if risk <= 0:
                continue
            position_size = (equity * risk_pct) / risk
            tp1 = entry - risk
            order = {
                'pair': None,
                'type': 'sell',
                'entry': entry,
                'stop': stop,
                'tp': tp1,
                'volume': position_size
            }
            return {'kans': True, 'order': order}
    # Voorspelling: als trendfilter klopt maar entry trigger nog niet, geef tijd tot kans
    if trend_up or trend_down:
        return {'kans': False, 'voorspelling': {'minuten': 5}}
    return {'kans': False}
