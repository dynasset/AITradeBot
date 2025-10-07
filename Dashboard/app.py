import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import threading
import time
from threading import Thread, Event
from flask import Flask, render_template, redirect, url_for, request, jsonify
from Dashboard.candles_db import init_db, insert_candles, get_candles, clear_db
from ai_tradebot.kraken.kraken_service import KrakenService
app = Flask(__name__)
bot_active = Event()
bot_data = {
    'balances': {},
    'pairs': [],
    'candles': {},
    'orders': {},
    'analysis': {},
    'status': 'inactive'
}

def bot_scheduler():
    ks = KrakenService()
    from ai_tradebot.strategies.strategy_workflow import load_strategies
    strategies = load_strategies()
    while bot_active.is_set():
        try:
            bot_data['balances'] = ks.get_balances()
            bot_data['pairs'] = list(ks.get_asset_pairs().keys())
            # Candles ophalen voor eerste 3 pairs als voorbeeld
            bot_data['candles'] = {pair: ks.get_ohlc(pair, interval=1, limit=20).to_dict() if ks.get_ohlc(pair, interval=1, limit=20) is not None else {} for pair in bot_data['pairs'][:3]}
            bot_data['orders'] = ks.get_open_orders()
            # Strategie-analyse uitvoeren
            analysis_results = {}
            for pair in bot_data['pairs'][:3]:
                multi_df = {1: ks.get_ohlc(pair, interval=1, limit=20)}
                for strategy in strategies:
                    if multi_df[1] is not None:
                        res = strategy(multi_df, 10000) # Dummy equity
                        analysis_results[pair] = res
            bot_data['analysis'] = analysis_results
            bot_data['status'] = 'active'
        except Exception as e:
            bot_data['status'] = f'error: {e}'
        time.sleep(60)

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    if bot_active.is_set():
        return {'status': bot_data['status'], 'message': 'Bot draait al.'}
    bot_active.set()
    Thread(target=bot_scheduler, daemon=True).start()
    bot_data['status'] = 'starting'
    return {'status': bot_data['status'], 'message': 'Bot wordt gestart.'}

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    if not bot_active.is_set():
        return {'status': bot_data['status'], 'message': 'Bot is al gestopt.'}
    bot_active.clear()
    bot_data['status'] = 'inactive'
    return {'status': bot_data['status'], 'message': 'Bot is gestopt.'}

@app.route('/api/bot_data', methods=['GET'])
def get_bot_data():
    return jsonify(bot_data)
## VERWIJDERD: dubbele initialisatie en imports

# Dummy service states (replace with real checks)
service_scripts = {
    'Kraken': 'run_kraken.py',
    'Telegram': 'run_telegram.py',
    'Strategy': 'run_strategy.py'
}

# Track running processes by service name
service_processes = {}

# Shared state
shared_state = {
    'balances': {},
    'available_pairs': [],
    'candles': {}, # candles[(pair, interval)] = df
}

kraken_service = KrakenService()

# Periodic balance and pairs update (every hour)
def update_balances_and_pairs():
    while True:
        try:
            balances = kraken_service.get_balances()
            shared_state['balances'] = balances
            pairs = kraken_service.get_asset_pairs()
            # Filter pairs obv balans (eenvoudig: alle pairs waar je asset > 0)
            available = []
            for pair in pairs:
                base = pair[:-4] if len(pair) > 4 else pair
                quote = pair[-4:] if len(pair) > 4 else pair
                if base in balances and float(balances[base]) > 0:
                    available.append(pair)
                elif quote in balances and float(balances[quote]) > 0:
                    available.append(pair)
            shared_state['available_pairs'] = available
        except Exception as e:
            pass
        time.sleep(3600)

# Periodic candles update (every minute)
def update_candles():
    while True:
        try:
            for pair in shared_state['available_pairs']:
                for interval in [1, 5, 15, 60]:
                    df = kraken_service.get_ohlc(pair, interval=interval, limit=100)
                    if df is not None:
                        candles = df.to_dict('records')
                        from .candles_db import insert_candles
                        insert_candles(pair, interval, candles)
                    from .candles_db import get_candles
                    shared_state['candles'][(pair, interval)] = get_candles(pair, interval)
        except Exception as e:
            pass
        time.sleep(60)

# Start background threads
threading.Thread(target=update_balances_and_pairs, daemon=True).start()
threading.Thread(target=update_candles, daemon=True).start()
from flask import jsonify

# API endpoint: actuele balans
@app.route('/api/balances')
def api_balances():
    return jsonify(shared_state['balances'])

# API endpoint: beschikbare pairs
@app.route('/api/pairs')
def api_pairs():
    return jsonify(shared_state['available_pairs'])

# API endpoint: candles per pair/timeframe
@app.route('/api/candles')
def api_candles():
    pair = request.args.get('pair')
    interval = int(request.args.get('interval', 1))
    from .candles_db import get_candles
    candles = get_candles(pair, interval)
    return jsonify(candles)

# Dummy error log (replace with real log reading)
def get_errors():
    errors = []
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        return errors
    for log_file in os.listdir(logs_dir):
        if log_file.endswith('.log'):
            with open(os.path.join(logs_dir, log_file), 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    if 'ERROR' in line:
                        errors.append((log_file, line.strip()))
    return errors

@app.route('/')
def dashboard():
    errors = get_errors()
    states = {}
    for name in service_scripts:
        states[name] = name in service_processes and service_processes[name].poll() is None
    return render_template('dashboard.html', service_states=states, errors=errors)

@app.route('/start/<service>')
def start_service(service):
    if service in service_scripts and service not in service_processes:
        script_path = os.path.join(os.path.dirname(__file__), service_scripts[service])
        proc = subprocess.Popen(['python3', script_path])
        service_processes[service] = proc
    return redirect(url_for('dashboard'))

@app.route('/stop/<service>')
def stop_service(service):
    if service in service_processes:
        proc = service_processes[service]
        proc.terminate()
        proc.wait(timeout=5)
        del service_processes[service]
        # Ruim candles DB op bij stop/herstart
        clear_db()
        init_db()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
