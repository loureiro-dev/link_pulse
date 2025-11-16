"""
User database operations
Handles user creation, authentication, and retrieval
"""

import sqlite3
import os
from typing import Optional, Tuple
from backend.db.connection import DATA_DIR, DB_PATH
from backend.auth.jwt import get_password_hash, verify_password

def init_users_table():
    """Initialize users table in database"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        name TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


def create_user(email: str, password: str, name: Optional[str] = None) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Create a new user in the database
    
    Args:
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        name: Optional user name
        
    Returns:
        Tuple of (success, user_id, error_message)
        If success=False, user_id is None and error_message contains reason
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if user already exists
        c.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
        if c.fetchone():
            conn.close()
            return False, None, "Email already registered"
        
        # Hash password and insert user
        hashed_password = get_password_hash(password)
        c.execute('''
            INSERT INTO users (email, hashed_password, name)
            VALUES (?, ?, ?)
        ''', (email.lower(), hashed_password, name))
        
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return True, user_id, None
    except Exception as e:
        conn.close()
        return False, None, f"Error creating user: {str(e)}"


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email from database
    
    Args:
        email: User email
        
    Returns:
        User dict with id, email, hashed_password, name, or None if not found
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, email, hashed_password, name FROM users WHERE email = ?', (email.lower(),))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "name": row[3]
        }
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Get user by ID from database
    
    Args:
        user_id: User ID
        
    Returns:
        User dict with id, email, name, or None if not found
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "name": row[2]
        }
    return None


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate user with email and password
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        User dict if authentication successful, None otherwise
    """
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"]
    }

