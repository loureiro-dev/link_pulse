const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

// API Functions
export async function getLinks(limit: number = 1000): Promise<Link[]> {
  const response = await fetch(`${API_BASE_URL}/api/links?limit=${limit}`);
  if (!response.ok) throw new Error('Erro ao buscar links');
  return response.json();
}

export async function getPages(): Promise<Page[]> {
  const response = await fetch(`${API_BASE_URL}/api/pages`);
  if (!response.ok) throw new Error('Erro ao buscar páginas');
  return response.json();
}

export async function createPage(page: Omit<Page, 'url'> & { url: string }): Promise<Page> {
  const response = await fetch(`${API_BASE_URL}/api/pages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(page),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao criar página');
  }
  return response.json();
}

export async function deletePage(url: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/pages?url=${encodeURIComponent(url)}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Erro ao excluir página');
}

export async function runScraper(): Promise<ScraperResponse> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/run`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Erro ao executar scraper');
  return response.json();
}

export async function getLastRun(): Promise<{ last_run: string }> {
  const response = await fetch(`${API_BASE_URL}/api/scraper/last-run`);
  if (!response.ok) throw new Error('Erro ao buscar última execução');
  return response.json();
}

export async function getStats(): Promise<Stats> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);
  if (!response.ok) throw new Error('Erro ao buscar estatísticas');
  return response.json();
}

export async function getTelegramConfig(): Promise<TelegramConfig> {
  const response = await fetch(`${API_BASE_URL}/api/telegram/config`);
  if (!response.ok) throw new Error('Erro ao buscar configuração do Telegram');
  return response.json();
}

export async function saveTelegramConfig(config: { bot_token: string; chat_id: string }): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/telegram/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error('Erro ao salvar configuração');
}

export async function testTelegram(): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/telegram/test`, {
    method: 'POST',
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao testar Telegram');
  }
  return response.json();
}

