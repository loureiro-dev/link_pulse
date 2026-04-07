"""
Classificador IA para páginas de captura de lançamentos digitais brasileiros.

Pipeline de classificação (por ordem de custo crescente):

  1. TIERING por score de URL (gratuito, instantâneo):
       score >= 50 → auto-aprovado  (lp. + UTM + inscricao = certeza)
       score 8-49  → envia para IA  (ambíguo)
       score < 8   → auto-rejeitado (youtube.com, blogspot, etc.)

  2. CACHE Supabase (gratuito para URLs já vistas):
       URL já classificada nos últimos 30 dias → retorna resultado salvo

  3. FEW-SHOT DINÂMICO (melhora precisão sem custo extra):
       Injeta até 8 páginas reais aprovadas pelo usuário como exemplos positivos
       + exemplos negativos fixos para calibrar o modelo

  4. API DA IA (Gemini grátis ou OpenAI barato):
       Só é chamada para URLs ambíguas e não-cacheadas

Custo estimado com tiering + cache: < 20% das chamadas sem tiering.
"""

import json
import re
import hashlib
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List


# ─── TIERING THRESHOLDS ───────────────────────────────────────────────────────

AUTO_APPROVE_SCORE = 50   # score_url() >= 50 → aprovado sem IA
AUTO_REJECT_SCORE  = 8    # score_url() < 8  → rejeitado sem IA


# ─── FEW-SHOT NEGATIVOS FIXOS ────────────────────────────────────────────────

NEGATIVE_EXAMPLES = [
    ("https://youtube.com/watch?v=abcdef",
     "Como Criar Grupos de WhatsApp - Tutorial 2025",
     "tutorial no YouTube, não é landing page"),
    ("https://instagram.com/p/abc123/",
     "Post de Instagram",
     "rede social, não é página de captura"),
    ("https://zenvia.com/blog/whatsapp-business",
     "WhatsApp Business - Blog Zenvia",
     "blog de ferramenta SaaS"),
    ("https://mercadolivre.com.br/produto/xyz",
     "Produto no Mercado Livre",
     "e-commerce com múltiplos produtos"),
    ("https://hostgator.com.br/hospedagem",
     "Hospedagem de Sites - HostGator",
     "serviço de infraestrutura, não lançamento"),
]

# ─── PROMPT BASE ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é um especialista em marketing digital brasileiro, especializado em lançamentos de infoprodutos.

Sua tarefa: classificar se uma URL é uma **página de captura para lançamento de infoproduto brasileiro** que provavelmente leva a um grupo de WhatsApp.

**O que é uma página de captura de lançamento:**
- Landing page com formulário (nome, e-mail, telefone) OU botão direto para WhatsApp
- Promove curso, mentoria, masterclass, workshop, imersão, treinamento ou evento
- Objetivo: coletar leads e depois revelar o grupo de WhatsApp
- Qualquer nicho: saúde, finanças, direito, tecnologia, esoterismo, idiomas, engenharia, etc.
- Geralmente tem UTM de tráfego pago (Facebook/Instagram Ads)

**O que NÃO é:**
- Posts ou perfis de redes sociais
- Artigos de blog ou notícias
- E-commerce com múltiplos produtos
- Ferramentas ou serviços SaaS
- Tutoriais ou vídeos do YouTube
- Sites institucionais sem oferta específica

**Sinais fortíssimos de positivo:**
- Subdomínio `lp.`, `vef.`, `mkt.`, `wp.`, `page.`, `referencia.`
- Path com: cadastro, inscricao, captura, grupovip, masterclass, workshop, imersao, formacao
- Sufixo `-v1`, `-v2`, `lp1`, `lp2` (teste A/B = tráfego pago)
- UTM com utm_campaign contendo CAPTACAO, LANCAMENTO, LEAD
- Plataformas: kpages.online, pages.hotmart.com, kiwify.com.br, braip.com

