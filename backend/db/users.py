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
        is_admin INTEGER DEFAULT 0,
        approved INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Migração: adicionar colunas is_admin e approved se não existirem
    try:
        c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    try:
        c.execute('ALTER TABLE users ADD COLUMN approved INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    
    # Criar primeiro admin se não existir nenhum usuário
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Criar usuário admin padrão (senha: admin123 - deve ser alterada!)
        from backend.auth.jwt import get_password_hash
        admin_password = get_password_hash("admin123")
        c.execute('''
            INSERT INTO users (email, hashed_password, name, is_admin, approved)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin@linkpulse.com", admin_password, "Administrador", 1, 1))
        conn.commit()
    
    conn.commit()
    conn.close()


def create_user(email: str, password: str, name: Optional[str] = None, is_admin: bool = False, approved: bool = False) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Create a new user in the database
    
    Args:
        email: User email (must be unique)
        password: Plain text password (will be hashed)
        name: Optional user name
        is_admin: Whether user is admin (default: False)
        approved: Whether user is approved (default: False)
        
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
        
        # Hash password and insert user (novos usuários começam não aprovados)
        hashed_password = get_password_hash(password)
        c.execute('''
            INSERT INTO users (email, hashed_password, name, is_admin, approved)
            VALUES (?, ?, ?, ?, ?)
        ''', (email.lower(), hashed_password, name, 1 if is_admin else 0, 1 if approved else 0))
        
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
        User dict with id, email, hashed_password, name, is_admin, approved, or None if not found
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, email, hashed_password, name, is_admin, approved FROM users WHERE email = ?', (email.lower(),))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "hashed_password": row[2],
            "name": row[3],
            "is_admin": bool(row[4]) if len(row) > 4 else False,
            "approved": bool(row[5]) if len(row) > 5 else False
        }
    return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Get user by ID from database
    
    Args:
        user_id: User ID
        
    Returns:
        User dict with id, email, name, is_admin, approved, or None if not found
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT id, email, name, is_admin, approved FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "is_admin": bool(row[3]) if len(row) > 3 else False,
            "approved": bool(row[4]) if len(row) > 4 else False
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
        Note: Returns user even if not approved (check approved field)
    """
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["hashed_password"]):
        return None
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "is_admin": user.get("is_admin", False),
        "approved": user.get("approved", False)
    }


def list_all_users(include_pending: bool = True) -> list:
    """
    List all users from database
    
    Args:
        include_pending: If True, includes pending users, otherwise only approved
        
    Returns:
        List of user dicts
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if include_pending:
        c.execute('SELECT id, email, name, is_admin, approved, created_at FROM users ORDER BY created_at DESC')
    else:
        c.execute('SELECT id, email, name, is_admin, approved, created_at FROM users WHERE approved = 1 ORDER BY created_at DESC')
    
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "is_admin": bool(row[3]),
            "approved": bool(row[4]),
            "created_at": row[5] if len(row) > 5 else None
        }
        for row in rows
    ]


def approve_user(user_id: int) -> bool:
    """
    Approve a user
    
    Args:
        user_id: User ID to approve
        
    Returns:
        True if successful, False otherwise
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('UPDATE users SET approved = 1 WHERE id = ?', (user_id,))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception:
        conn.close()
        return False


def reject_user(user_id: int) -> bool:
    """
    Reject/delete a user
    
    Args:
        user_id: User ID to reject/delete
        
    Returns:
        True if successful, False otherwise
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception:
        conn.close()
        return False


def update_user_profile(user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> bool:
    """
    Update user profile information
    
    Args:
        user_id: User ID
        name: New name (optional)
        email: New email (optional)
        
    Returns:
        True if successful, False otherwise
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if email is not None:
            # Check if email already exists
            c.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email.lower(), user_id))
            if c.fetchone():
                conn.close()
                return False
            updates.append('email = ?')
            params.append(email.lower())
        
        if not updates:
            conn.close()
            return False
        
        params.append(user_id)
        query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
        c.execute(query, params)
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception:
        conn.close()
        return False


def update_user_password(user_id: int, new_password: str) -> bool:
    """
    Update user password
    
    Args:
        user_id: User ID
        new_password: New plain text password (will be hashed)
        
    Returns:
        True if successful, False otherwise
    """
    init_users_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        hashed_password = get_password_hash(new_password)
        c.execute('UPDATE users SET hashed_password = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception:
        conn.close()
        return False


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin
    
    Args:
        user_id: User ID
        
    Returns:
        True if user is admin, False otherwise
    """
    user = get_user_by_id(user_id)
    return user.get("is_admin", False) if user else False


