from fastapi import APIRouter, HTTPException, Depends
from backend.auth.middleware import get_current_user
from backend.main import LOGS_FILE
import os

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/recent")
async def get_recent_logs(lines: int = 50, current_user: dict = Depends(get_current_user)):
    """
    Retorna as últimas linhas do arquivo de log.
    Utilizado pelo LogConsole para exibição em tempo real.
    """
    if not os.path.exists(LOGS_FILE):
        return {"logs": []}
    
    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as f:
            # Pega as últimas 'lines' linhas
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return {"logs": [line.strip() for line in recent]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler logs: {str(e)}")
