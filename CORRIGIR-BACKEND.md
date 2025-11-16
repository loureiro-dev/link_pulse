# 🔧 CORREÇÃO URGENTE - Múltiplos Backends Rodando

## ⚠️ PROBLEMA DETECTADO:

Há **2 processos** rodando na porta 8000 simultaneamente. Isso causa conflito!

## ✅ SOLUÇÃO:

### 1. Pare TODOS os processos do backend:

```powershell
# Opção 1: Parar todos os processos Python na porta 8000
Get-Process -Name python | Where-Object {$_.Id -in @(8232, 13184)} | Stop-Process -Force

# Opção 2: Parar manualmente
# Vá em cada terminal onde o backend está rodando e pressione Ctrl+C
```

### 2. Verifique se a porta está livre:

```powershell
netstat -ano | findstr :8000
```

Se ainda aparecer algo, a porta não está livre.

### 3. Inicie APENAS UM backend:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Aguarde a mensagem:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 🧪 TESTE:

1. **Teste no navegador:**
   - Acesse: http://localhost:8000/api/pages
   - Deve retornar as 2 páginas em JSON

2. **Recarregue o frontend:**
   - Pressione F5 na página de gerenciamento
   - As páginas devem aparecer!

## 📝 Páginas que devem aparecer:

- ✅ "black cripto"
- ✅ "black fluency"

---

**Após fazer isso, o erro deve desaparecer!** 🎉

