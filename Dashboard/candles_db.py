import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'candles.sqlite3')

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS candles (
        pair TEXT,
        interval INTEGER,
        time INTEGER,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        vwap REAL,
        volume REAL,
        count INTEGER,
        PRIMARY KEY (pair, interval, time)
    )''')
    conn.commit()
    conn.close()

def insert_candles(pair, interval, candles):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    for candle in candles:
        c.execute('''INSERT OR REPLACE INTO candles VALUES (?,?,?,?,?,?,?,?,?,?)''', (
            pair, interval, candle['time'], candle['open'], candle['high'], candle['low'], candle['close'], candle['vwap'], candle['volume'], candle['count']
        ))
    conn.commit()
    conn.close()

def get_candles(pair, interval, limit=100):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''SELECT time, open, high, low, close, vwap, volume, count FROM candles WHERE pair=? AND interval=? ORDER BY time DESC LIMIT ?''', (pair, interval, limit))
    rows = c.fetchall()
    conn.close()
    # Reverse for chart (oldest first)
    rows = rows[::-1]
    result = {k: [] for k in ['time','open','high','low','close','vwap','volume','count']}
    for row in rows:
        for i, k in enumerate(result):
            result[k].append(row[i])
    return result

def clear_db():
    path = get_db_path()
    if os.path.exists(path):
        os.remove(path)
