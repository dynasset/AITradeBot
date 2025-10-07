import pytest
from ai_tradebot.strategies.indicators import ema, bollinger_bands, rsi
import pandas as pd

def test_ema():
    s = pd.Series([1, 2, 3, 4, 5])
    result = ema(s, period=3)
    assert hasattr(result, 'iloc')

def test_bollinger_bands():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    upper, lower = bollinger_bands(s, period=3)
    assert hasattr(upper, 'iloc') and hasattr(lower, 'iloc')

def test_rsi():
    s = pd.Series([1, 2, 3, 2, 1, 2, 3, 4, 5])
    result = rsi(s, period=3)
    assert hasattr(result, 'iloc')
