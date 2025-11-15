
import sqlite3, os
from datetime import datetime

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data')
DB_PATH = os.path.join(BASE, 'whatsapp_links.db')

def init_db():
    os.makedirs(BASE, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        source TEXT,
        found_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_links(links, source='unknown'):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for link in links:
        try:
            c.execute('INSERT OR IGNORE INTO links (url, source, found_at) VALUES (?, ?, ?)', (link, source, now))
        except Exception:
            continue
    conn.commit()
    conn.close()

def list_links(limit=100):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT url, source, found_at FROM links ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
