"""
Database operations for pages
Handles user-specific pages storage
"""

import sqlite3
import os
from typing import List, Optional, Tuple

# Database path: backend/data/whatsapp_links.db
BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BACKEND_ROOT, "backend", "data")
DB_PATH = os.path.join(DATA_DIR, "whatsapp_links.db")


def init_pages_table():
    """Initialize pages table in database"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        UNIQUE(url, user_id)
    )
    ''')
    
    conn.commit()
    conn.close()


def save_pages(pages: List[dict], user_id: int) -> None:
    """
    Save pages to database for a specific user
    
    Args:
        pages: List of page dicts with 'url' and 'name'
        user_id: ID of the user who owns these pages
    """
    init_pages_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Remove all existing pages for this user
    c.execute('DELETE FROM pages WHERE user_id = ?', (user_id,))
    
    # Insert new pages
    for page in pages:
        try:
            c.execute('INSERT INTO pages (url, name, user_id) VALUES (?, ?, ?)',
                     (page.get('url', ''), page.get('name', ''), user_id))
        except Exception:
            continue
    
    conn.commit()
    conn.close()


def load_pages(user_id: int) -> List[dict]:
    """
    Load pages from database for a specific user
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of page dicts with 'url' and 'name'
    """
    init_pages_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT url, name FROM pages WHERE user_id = ? ORDER BY id ASC', (user_id,))
    rows = c.fetchall()
    conn.close()
    
    return [{'url': row[0], 'name': row[1]} for row in rows]


def add_page(url: str, name: str, user_id: int) -> bool:
    """
    Add a single page for a user
    
    Args:
        url: Page URL
        name: Page name/campaign
        user_id: ID of the user
        
    Returns:
        True if added, False if already exists
    """
    init_pages_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO pages (url, name, user_id) VALUES (?, ?, ?)',
                 (url, name, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def delete_page(url: str, user_id: int) -> bool:
    """
    Delete a page for a user
    
    Args:
        url: Page URL to delete
        user_id: ID of the user
        
    Returns:
        True if deleted, False if not found
    """
    init_pages_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM pages WHERE url = ? AND user_id = ?', (url, user_id))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted

