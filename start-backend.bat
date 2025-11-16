@echo off
echo 🚀 Iniciando Backend...
cd backend
call venv\Scripts\activate.bat
echo 🌐 Iniciando servidor na porta 8000...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause

