@echo off
echo 🚀 Iniciando Frontend...
cd frontend
if not exist node_modules (
    echo 📦 Instalando dependências...
    call npm install
)
echo 🌐 Iniciando servidor na porta 3000...
npm run dev
pause

