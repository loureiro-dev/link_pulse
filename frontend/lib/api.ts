// Usa variável de ambiente ou padrão localhost:8000
// Garante que sempre use a URL correta
const getApiBaseUrl = () => {
  // No Next.js, variáveis NEXT_PUBLIC_* são expostas no cliente
  // Tenta pegar da variável de ambiente primeiro
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  
  if (envUrl) {
    // Remove barra final se existir
    return envUrl.replace(/\/$/, '');
  }
  
  // Fallback: se estiver no servidor (SSR), usa localhost
  // Se estiver no cliente e não tiver variável, também usa localhost (desenvolvimento)
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  
  // No cliente, se não tiver variável configurada, mostra erro mais claro
  console.warn('NEXT_PUBLIC_API_URL não configurada. Usando localhost:8000');
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

export interface User {
  id: number;
  email: string;
  name?: string;
  is_admin: boolean;
  approved: boolean;
  created_at?: string;
}

export interface UpdateProfileData {
  name?: string;
  email?: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

// Import auth utilities to get token
import { getToken } from './auth';

// Função auxiliar para fazer requisições
async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`[API] Fazendo requisição: ${options.method || 'GET'} ${url}`);
  
  // Get token from cookie if available
  const token = getToken();
  const headers: Record<string, string> = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  // Add Authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      cache: 'no-store',
      mode: 'cors',
      headers,
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

// Profile API
export async function getMyProfile(): Promise<User> {
  return fetchApi('/api/profile/me');
}

export async function updateProfile(data: UpdateProfileData): Promise<User> {
  return fetchApi('/api/profile/me', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function changePassword(data: ChangePasswordData): Promise<{ message: string }> {
  return fetchApi('/api/profile/change-password', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ─── DISCOVERY: SHARED ────────────────────────────────────────────────────────

export async function addDiscoveredPage(url: string, name: string): Promise<{ success: boolean; message: string }> {
  return fetchApi('/api/discovery/add', { method: 'POST', body: JSON.stringify({ url, name }) });
}

// ─── DISCOVERY: DUCKDUCKGO ────────────────────────────────────────────────────

export interface DDGPage {
  url: string;
  name: string;
  has_whatsapp: boolean | null;
  verified: boolean;
  added: boolean;
  query: string | null;
}

export interface DDGResponse {
  success: boolean;
  pages_found: number;
  pages_added: number;
  pages: DDGPage[];
  message: string;
}

export async function runDuckDuckGoDiscovery(opts: {
  queries?: string[];
  max_results_per_query?: number;
  verify?: boolean;
  only_with_whatsapp?: boolean;
  auto_add?: boolean;
} = {}): Promise<DDGResponse> {
  return fetchApi('/api/discovery/duckduckgo', { method: 'POST', body: JSON.stringify(opts) });
}

export async function getDDGQueries(): Promise<{ queries: string[] }> {
  return fetchApi('/api/discovery/duckduckgo/queries');
}

// ─── DISCOVERY: YOUTUBE ───────────────────────────────────────────────────────

export interface YoutubeVideoResult {
  video_id: string;
  title: string;
  channel: string;
  published_at: string;
  description: string;
  thumbnail: string;
  video_url: string;
  query: string;
  whatsapp_links: string[];
  landing_urls: string[];
  added_urls: string[];
}

export interface YoutubeDiscoveryResponse {
  success: boolean;
  videos_found: number;
  pages_added: number;
  results: YoutubeVideoResult[];
  message: string;
}

export interface YoutubeConfig {
  api_key: string;
  configured: boolean;
}

export async function getYoutubeConfig(): Promise<YoutubeConfig> {
  return fetchApi('/api/youtube/config');
}

export async function saveYoutubeApiKey(api_key: string): Promise<{ success: boolean; message: string }> {
  return fetchApi('/api/youtube/save', { method: 'POST', body: JSON.stringify({ api_key }) });
}

export async function validateYoutubeKey(): Promise<{ success: boolean; message: string }> {
  return fetchApi('/api/youtube/validate', { method: 'POST' });
}

export async function runYoutubeDiscovery(opts: {
  queries?: string[];
  max_results_per_query?: number;
  auto_add_with_url?: boolean;
} = {}): Promise<YoutubeDiscoveryResponse> {
  return fetchApi('/api/discovery/youtube', { method: 'POST', body: JSON.stringify(opts) });
}

export async function getYoutubeQueries(): Promise<{ queries: string[] }> {
  return fetchApi('/api/discovery/youtube/queries');
}

// ─── DISCOVERY: TELEGRAM CHANNELS ────────────────────────────────────────────

export interface TelegramPost {
  channel: string;
  channel_title: string;
  text: string;
  date: string;
  message_url: string;
  whatsapp_links: string[];
  landing_urls: string[];
}

export interface TelegramChannelResult {
  channel: string;
  success: boolean;
  posts_found: number;
  posts: TelegramPost[];
  error: string | null;
  pages_added: number;
}

export interface TelegramDiscoveryResponse {
  success: boolean;
  channels_scanned: number;
  total_posts: number;
  total_whatsapp_links: number;
  results: TelegramChannelResult[];
  message: string;
}

export async function runTelegramDiscovery(opts: {
  channels: string[];
  limit_per_channel?: number;
  only_with_links?: boolean;
  auto_add?: boolean;
}): Promise<TelegramDiscoveryResponse> {
  return fetchApi('/api/discovery/telegram', { method: 'POST', body: JSON.stringify(opts) });
}

// ─── YOUTUBE SETTINGS ─────────────────────────────────────────────────────────

// Admin API
export async function getAllUsers(includePending: boolean = true): Promise<User[]> {
  return fetchApi(`/api/admin/users?include_pending=${includePending}`);
}

export async function getPendingUsers(): Promise<User[]> {
  return fetchApi('/api/admin/users/pending');
}

export async function approveUser(userId: number): Promise<User> {
  return fetchApi(`/api/admin/users/${userId}/approve`, {
    method: 'POST',
  });
}

export async function rejectUser(userId: number): Promise<{ message: string }> {
  return fetchApi(`/api/admin/users/${userId}/reject`, {
    method: 'DELETE',
  });
}