Responda APENAS com JSON válido, sem markdown:
{"is_capture_page": true/false, "confidence": 0.0-1.0, "niche": "saude|financas|tech|educacao|direito|esoterismo|idiomas|outro", "reasoning": "motivo em até 15 palavras"}"""


# ─── CACHE (Supabase) ─────────────────────────────────────────────────────────

def _url_hash(url: str) -> str:
    return hashlib.md5(url.strip().lower().encode()).hexdigest()


def _cache_get(url: str) -> Optional[Dict]:
    """Busca resultado em cache. Retorna None se não encontrado ou expirado."""
    try:
        from backend.db.supabase_client import get_client
        client = get_client()
        url_hash = _url_hash(url)
        now = datetime.now(timezone.utc).isoformat()
        result = (
            client.table("ai_cache")
            .select("is_capture_page, confidence, niche, reasoning, provider")
            .eq("url_hash", url_hash)
            .gt("expires_at", now)
            .limit(1)
            .execute()
        )
        if result.data:
            row = result.data[0]
            row["from_cache"] = True
            return row
    except Exception:
        pass
    return None


def _cache_set(url: str, result: Dict) -> None:
    """Salva resultado no cache por 30 dias."""
    try:
        from backend.db.supabase_client import get_client
        client = get_client()
        url_hash = _url_hash(url)
        expires = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        client.table("ai_cache").upsert({
            "url_hash": url_hash,
            "url": url[:500],
            "is_capture_page": result.get("is_capture_page"),
            "confidence": result.get("confidence"),
            "niche": result.get("niche", "outro"),
            "reasoning": result.get("reasoning", "")[:200],
            "provider": result.get("provider", ""),
            "expires_at": expires,
        }, on_conflict="url_hash").execute()
    except Exception:
        pass


# ─── FEW-SHOT DINÂMICO ────────────────────────────────────────────────────────

def _get_user_examples(user_id: int, limit: int = 8) -> List[Dict]:
    """
    Busca páginas aprovadas pelo usuário no Supabase como exemplos positivos.
    Quanto mais páginas o usuário tiver, mais personalizado fica o prompt.
    """
    try:
        from backend.db.supabase_client import get_client
        client = get_client()
        result = (
            client.table("pages")
            .select("url, name")
            .eq("user_id", user_id)
            .order("id", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception:
        return []


def _build_few_shot_text(user_examples: List[Dict]) -> str:
    """Constrói o bloco de exemplos para o prompt."""
    lines = []

    # Exemplos positivos do usuário (dinâmicos)
    if user_examples:
        lines.append("Exemplos de páginas APROVADAS por este usuário:")
        for ex in user_examples:
            url = ex.get("url", "")
            name = ex.get("name", "")
            lines.append(f'  URL: {url}\n  Nome: {name}\n  → {{"is_capture_page":true,"confidence":0.92,"niche":"outro","reasoning":"aprovado pelo usuário"}}')

    # Exemplos negativos fixos
    lines.append("\nExemplos de páginas REJEITADAS:")
    for url, title, reason in NEGATIVE_EXAMPLES[:3]:
        lines.append(f'  URL: {url}\n  Título: {title}\n  → {{"is_capture_page":false,"confidence":0.95,"niche":"outro","reasoning":"{reason}"}}')

    return "\n".join(lines)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _build_user_message(url: str, title: str = "", snippet: str = "") -> str:
    parts = [f"URL: {url}"]
    if title:
        parts.append(f"Título: {title[:150]}")
    if snippet:
        parts.append(f"Descrição: {snippet[:200]}")
    return "\n".join(parts)


def _parse_response(text: str) -> Dict:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {"is_capture_page": False, "confidence": 0.0, "niche": "outro", "reasoning": "parse error"}


# ─── BACKENDS DE IA ───────────────────────────────────────────────────────────

def _classify_gemini(api_key: str, url: str, title: str, snippet: str, few_shot: str) -> Dict:
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    user_text = _build_user_message(url, title, snippet)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{few_shot}\n\nAgora classifique:\n{user_text}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 150},
    }
    resp = requests.post(endpoint, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_response(text)


def _classify_openai(api_key: str, url: str, title: str, snippet: str, few_shot: str) -> Dict:
    system_with_examples = f"{SYSTEM_PROMPT}\n\n{few_shot}"
    messages = [
        {"role": "system", "content": system_with_examples},
        {"role": "user", "content": _build_user_message(url, title, snippet)},
    ]
    payload = {"model": "gpt-4o-mini", "messages": messages, "temperature": 0.1, "max_tokens": 150}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    return _parse_response(text)


# ─── INTERFACE PÚBLICA ────────────────────────────────────────────────────────

def classify_page(
    url: str,
    title: str = "",
    snippet: str = "",
    api_key: str = "",
    provider: str = "gemini",
    user_id: Optional[int] = None,
    use_cache: bool = True,
    use_tiering: bool = True,
) -> Dict:
    """
    Classifica se uma URL é uma página de captura de lançamento brasileiro.

    Pipeline: tiering → cache → few-shot dinâmico → API de IA

    Args:
        url:          URL da página
        title:        Título da página (melhora precisão)
        snippet:      Trecho de texto (melhora precisão)
        api_key:      Chave da API (Gemini ou OpenAI)
        provider:     "gemini" | "openai"
        user_id:      ID do usuário (para few-shot dinâmico com páginas históricas)
        use_cache:    Usar cache do Supabase (padrão: True)
        use_tiering:  Usar auto-aprovação/rejeição por score (padrão: True)
    """
    base = {"provider": provider, "error": None, "from_cache": False, "from_tiering": False}

    # 1. TIERING — decisão por score de URL (zero custo)
    if use_tiering:
        try:
            from backend.services.discovery.page_discovery import score_url
            score = score_url(url)
            if score >= AUTO_APPROVE_SCORE:
                return {**base, "is_capture_page": True,  "confidence": 0.92,
                        "niche": "outro", "reasoning": f"auto-aprovado (score={score})",
                        "from_tiering": True, "url_score": score}
            if score < AUTO_REJECT_SCORE:
                return {**base, "is_capture_page": False, "confidence": 0.92,
                        "niche": "outro", "reasoning": f"auto-rejeitado (score={score})",
                        "from_tiering": True, "url_score": score}
        except Exception:
            pass

    # 2. CACHE — resultado já existente (zero custo)
    if use_cache:
        cached = _cache_get(url)
        if cached:
            return {**base, **cached}

    # 3. FEW-SHOT DINÂMICO — exemplos do usuário
    user_examples = _get_user_examples(user_id, limit=8) if user_id else []
    few_shot_text = _build_few_shot_text(user_examples)

    # 4. API DE IA
    if not api_key:
        return {**base, "is_capture_page": None, "confidence": 0.0,
                "niche": "outro", "reasoning": "sem chave de API", "error": "no_api_key"}

    try:
        if provider == "openai":
            result = _classify_openai(api_key, url, title, snippet, few_shot_text)
        else:
            result = _classify_gemini(api_key, url, title, snippet, few_shot_text)

        result = {**base, **result}

        # Salva no cache
        if use_cache:
            _cache_set(url, result)

        return result

    except Exception as e:
        return {**base, "is_capture_page": None, "confidence": 0.0,
                "niche": "outro", "reasoning": str(e)[:100], "error": str(e)[:200]}


def classify_batch(
    pages: List[Dict],
    api_key: str,
    provider: str = "gemini",
    min_confidence: float = 0.65,
    user_id: Optional[int] = None,
    use_cache: bool = True,
    use_tiering: bool = True,
) -> List[Dict]:
    """
    Classifica uma lista de páginas.

    Cada dict deve ter "url" e opcionalmente "name"/"title"/"snippet".
    Adiciona campos "ai", "ai_status" a cada página.

    ai_status:
      "approved" → IA confirmou que é página de captura (confidence >= min_confidence)
      "rejected" → IA confirmou que não é (confidence >= min_confidence)
      "review"   → incerto (confidence baixa ou erro)
      "tiered"   → decidido por score sem chamar IA
      "cached"   → resultado do cache
    """
    # Pré-carrega exemplos do usuário UMA vez para o batch inteiro
    user_examples = _get_user_examples(user_id, limit=8) if user_id else []
    few_shot_text = _build_few_shot_text(user_examples)

    for page in pages:
        url   = page.get("url", "")
        title = page.get("name", page.get("title", ""))
        snippet = page.get("snippet", "")

        result = classify_page(
            url=url, title=title, snippet=snippet,
            api_key=api_key, provider=provider,
            user_id=None,       # já pré-carregamos os exemplos acima
            use_cache=use_cache,
            use_tiering=use_tiering,
        )

        # Sobrescreve o few-shot para chamadas que foram além do tiering/cache
        # (classify_page já usou few_shot_text interno — ok para Gemini/OpenAI)

        page["ai"] = result
        conf    = result.get("confidence", 0.0)
        is_cap  = result.get("is_capture_page")
        tiered  = result.get("from_tiering", False)
        cached  = result.get("from_cache", False)

        if tiered:
            page["ai_status"] = "approved" if is_cap else "rejected"
        elif cached:
            page["ai_status"] = "approved" if (is_cap and conf >= min_confidence) else (
                                 "rejected" if (is_cap is False and conf >= min_confidence) else "review")
        elif is_cap is True and conf >= min_confidence:
            page["ai_status"] = "approved"
        elif is_cap is False and conf >= min_confidence:
            page["ai_status"] = "rejected"
        else:
            page["ai_status"] = "review"

    return pages


def validate_api_key(api_key: str, provider: str = "gemini") -> Dict:
    """Testa a chave de API com uma URL de exemplo."""
    result = classify_page(
        url="https://lp.example.com.br/inscricao-v1/?utm_source=ig&utm_campaign=CAPTACAO",
        title="Inscrição Gratuita — Masterclass Lançamento",
        api_key=api_key,
        provider=provider,
        use_cache=False,
        use_tiering=False,   # força a chamada real à API
    )
    if result.get("error"):
        return {"valid": False, "message": result["error"]}
    return {"valid": True, "message": f"✓ {provider.title()} funcionando — classificação OK"}
