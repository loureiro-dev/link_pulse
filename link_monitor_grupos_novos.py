import os
import re
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

# ==============================================================================
# 📋 CONFIGURAÇÃO E DADOS
# ==============================================================================
TOKEN = "7585232781:AAGCEXAojfQbxc-tgCzifXbzD89AP4F7YIE"
CHAT_ID = "1289789994"
ARQUIVO_LINKS = "grupos_enviados.txt"
ARQUIVO_PAGINAS = "paginas.json"

def carregar_paginas():
    if not os.path.exists(ARQUIVO_PAGINAS):
        paginas_padrao = [
            ["https://sndflw.com/i/primeiro-dolar-26?fbclid=PAVERFWARCHslleHRuA2FlbQEwAGFkaWQBqzGZfLTKy3NydGMGYXBwX2lkDzEyNDAyNDU3NDI4NzQxNAABp1rx5QV3Wv7FfN3KdtyNNOFlqKQi5FtMV-chFBxb9WCShBuNDBpMVT4oM11C_aem__w6NfZ_BwptwhBHHGh8CSA", "Primeiro Dolar 26"]
        ]
        with open(ARQUIVO_PAGINAS, "w", encoding="utf-8") as f:
            json.dump(paginas_padrao, f, indent=4, ensure_ascii=False)
        return paginas_padrao
    
    with open(ARQUIVO_PAGINAS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []
# Padrões compilados para melhor performance na busca de links
PADROES_BUSCA = {
    "WhatsApp": re.compile(r'https?://(?:chat\.whatsapp\.com|api\.whatsapp\.com|wa\.me)/[^\s"\'<>]+', re.IGNORECASE),
    "Telegram": re.compile(r'https?://(?:t\.me|telegram\.me)/[^\s"\'<>]+', re.IGNORECASE),
    "SendFlow": re.compile(r'https?://(?:sendflow\.pro|sndflw\.com|i\.sendflow\.pro)/[^\s"\'<>]+', re.IGNORECASE)
}

# ==============================================================================
# 🔧 FUNÇÕES AUXILIARES
# ==============================================================================

def carregar_grupos_enviados():
    """Carrega grupos já enviados para evitar duplicatas."""
    if not os.path.exists(ARQUIVO_LINKS):
        return set()
    with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
        return {linha.strip() for linha in f if linha.strip()}

def salvar_grupo_enviado(grupo_link):
    """Adiciona o link de um grupo à lista de já enviados."""
    with open(ARQUIVO_LINKS, "a", encoding="utf-8") as f:
        f.write(f"{grupo_link}\n")

def extrair_link_limpo(link_completo):
    """Extrai apenas a URL limpa (sem o prefixo de tipo)."""
    return link_completo.split(": ", 1)[1] if ": " in link_completo else link_completo

def eh_grupo(link):
    """Verifica se a URL pertence a um grupo válido (ignorando chats individuais)."""
    link_limpo = extrair_link_limpo(link).lower()
    
    if "chat.whatsapp.com" in link_limpo:
        return True
    
    if "t.me/" in link_limpo or "telegram.me/" in link_limpo:
        # Excluir chats individuais que contêm números de telefone
        return not bool(re.search(r'/\+?\d+', link_limpo))
        
    return False

def enviar_telegram(mensagem):
    """Envia uma mensagem de texto para o Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar para o Telegram: {e}")
        return False

def buscar_links(url):
    """Acessa a página informada e extrai os links que correspodem aos padrões."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        html = requests.get(url, headers=headers, timeout=15, allow_redirects=True).text
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return []

    links_encontrados = set()
    for tipo, padrao in PADROES_BUSCA.items():
        for match in padrao.finditer(html):
            link_limpo = match.group(0).rstrip('",\')}]')
            if len(link_limpo) > 10:
                links_encontrados.add(f"{tipo}: {link_limpo}")
                
    return list(links_encontrados)

def obter_info_grupo(url_grupo):
    """Acessa o link de convite do WhatsApp/Telegram e tenta extrair o Nome (og:title)"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        html = requests.get(url_grupo, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            titulo = og_title['content']
            if titulo == "WhatsApp Group Invite" or titulo == "Join group chat on Telegram":
                return "Grupo Restrito/Sem Nome Exposto"
            return titulo
        return "Grupo Sem Titulo Capturado"
    except Exception:
        return "Nome Indisponível"

# ==============================================================================
# 🚀 FLUXO PRINCIPAL
# ==============================================================================

def main():
    print(f"\n🚀 Iniciando busca por GRUPOS NOVOS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    grupos_enviados = carregar_grupos_enviados()
    total_novos_encontrados = []
    
    PAGINAS = carregar_paginas()
    
    if not PAGINAS:
        print("   ❌ Nenhuma página configurada. Adicione links pela interface.")
        return
    
    for url, nome in PAGINAS:
        print(f"\n📡 Verificando: {nome}")
        
        # Obter apenas links que sejam efetivamente grupos
        links = buscar_links(url)
        grupos = [link for link in links if eh_grupo(link)]
        
        if not grupos:
            print("   ❌ Nenhum grupo encontrado.")
            continue
            
        print(f"   🔍 Encontrados {len(grupos)} grupo(s)")
        
        # Determinar quais grupos são realmente não vistos (novos)
        grupos_novos = []
        for grupo in grupos:
            link_limpo = extrair_link_limpo(grupo)
            if link_limpo not in grupos_enviados:
                nome_real = obter_info_grupo(link_limpo)
                grupos_novos.append((grupo, nome_real))
                print(f"   ✅ NOVO: [{nome_real}] - {grupo}")
            else:
                print(f"   ❌ JÁ ENVIADO: {grupo}")
                
        # Enviar alerta ao Telegram se houver novos grupos
        if grupos_novos:
            data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            linhas_msg = [
                "🆕 **GRUPO(S) NOVO(S) ENCONTRADO(S)!**\n",
                f"🎯 **{nome}**",
                f"🕐 {data_hora}\n"
            ]
            
            for i, (grupo, nome_real) in enumerate(grupos_novos, 1):
                tipo, link = grupo.split(": ", 1)
                linhas_msg.append(f"{i}. 🗣️ **{nome_real}**\n   🔗 {tipo}: {link}\n")
                
            linhas_msg.append(f"\n📊 Total: {len(grupos_novos)} grupo(s) novo(s)")
            linhas_msg.append(f"📍 Fonte: {nome}")
            
            mensagem_final = "\n".join(linhas_msg)
            
            if enviar_telegram(mensagem_final):
                print(f"✅ ENVIADO! {len(grupos_novos)} grupo(s) novo(s) de {nome}")
                # Registrar grupos enviados para não repeti-los no futuro
                for (grupo, nome_real) in grupos_novos:
                    salvar_grupo_enviado(extrair_link_limpo(grupo))
                total_novos_encontrados.extend([g for g, n in grupos_novos])
            else:
                print(f"   ❌ ERRO ao enviar grupos de {nome}")
        else:
            print("   ℹ️  Nenhum grupo novo (todos já foram enviados)")

    # 🏁 Relatório de encerramento da execução atual
    print("\n🏁 RESUMO FINAL:")
    print(f"   📊 Páginas verificadas: {len(PAGINAS)}")
    print(f"   🆕 Grupos novos encontrados: {len(total_novos_encontrados)}")
    
    # Se não houve nenhum grupo novo no monitoramento de todas as páginas,
    # informamos o Telegram a fim de garantir que o robô está ativo e operando.
    if not total_novos_encontrados:
        print("   📱 Enviando relatório de 'nenhum grupo novo'")
        msg_status = (
            "📊 **Relatório de Monitoramento**\n"
            f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"✅ {len(PAGINAS)} páginas verificadas\n"
            "❌ Nenhum grupo novo encontrado\n"
            "ℹ️  Todos os grupos já foram enviados anteriormente\n\n"
            "🔄 Próxima verificação conforme agendamento"
        )
        enviar_telegram(msg_status)
    else:
        print("   ✅ Grupos novos foram enviados - sem relatório adicional")
        
    print(f"\n🎯 CONCLUÍDO - {len(total_novos_encontrados)} grupo(s) novo(s) processado(s)")

if __name__ == "__main__":
    main()
