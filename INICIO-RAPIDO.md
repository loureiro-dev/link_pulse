# ⚡ Início Rápido - LinkPulse

## 🚀 Iniciar o Sistema Completo

### Windows PowerShell (Recomendado)

```powershell
# Opção 1: Iniciar tudo de uma vez (abre 2 janelas)
.\start-all.ps1

# Opção 2: Iniciar separadamente
.\start-backend.ps1    # Em um terminal
.\start-frontend.ps1   # Em outro terminal
```

**⚠️ IMPORTANTE:** No PowerShell, sempre use `.\` antes do nome do script!

### Windows CMD

```cmd
start-backend.bat
start-frontend.bat
```

## 📍 URLs de Acesso

Após iniciar, acesse:

- **Dashboard:** http://localhost:3000
- **API Backend:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs

## ✅ Checklist de Primeira Execução

- [ ] Backend iniciado na porta 8000
- [ ] Frontend iniciado na porta 3000
- [ ] Dashboard carregando sem erros
- [ ] Adicionar primeira página para monitoramento
- [ ] Executar scraper pela primeira vez
- [ ] (Opcional) Configurar Telegram para notificações

## 🎯 Primeiros Passos

1. **Adicionar uma página:**
   - No dashboard, clique em "+ Adicionar Página"
   - Cole a URL da landing page
   - Dê um nome para a campanha
   - Clique em "Adicionar"

2. **Executar o scraper:**
   - Clique em "🚀 Executar Scraper Agora"
   - Aguarde a execução
   - Veja os resultados na tabela

3. **Visualizar links:**
   - Todos os links coletados aparecem na tabela
   - Você pode copiar links clicando em "Copiar"

## 🆘 Problemas Comuns

**Backend não inicia:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend não inicia:**
```powershell
cd frontend
npm install
npm run dev
```

**Erro de porta em uso:**
- Backend: Altere a porta no comando uvicorn ou no script
- Frontend: Altere no `package.json` ou use `npm run dev -- -p 3001`

---

**Pronto para usar! 🎉**

