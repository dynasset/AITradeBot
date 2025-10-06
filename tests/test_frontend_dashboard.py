import requests
from bs4 import BeautifulSoup

def test_dashboard_loads():
    # Zorg dat de Flask-app lokaal draait op poort 5000
    resp = requests.get('http://localhost:5000/')
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Check op bot-control knoppen
    start_btn = soup.find(id='startBotBtn')
    stop_btn = soup.find(id='stopBotBtn')
    assert start_btn is not None
    assert stop_btn is not None
    # Check op live bot data box
    bot_data_box = soup.find(class_='bot-data-box')
    assert bot_data_box is not None
