import pytest
from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi

def test_load_strategies():
    strategies = load_strategies()
    assert isinstance(strategies, list)
    assert all(callable(s) for s in strategies)

def test_strategy_on_dummy_data():
    # Simuleer een multi-timeframe OHLC dict
    dummy_df = {1: None, 5: None, 15: None, 60: None}
    strategies = load_strategies()
    for strategy in strategies:
        try:
            res = strategy(dummy_df, 10000)
            assert isinstance(res, dict) or res is None
        except Exception as e:
            assert False, f"Strategie {strategy.__name__} faalt: {e}"
