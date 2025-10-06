import requests
import time

def test_dashboard_performance():
    start = time.time()
    resp = requests.get('http://localhost:5000/')
    duration = time.time() - start
    assert resp.status_code == 200
    # Dashboard moet binnen 2 seconden laden
    assert duration < 2
