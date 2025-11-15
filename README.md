# WhatsApp Link Intelligence — Projeto Pessoal de Estudo 🚀


- Aprender e aplicar scraping avançado (Requests + BeautifulSoup + Selenium).
- Criar um pipeline de dados que seja fácil de entender, mas completo.
- Armazenar links coletados em um banco SQLite simples.
- Construir um minidashboard para visualizar resultados.
- Treinar habilidades úteis para Data Science e Engenharia de Dados.
- E claro, automatizar algo que eu já fazia manualmente  ~E

---
# 🚀 WhatsApp Link Intelligence

Um projeto pessoal criado para automatizar um problema real do dia a dia:
monitorar links de grupos do WhatsApp escondidos em páginas de lançamento.

Com o tempo percebi que muitos produtores digitais escondem esses links dentro de:
- HTML quebrado  
- scripts JS
- iframes
- campos invisíveis
- redirecionamentos

Fazer isso manualmente era cansativo, então transformei o processo em um mini pipeline:
**coletar → limpar → detectar → armazenar → visualizar → notificar (opcional).**

Este projeto foi criado com o objetivo de:
- treinar habilidades de *data scraping*
- praticar engenharia de dados
- construir um dashboard real utilizando Streamlit
- consolidar boas práticas de projeto
- ter um case sólido para portfólio e currículo

---

# 🧠 O que este projeto faz

### ✔ Coleta links públicos de grupos de WhatsApp
Procura padrões do tipo:

- `https://chat.whatsapp.com/...`
- `https://api.whatsapp.com/send?phone=...`

### ✔ Extrai e normaliza links escondidos  
Limpa, normaliza e valida somente links que realmente são de **grupos**.

### ✔ Armazena tudo em um banco SQLite  
Sem complicação: um arquivo `.db` dentro da pasta `data/`.

### ✔ Evita duplicatas automaticamente  
Mesmo que o link apareça várias vezes, só 1 registro é salvo.

### ✔ Dashboard Streamlit completo
Com:
- tabela de links coletados  
- filtros por campanha e data  
- gráficos (linha e distribuição por fontes)
- CRUD de páginas (adicionar, editar, excluir)
- importação/exportação CSV  
- botão **Executar Scraper Agora**  
- registro da última execução  
- seção de métricas rápidas  
- tema visual simples e amigável  

### ✔ Notificação no Telegram (opcional)
Receba alertas sempre que novos links forem encontrados.

---

## 🧱 Estrutura do Projeto

```
src/
    collectors/        # Módulos de coleta (requests e selenium)
    processing/        # Limpeza e normalização de links
    storage/           # Banco de dados SQLite
    notifications/     # Notificação via Telegram (opcional)
    pipeline.py        # Pipeline principal
dashboard/
    app.py             # Dashboard em Streamlit
notebooks/
    exploratory_analysis.ipynb
data/
    raw/               # HTML bruto (opcional)
    processed/         # CSV/Parquet (opcional)
```

---

## 🚀 Como usar

1. Crie um ambiente virtual:

```
python -m venv venv
source venv/bin/activate
```

2. Instale dependências:

```
pip install -r requirements.txt
```

3. Configure (opcional) variáveis de ambiente para Telegram:

```
export WL_TOKEN="seu_token"
export WL_CHAT_ID="seu_chat"
```

4. Execute o pipeline:

```
python -m src.pipeline
```

5. Rode o dashboard:

```
streamlit run dashboard/app.py
```

Como usar o painel
➕ Adicionar páginas

No painel, use o formulário:

URL da landing page

Nome da campanha

Exemplo:

https://minhacaptura.com/inscricao
Nome da campanha: Workshop Inteligência Digital

🚀 Rodar o scraper

Clique no botão:
Iniciar Coleta

Ele vai:

visitar todas as páginas cadastradas

extrair possíveis links

filtrar apenas WhatsApp válidos

salvar no banco

atualizar o dashboard

📁 Exportar/Importar CSV

Ideal para organizar campanhas maiores.

---

## 📌 Algumas limitações (sim, existem!)

- Páginas com **recaptcha** ainda travam o scraper.
- Alguns links aparecem apenas após fluxos complexos (multi-step), e ainda não implementei tudo.
- Em ambientes sem Chrome/Chromedriver, o Selenium pode não funcionar.
- A heurística de “página de obrigado” é simples — aceita sugestões!

---

## 🧠 Ideias futuras

- Implementar coleta distribuída.
- Exportar tudo para um data lake (S3/MinIO).
- Criar modelo para prever quais páginas têm maior chance de esconder grupos.
- Melhorar parser de JavaScript.

Se quiser contribuir, fique à vontade 🙂  
