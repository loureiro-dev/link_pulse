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
    
    # Tabela de links com user_id
    c.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        source TEXT,
        found_at TEXT,
        user_id INTEGER NOT NULL,
        UNIQUE(url, user_id)
    )
    ''')
    
    # Tabela de páginas com user_id
    c.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        UNIQUE(url, user_id)
    )
    ''')
    
    # Adiciona coluna user_id na tabela links se não existir (migração)
    try:
        c.execute('ALTER TABLE links ADD COLUMN user_id INTEGER')
        # Migra dados existentes para user_id = 1 (admin padrão)
        c.execute('UPDATE links SET user_id = 1 WHERE user_id IS NULL')
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    conn.commit()
    conn.close()


def save_links(links: List[str], source: str = 'unknown', user_id: int = 1) -> None:
    """
    Save collected links to database
    
    Args:
        links: List of link URLs to save
        source: Source/campaign name for the links
        user_id: ID of the user who owns these links
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    for link in links:
        try:
            c.execute('INSERT OR IGNORE INTO links (url, source, found_at, user_id) VALUES (?, ?, ?, ?)', 
                     (link, source, now, user_id))
        except Exception:
            continue
    conn.commit()
    conn.close()


def list_links(limit: int = 100, user_id: int = None) -> List[Tuple[str, str, str]]:
    """
    List collected links from database
    
    Args:
        limit: Maximum number of links to return
        user_id: Filter links by user ID (if None, returns all)
        
    Returns:
        List of tuples (url, source, found_at)
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_id is not None:
        c.execute('SELECT url, source, found_at FROM links WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    else:
        c.execute('SELECT url, source, found_at FROM links ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


