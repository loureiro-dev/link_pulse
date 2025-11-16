// Usa variável de ambiente ou padrão localhost:8000
// Garante que sempre use a URL correta
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  
  // Tenta pegar da variável de ambiente, senão usa o padrão
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl) {
    return envUrl;
  }
  
  // Fallback para localhost:8000
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface Link {
  url: string;
  source: string;
  found_at: string;
}

export interface Page {
  url: string;
  name: string;
}

export interface Stats {
  total_links: number;
  unique_links: number;
  campaigns: number;
  total_pages: number;
  last_run: string;
}

export interface ScraperResponse {
  success: boolean;
  total_checked: number;
  links_found: number;
  links: Link[];
  message: string;
}

export interface TelegramConfig {
  bot_token: string;
  chat_id: string;
  configured: boolean;
}

// Função auxiliar para fazer requisições
async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`[API] Fazendo requisição: ${options.method || 'GET'} ${url}`);
  
  try {
    const response = await fetch(url, {
      ...options,
      cache: 'no-store',
      mode: 'cors',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    console.log(`[API] Resposta: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] Erro na resposta:`, errorText);
      throw new Error(`Erro ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`[API] Dados recebidos:`, data);
    return data;
  } catch (error: any) {
    console.error(`[API] Erro na requisição:`, error);
    
    // Verifica se é erro de conexão
    if (
      error.message?.includes('fetch') ||
      error.name === 'TypeError' ||
      error.message?.includes('Failed to fetch') ||
      error.message?.includes('NetworkError') ||
      error.message?.includes('Network request failed')
    ) {
      throw new Error('Não foi possível conectar ao backend. Verifique se o servidor está rodando na porta 8000.');
    }
    
    throw error;
  }
}

// API Functions
export async function getLinks(limit: number = 1000): Promise<Link[]> {
  return fetchApi(`/api/links?limit=${limit}`);
}

export async function getPages(): Promise<Page[]> {
  return fetchApi('/api/pages');
}

export async function createPage(page: Omit<Page, 'url'> & { url: string }): Promise<Page> {
  return fetchApi('/api/pages', {
    method: 'POST',
    body: JSON.stringify(page),
  });
}

export async function deletePage(url: string): Promise<void> {
  await fetchApi(`/api/pages?url=${encodeURIComponent(url)}`, {
    method: 'DELETE',
  });
}

export async function runScraper(): Promise<ScraperResponse> {
  return fetchApi('/api/scraper/run', {
    method: 'POST',
  });
}

export async function getLastRun(): Promise<{ last_run: string }> {
  return fetchApi('/api/scraper/last-run');
}

export async function getStats(): Promise<Stats> {
  return fetchApi('/api/stats');
}

export async function getTelegramConfig(): Promise<TelegramConfig> {
  return fetchApi('/api/telegram/config');
}

export async function saveTelegramConfig(config: { bot_token: string; chat_id: string }): Promise<void> {
  await fetchApi('/api/telegram/save', {
    method: 'POST',
    body: JSON.stringify(config),
  });
}

export async function testTelegram(): Promise<{ success: boolean; message: string }> {
  return fetchApi('/api/telegram/test', {
    method: 'POST',
  });
}
