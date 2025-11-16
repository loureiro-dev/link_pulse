# Script para iniciar backend e frontend simultaneamente
Write-Host "🚀 Iniciando Backend e Frontend..." -ForegroundColor Green

# Obtém o diretório do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Inicia o backend em uma nova janela
Write-Host "📦 Iniciando Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$ScriptDir\start-backend.ps1"

# Aguarda um pouco para o backend iniciar
Start-Sleep -Seconds 3

# Inicia o frontend em uma nova janela
Write-Host "📦 Iniciando Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$ScriptDir\start-frontend.ps1"

Write-Host ""
Write-Host "✅ Backend e Frontend iniciados em janelas separadas!" -ForegroundColor Green
Write-Host "📝 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📝 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione qualquer tecla para fechar esta janela..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

