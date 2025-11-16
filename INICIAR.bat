@echo off
echo ========================================
echo   LinkPulse - Iniciar Sistema Completo
echo ========================================
echo.
echo Escolha uma opcao:
echo.
echo 1. Iniciar Backend e Frontend (Recomendado)
echo 2. Iniciar apenas Backend
echo 3. Iniciar apenas Frontend
echo 4. Sair
echo.
set /p opcao="Digite o numero da opcao: "

if "%opcao%"=="1" (
    echo.
    echo Iniciando Backend e Frontend...
    start powershell -NoExit -File "%~dp0start-all.ps1"
    goto fim
)

if "%opcao%"=="2" (
    echo.
    echo Iniciando Backend...
    start powershell -NoExit -File "%~dp0start-backend.ps1"
    goto fim
)

if "%opcao%"=="3" (
    echo.
    echo Iniciando Frontend...
    start powershell -NoExit -File "%~dp0start-frontend.ps1"
    goto fim
)

if "%opcao%"=="4" (
    goto fim
)

echo Opcao invalida!
pause
:fim

