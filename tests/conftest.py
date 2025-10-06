
import sys
import os
import threading
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
def run_flask():
	from Dashboard.app import app
	app.run(port=5000)

@pytest.fixture(scope='session', autouse=True)
def flask_server():
	t = threading.Thread(target=run_flask, daemon=True)
	t.start()
	time.sleep(2)  # Geef server tijd om op te starten
	yield
	# Server wordt automatisch gestopt bij einde sessie (daemon)
