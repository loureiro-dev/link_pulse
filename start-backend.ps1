# Script para iniciar o backend
Write-Host "🚀 Iniciando Backend..." -ForegroundColor Green

# Navega para o diretório backend
Set-Location backend

# Ativa o ambiente virtual
Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Inicia o servidor uvicorn
Write-Host "🌐 Iniciando servidor na porta 8000..." -ForegroundColor Cyan
uvicorn main:app --reload --host 0.0.0.0 --port 8000

