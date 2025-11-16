#!/usr/bin/env python3
"""
Test script to verify /auth/me endpoint returns is_admin correctly
"""
import sys
import os
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_auth_me():
    """Test /auth/me endpoint"""
    # First, login to get a token
    login_url = "http://localhost:8000/auth/login"
    login_data = {
        "email": "gusta.loureiro.dev@gmail.com",
        "password": "sua_senha_aqui"  # User needs to provide password
    }
    
    print("Testando endpoint /auth/me...")
    print("=" * 50)
    print("NOTA: Este script precisa que você forneça a senha do usuário")
    print("Ou você pode testar manualmente fazendo login e depois:")
    print("1. Abra o console do navegador (F12)")
    print("2. Execute: fetch('http://localhost:8000/auth/me', { headers: { 'Authorization': 'Bearer ' + document.cookie.match(/linkpulse_token=([^;]+)/)?.[1] } }).then(r => r.json()).then(console.log)")
    print("=" * 50)

if __name__ == "__main__":
    test_auth_me()

