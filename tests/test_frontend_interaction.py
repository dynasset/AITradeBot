import requests
from bs4 import BeautifulSoup

def test_dashboard_interaction():
    resp = requests.get('http://localhost:5000/')
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Start/Stop knoppen
    start_btn = soup.find(id='startBotBtn')
    stop_btn = soup.find(id='stopBotBtn')
    assert start_btn is not None
    assert stop_btn is not None
    # Status-indicator
    status_text = soup.find(id='botStatusText')
    assert status_text is not None
    # AJAX-data box
    bot_data_box = soup.find(class_='bot-data-box')
    assert bot_data_box is not None
