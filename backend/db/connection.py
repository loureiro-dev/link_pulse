"""
Database connection and operations
Handles SQLite database for storing collected links
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Tuple

# Database path: backend/data/whatsapp_links.db
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BACKEND_ROOT, "backend", "data")
DB_PATH = os.path.join(DATA_DIR, "whatsapp_links.db")


def init_db():
    """Initialize database and create tables if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
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


def save_links(links: List[str], source: str = 'unknown') -> None:
    """
    Save collected links to database
    
    Args:
        links: List of link URLs to save
        source: Source/campaign name for the links
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for link in links:
        try:
            c.execute('INSERT OR IGNORE INTO links (url, source, found_at) VALUES (?, ?, ?)', 
                     (link, source, now))
        except Exception:
            continue
    conn.commit()
    conn.close()


def list_links(limit: int = 100) -> List[Tuple[str, str, str]]:
    """
    List collected links from database
    
    Args:
        limit: Maximum number of links to return
        
    Returns:
        List of tuples (url, source, found_at)
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT url, source, found_at FROM links ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


