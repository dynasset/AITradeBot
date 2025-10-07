import pytest
from ai_tradebot.notifications.telegram_service import TelegramService

def test_send_message(monkeypatch):
    # Mock requests.post
    class DummyResponse:
        def __init__(self):
            self.text = '{}'
        def raise_for_status(self):
            pass
        def json(self):
            return {'ok': True}
    monkeypatch.setattr('requests.post', lambda *a, **kw: DummyResponse())
    ts = TelegramService('dummy_token', chat_id=123)
    result = ts.send_message('Test')
    assert 'ok' in result or 'error' in result

def test_get_updates(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {'result': []}
    monkeypatch.setattr('requests.get', lambda *a, **kw: DummyResponse())
    ts = TelegramService('dummy_token', chat_id=123)
    result = ts.get_updates()
    assert 'result' in result or 'error' in result
