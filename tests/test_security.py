import requests

def test_no_secrets_in_api():
    # Controleer dat API keys en .env niet uitlekken via endpoints
    resp = requests.get('http://localhost:5000/api/bot_data')
    assert resp.status_code == 200
    forbidden = ['KRAKEN_API_KEY', 'KRAKEN_API_SECRET', 'TELEGRAM_TOKEN']
    for key in forbidden:
        assert key not in resp.text
