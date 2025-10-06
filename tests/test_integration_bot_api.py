import pytest
from Dashboard.app import app

def test_bot_api_workflow():
    client = app.test_client()
    # Start bot
    resp = client.post('/api/start_bot')
    assert resp.status_code == 200
    assert 'status' in resp.json
    # Check bot data
    resp = client.get('/api/bot_data')
    assert resp.status_code == 200
    assert 'balances' in resp.json
    assert 'pairs' in resp.json
    assert 'orders' in resp.json
    assert 'candles' in resp.json
    assert 'analysis' in resp.json
    # Stop bot
    resp = client.post('/api/stop_bot')
    assert resp.status_code == 200
    assert 'status' in resp.json
