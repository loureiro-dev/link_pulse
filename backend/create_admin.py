#!/usr/bin/env python3
"""
Script para criar usuário admin ou tornar usuário existente em admin
"""
import sqlite3
import os
import sys

# Caminho do banco
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'whatsapp_links.db')

# Importa função de hash
sys.path.insert(0, os.path.dirname(__file__))
try:
    from backend.auth.jwt import get_password_hash
except ImportError:
    # Se não conseguir importar, tenta criar hash manualmente
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

def create_or_update_admin():
    """Cria ou atualiza usuário admin"""
    if not os.path.exists(DB_PATH):
        print("Banco de dados nao encontrado. Execute o backend primeiro para criar o banco.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    admin_email = "admin@linkpulse.com"
    admin_password = "admin123"
    
    # Verifica se admin já existe
    c.execute('SELECT id, is_admin, approved FROM users WHERE email = ?', (admin_email,))
    existing = c.fetchone()
    
    if existing:
        # Atualiza para admin e aprovado
        c.execute('UPDATE users SET is_admin = 1, approved = 1 WHERE email = ?', (admin_email,))
        conn.commit()
        print(f"Usuario admin {admin_email} atualizado com sucesso!")
        print(f"Senha: {admin_password}")
    else:
        # Cria novo admin
        hashed_password = get_password_hash(admin_password)
        c.execute('''
            INSERT INTO users (email, hashed_password, name, is_admin, approved)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_email, hashed_password, "Administrador", 1, 1))
        conn.commit()
        print(f"Usuario admin {admin_email} criado com sucesso!")
        print(f"Senha: {admin_password}")
    
    conn.close()

if __name__ == "__main__":
    create_or_update_admin()

