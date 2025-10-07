import pytest
from ai_tradebot.strategies.scalper import analyse_remon, analyse_scalper
from ai_tradebot.strategies.smc_cotton import analyse_breaker_block_reversal, analyse_liquidity_sweep_momentum
from ai_tradebot.strategies.strategy_workflow import load_strategies, fetch_kraken_ohlc_multi

def test_analyse_remon():
    result = analyse_remon('XBTUSD', 100)
    assert isinstance(result, dict) or result is None

def test_analyse_scalper():
    multi_df = {1: None, 3: None, 5: None, 15: None, 60: None}
    result = analyse_scalper(multi_df, 100)
    assert isinstance(result, dict)

def test_analyse_breaker_block_reversal():
    multi_df = {1: None, 3: None, 5: None, 15: None, 60: None}
    result = analyse_breaker_block_reversal(multi_df, 100)
    assert isinstance(result, dict)

def test_analyse_liquidity_sweep_momentum():
    multi_df = {1: None, 3: None, 5: None, 15: None, 60: None}
    result = analyse_liquidity_sweep_momentum(multi_df, 100)
    assert isinstance(result, dict)

def test_load_strategies():
    strategies = load_strategies()
    assert isinstance(strategies, list)

def test_fetch_kraken_ohlc_multi():
    dfs = fetch_kraken_ohlc_multi('XBTUSD')
    assert isinstance(dfs, dict)
