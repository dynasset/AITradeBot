"""
Indicatoren voor scalper strategie: EMA, Bollinger Bands, RSI
"""
import numpy as np
import pandas as pd

def ema(series, period=100):
    return series.ewm(span=period, adjust=False).mean()

def bollinger_bands(series, period=20, stddev=2):
    ma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = ma + stddev * std
    lower = ma - stddev * std
    return upper, lower

def rsi(series, period=4):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
