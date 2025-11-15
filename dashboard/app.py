# dashboard/app.py
import os
import sys
import io
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# Adiciona a raiz do projeto ao sys.path para importar src.*
# ------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)
PAGES_FILE = os.path.join(DATA_DIR, "pages.csv")
LAST_RUN_FILE = os.path.join(DATA_DIR, "last_run.txt")

# ------------------------------------------------------------
# Funções de gerenciamento de páginas (CRUD básico + import/export)
# ------------------------------------------------------------
def load_pages():
    """Carrega páginas (url, name) do CSV."""
    if not os.path.exists(PAGES_FILE):
        return pd.DataFrame(columns=["url", "name"])
    try:
        return pd.read_csv(PAGES_FILE)
    except Exception:
        # se o CSV tiver problema, recriar vazio
        return pd.DataFrame(columns=["url", "name"])

def save_pages_df(df):
    df.to_csv(PAGES_FILE, index=False)

def save_page(url, name):
    df = load_pages()
    # evita duplicata exata de URL
    if (df['url'] == url).any():
        return False
    new_row = {"url": url, "name": name}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_pages_df(df)
    return True

def update_page(old_url, new_url, new_name):
    df = load_pages()
    idx = df.index[df['url'] == old_url]
    if len(idx) == 0:
        return False
    i = idx[0]
    df.at[i, 'url'] = new_url
    df.at[i, 'name'] = new_name
    save_pages_df(df)
    return True

def delete_page(url):
    df = load_pages()
    df = df[df['url'] != url]
    save_pages_df(df)

def import_pages_from_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # requer colunas url,name
        if 'url' not in df.columns or 'name' not in df.columns:
            return False, "Arquivo CSV precisa ter colunas: url,name"
        df_exist = load_pages()
        df_combined = pd.concat([df_exist, df], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['url'])
        save_pages_df(df_combined)
        return True, f"{len(df)} linhas importadas (duplicatas removidas)"
    except Exception as e:
        return False, str(e)

def export_pages_to_bytes():
    df = load_pages()
    b = df.to_csv(index=False).encode("utf-8")
    return b

# ------------------------------------------------------------
# Scraper runner (usa os módulos em src/ — imports com src.)
# ------------------------------------------------------------
# Observação: collect_from_page em src.collectors.requests_collector retorna (links, has_form, is_thanks)
from src.collectors.requests_collector import collect_from_page
from src.processing.cleaning import normalize_whatsapp_link, is_group_link
from src.storage.database import save_links, list_links

def write_last_run(msg):
    try:
        with open(LAST_RUN_FILE, "w", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} - {msg}")
    except:
        pass

