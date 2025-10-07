import pytest
from ai_tradebot.kraken.kraken_service import KrakenService

def test_get_asset_pairs():
    ks = KrakenService()
    pairs = ks.get_asset_pairs()
    assert isinstance(pairs, dict)
    assert len(pairs) > 0

def test_get_ticker():
    ks = KrakenService()
    result = ks.get_ticker('XBTUSD')
    assert isinstance(result, dict)
    assert 'price' in result

def test_place_order_invalid():
    ks = KrakenService()
    # Verwacht een error bij ongeldige order
    response = ks.place_order('XBTUSD', 'buy', 0.00001)
    assert 'error' in response

def test_get_balances():
    ks = KrakenService()
    balances = ks.get_balances()
    assert isinstance(balances, dict)

def test_get_open_orders():
    ks = KrakenService()
    orders = ks.get_open_orders()
    assert isinstance(orders, dict)

def test_get_ohlc():
    ks = KrakenService()
    df = ks.get_ohlc('XBTUSD', interval=1, limit=5)
    assert df is None or hasattr(df, 'shape')
