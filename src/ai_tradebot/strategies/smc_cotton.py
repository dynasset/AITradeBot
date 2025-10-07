"""
Strategieën: Smart Money Concepts (SMC) & Cotton Candy
- analyse_breaker_block_reversal
- analyse_liquidity_sweep_momentum
"""
import pandas as pd

def analyse_breaker_block_reversal(multi_df: dict, equity: float) -> dict:
    """
    SMC Breaker Block Reversal:
    Zoek naar breaker block, wacht op retest en reversal.
    """
    df = multi_df.get(15)
    if df is None or len(df) < 30:
        df = multi_df.get(5)
    if df is None or len(df) < 30:
        return {'kans': False}
    # Simpele breaker block: laatste swing low/high voor impuls
    swing_high = df['high'].rolling(window=5).max().iloc[-10]
    swing_low = df['low'].rolling(window=5).min().iloc[-10]
    impuls_up = df['close'].iloc[-10] > swing_high
    impuls_down = df['close'].iloc[-10] < swing_low
    # Retest breaker block
    recent_close = df['close'].iloc[-1]
    reversal = (impuls_up and recent_close < swing_high) or (impuls_down and recent_close > swing_low)
    if reversal:
        entry = recent_close
        stop = swing_low if impuls_up else swing_high
        risk = abs(entry - stop)
        if risk == 0:
            return {'kans': False}
        position_size = (equity * 0.02) / risk
        tp = entry + risk if impuls_up else entry - risk
        order = {
            'pair': None,
            'type': 'buy' if impuls_up else 'sell',
            'entry': entry,
            'stop': stop,
            'tp': tp,
            'volume': position_size
        }
        return {'kans': True, 'order': order}
    return {'kans': False}

def analyse_liquidity_sweep_momentum(multi_df: dict, equity: float) -> dict:
    """
    Cotton Candy Liquidity Sweep + Momentum:
    Zoek naar sweep van high/low gevolgd door momentum candle.
    """
    df = multi_df.get(5)
    if df is None or len(df) < 20:
        return {'kans': False}
    highs = df['high']
    lows = df['low']
    # Sweep: spike door high/low
    sweep_high = highs.iloc[-2] > highs.iloc[-5:-2].max()
    sweep_low = lows.iloc[-2] < lows.iloc[-5:-2].min()
    momentum_up = df['close'].iloc[-1] > highs.iloc[-2] and sweep_low
    momentum_down = df['close'].iloc[-1] < lows.iloc[-2] and sweep_high
    if momentum_up or momentum_down:
        entry = df['close'].iloc[-1]
        stop = lows.iloc[-2] if momentum_up else highs.iloc[-2]
        risk = abs(entry - stop)
        if risk == 0:
            return {'kans': False}
        position_size = (equity * 0.01) / risk
        tp = entry + risk if momentum_up else entry - risk
        order = {
            'pair': None,
            'type': 'buy' if momentum_up else 'sell',
            'entry': entry,
            'stop': stop,
            'tp': tp,
            'volume': position_size
        }
        return {'kans': True, 'order': order}
    return {'kans': False}