def read_last_run():
    if not os.path.exists(LAST_RUN_FILE):
        return "Nunca"
    try:
        with open(LAST_RUN_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Erro ao ler"

def run_scraper_from_dashboard():
    """
    Executa o scraper para cada página cadastrada.
    Retorna lista de tuplas (link, campaign_name).
    """
    pages = load_pages()
    all_found = []
    total_checked = 0
    for _, row in pages.iterrows():
        url = str(row.get("url")).strip()
        name = str(row.get("name")).strip()
        if not url:
            continue
        total_checked += 1
        try:
            links, has_form, is_thanks = collect_from_page(url)
        except Exception as e:
            # se o collector falhar, só continuar
            links, has_form, is_thanks = [], False, False

        cleaned = []
        for l in links:
            c = normalize_whatsapp_link(l)
            if is_group_link(c):
                cleaned.append(c)

        # remove duplicatas locais
        cleaned = list(dict.fromkeys(cleaned))
        if cleaned:
            # salva no DB usando save_links (espera lista de strings)
            save_links(cleaned, source=name)
            for link in cleaned:
                all_found.append((link, name))

    write_last_run(f"Coleta finalizada. Páginas verificadas: {total_checked}, links encontrados: {len(all_found)}")
    return all_found

# ------------------------------------------------------------
# UI / Streamlit
# ------------------------------------------------------------
st.set_page_config(page_title="WhatsApp Link Intelligence", layout="wide")

# CSS simples para melhorar visual
st.markdown("""
    <style>
    .title {
        font-size:32px;
        font-weight:700;
        color:#0d6efd;
    }
    .section {
        padding: 8px 12px;
        border-radius:8px;
        background: #ffffff;
        border: 1px solid #efefef;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🚀 WhatsApp Link Intelligence</div>", unsafe_allow_html=True)
st.write("Painel para monitoramento de links de grupos do WhatsApp — adicione páginas, rode a coleta e receba relatórios.")

# TOP ROW: metrics and last run
col_a, col_b, col_c = st.columns([1, 2, 1])

# carregando links do DB para métricas
rows = list_links(10000)  # pega muitos por default
df_links = pd.DataFrame(rows, columns=["url", "source", "found_at"]) if rows else pd.DataFrame(columns=["url", "source", "found_at"])

with col_a:
    st.subheader("Métricas rápidas")
    st.metric("Total links", int(df_links.shape[0]))
    st.metric("Campanhas", int(df_links['source'].nunique() if not df_links.empty else 0))

with col_b:
    st.subheader("Última execução")
    st.write(read_last_run())

with col_c:
    # import/export buttons
    st.subheader("Gerenciar páginas")
    col_down, col_up = st.columns(2)
    if st.button("Exportar páginas (CSV)"):
        b = export_pages_to_bytes()
        st.download_button("Baixar CSV", data=b, file_name="pages.csv", mime="text/csv")
    uploaded = st.file_uploader("Importar CSV (url,name)", type=["csv"])
    if uploaded:
        ok, msg = import_pages_from_file(uploaded)
        if ok:
            st.success(msg)
        else:
            st.error(msg)


st.write("---")

# show links table and basic charts
left_col, right_col = st.columns([3, 1])

with left_col:
    st.subheader("Links coletados")
    if not df_links.empty:
        # filter controls
        sources = ["(todos)"] + sorted(df_links['source'].dropna().unique().tolist())
        sel_source = st.selectbox("Filtrar por campanha", sources)
        df_view = df_links.copy()
        if sel_source and sel_source != "(todos)":
            df_view = df_view[df_view['source'] == sel_source]

        # date filter
        try:
            df_view['found_at_dt'] = pd.to_datetime(df_view['found_at'], errors='coerce')
            min_date = df_view['found_at_dt'].min().date()
            max_date = df_view['found_at_dt'].max().date()
            date_range = st.date_input("Intervalo de datas", value=(min_date, max_date) if pd.notnull(min_date) else None)
            if date_range and len(date_range) == 2 and pd.notnull(min_date):
                start, end = date_range
                df_view = df_view[(df_view['found_at_dt'].dt.date >= start) & (df_view['found_at_dt'].dt.date <= end)]
        except Exception:
            pass

        st.dataframe(df_view[['url','source','found_at']].sort_values('found_at', ascending=False), use_container_width=True, height=360)

        # time series
        try:
            series = pd.to_datetime(df_links['found_at']).dt.date.value_counts().sort_index()
            series.index = pd.to_datetime(series.index)
            st.subheader("Evolução diária")
            st.line_chart(series)
        except Exception:
            pass

    else:
        st.info("Nenhum link coletado ainda.")

with right_col:
    st.subheader("Ações rápidas")
    st.write("Clique para executar ou ver histórico.")
    if st.button("🚀 Iniciar Coleta"):
        with st.spinner("Executando coleta..."):
            result = run_scraper_from_dashboard()
            if result:
                st.success(f"{len(result)} links coletados.")
                # mostra exemplos
                for r in result[:10]:
                    st.write(f"• {r[1]} — {r[0]}")
            else:
                st.info("Nenhum link novo encontrado.")
    if st.button("💾 Forçar salvar DB (vacuum)"):
        # no projeto simples não temos vacuum exposto, apenas indicamos
        st.info("Operação simples — nada a executar aqui no ambiente leve.")
    st.markdown("---")
    st.subheader("Prompt alternativo para IA")
    st.caption("Caso não saiba de código use este prompt em uma IA para melhorar o scraper com base nas suas necessidades")
    prompt_text = """Estou trabalhando em um projeto que coleta links de grupos do WhatsApp em páginas de captura. O projeto usa requests+Selenium, grava links em SQLite e exibe dashboard Streamlit. 
Preciso de sugestões para:
- melhorar a heurística de extração (links escondidos em JS, iframes)
- otimizar a normalização de links
Forneça exemplos de regex, trechos de código em Python (requests + BeautifulSoup + Selenium) e ideias de testes automatizados."""
    st.code(prompt_text, language="text")
    st.caption("Copie e cole esse prompt em outra IA se precisar.")

st.write("---")

# Pages management: add/update/delete
st.subheader("Gerenciar páginas de captura")

pages_df = load_pages()
if pages_df.empty:
    st.info("Nenhuma página cadastrada. Use o formulário abaixo para adicionar.")
else:
    st.dataframe(pages_df, use_container_width=True, height=160)

# Edit/delete UI
with st.form("edit_form"):
    st.write("Editar / Excluir página")
    pages_list = pages_df['url'].tolist() if not pages_df.empty else []
    sel = st.selectbox("Selecionar URL", [""] + pages_list)
    new_url = st.text_input("URL (editar)", value=sel)
    new_name = st.text_input("Nome (editar)", value=(pages_df[pages_df['url']==sel]['name'].values[0] if sel else ""))
    btn_update = st.form_submit_button("Atualizar")
    btn_delete = st.form_submit_button("Excluir")

    if btn_update and sel:
        ok = update_page(sel, new_url, new_name)
        if ok:
            st.success("Página atualizada.")
        else:
            st.error("Não foi possível atualizar.")
    if btn_delete and sel:
        delete_page(sel)
        st.success("Página excluída.")

st.write("---")

# Add new page form
st.subheader("Adicionar nova página")

with st.form("add_form"):
    in_url = st.text_input("URL")
    in_name = st.text_input("Nome da campanha")
    add_sub = st.form_submit_button("Adicionar")
    if add_sub:
        if in_url.strip() and in_name.strip():
            ok = save_page(in_url.strip(), in_name.strip())
            if ok:
                st.success("Página adicionada.")
            else:
                st.info("URL já cadastrada.")
        else:
            st.error("Preencha URL e Nome.")

st.write("---")

# footer
st.markdown("### Status & Ajuda")
st.write(f"Data/hora local: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.write("Se quiser, posso adicionar export de logs, autenticação, ou deploy em Heroku/Render.")
