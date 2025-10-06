import pytest
from ai_tradebot.kraken.kraken_service import KrakenService

@pytest.fixture
def kraken():
    return KrakenService()

def test_get_asset_pairs(kraken):
    pairs = kraken.get_asset_pairs()
    assert isinstance(pairs, dict)
    assert len(pairs) > 0

def test_get_balances(kraken):
    balances = kraken.get_balances()
    assert isinstance(balances, dict)

def test_get_open_orders(kraken):
    orders = kraken.get_open_orders()
    assert isinstance(orders, dict)

def test_get_ohlc(kraken):
    pairs = list(kraken.get_asset_pairs().keys())
    if pairs:
        df = kraken.get_ohlc(pairs[0], interval=1, limit=5)
        assert df is not None
        assert hasattr(df, 'to_dict')
