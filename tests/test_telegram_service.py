import pytest
from ai_tradebot.notifications.telegram_service import TelegramService

def test_send_message():
    # Gebruik een dummy token en chat_id zodat er geen echte berichten worden verstuurd
    telegram = TelegramService(token='dummy', chat_id=123456)
    try:
        telegram.send_message('Testbericht')
    except Exception as e:
        # Verwacht een fout door dummy credentials, maar geen crash
        assert 'error' in str(e) or '401' in str(e) or 'invalid' in str(e)

def test_error_logging():
    telegram = TelegramService(token='dummy', chat_id=123456)
    try:
        telegram.log_error('Test error')
    except Exception as e:
        assert 'error' in str(e) or '401' in str(e) or 'invalid' in str(e)
