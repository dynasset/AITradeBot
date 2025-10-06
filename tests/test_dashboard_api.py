import pytest
from Dashboard.app import app

def test_home_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

def test_start_bot_route():
    client = app.test_client()
    response = client.post('/api/start_bot')
    assert response.status_code == 200
    assert 'status' in response.json

def test_stop_bot_route():
    client = app.test_client()
    response = client.post('/api/stop_bot')
    assert response.status_code == 200
    assert 'status' in response.json

def test_bot_data_route():
    client = app.test_client()
    response = client.get('/api/bot_data')
    assert response.status_code == 200
    assert 'balances' in response.json
    assert 'pairs' in response.json
    assert 'orders' in response.json
    assert 'candles' in response.json
    assert 'analysis' in response.json
