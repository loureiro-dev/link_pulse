# Script para iniciar o frontend
Write-Host "🚀 Iniciando Frontend..." -ForegroundColor Green

# Navega para o diretório frontend
Set-Location frontend

# Verifica se node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    npm install
}

# Inicia o servidor de desenvolvimento
Write-Host "🌐 Iniciando servidor na porta 3000..." -ForegroundColor Cyan
npm run dev

