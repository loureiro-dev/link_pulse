'use client';

import { useState, useEffect } from 'react';
import { runYoutubeDiscovery, addDiscoveredPage, getYoutubeConfig, YoutubeVideoResult } from '@/lib/api';
import { Youtube, CheckCircle, AlertCircle, Plus, ExternalLink, Loader2, Info, KeyRound, Settings } from 'lucide-react';
import Link from 'next/link';

export default function YoutubeSection() {
  const [configured, setConfigured] = useState(false);
  const [searching, setSearching] = useState(false);
  const [result, setResult] = useState<{ results: YoutubeVideoResult[]; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [maxResults, setMaxResults] = useState(10);
  const [autoAdd, setAutoAdd] = useState(false);
  const [addedUrls, setAddedUrls] = useState<Set<string>>(new Set());
  const [addingUrl, setAddingUrl] = useState<string | null>(null);

  useEffect(() => {
    getYoutubeConfig().then(c => setConfigured(c.configured)).catch(() => {});
  }, []);

  const handleSearch = async () => {
    setSearching(true);
    setError(null);
    setResult(null);
    setAddedUrls(new Set());
    try {
      const res = await runYoutubeDiscovery({ max_results_per_query: maxResults, auto_add_with_url: autoAdd });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Erro na busca');
    } finally {
      setSearching(false);
    }
  };

  const handleAdd = async (url: string, name: string) => {
    setAddingUrl(url);
    try {
      await addDiscoveredPage(url, name);
      setAddedUrls(prev => new Set(prev).add(url));
    } catch { } finally { setAddingUrl(null); }
  };

  if (!configured) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
          <KeyRound className="w-8 h-8 text-red-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Chave de API necessária</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center max-w-md">
          Para usar o módulo YouTube, configure sua chave da YouTube Data API v3 nas Configurações.
          É gratuita — 10.000 requisições/dia.
        </p>
        <Link href="/settings"
          className="flex items-center gap-2 px-5 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors">
          <Settings className="w-4 h-4" />Ir para Configurações
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <Info className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
        <p className="text-xs text-red-700 dark:text-red-300">
          Busca vídeos de lançamentos com <strong>6 termos pré-configurados</strong>.
          Extrai links de WhatsApp e landing pages das <strong>descrições completas</strong> dos vídeos.
          Quota gratuita: 10.000 unidades/dia (≈ 100 buscas).
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Vídeos por termo</label>
          <select value={maxResults} onChange={e => setMaxResults(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value={5}>5 vídeos (rápido)</option>
            <option value={10}>10 vídeos (recomendado)</option>
            <option value={25}>25 vídeos (completo)</option>
          </select>
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative">
              <input type="checkbox" checked={autoAdd} onChange={e => setAutoAdd(e.target.checked)} className="sr-only" />
              <div className={`w-11 h-6 rounded-full transition-colors ${autoAdd ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}`}>
                <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${autoAdd ? 'translate-x-5' : ''}`} />
              </div>
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">Adicionar 1ª URL automaticamente</span>
          </label>
        </div>
      </div>

      <button onClick={handleSearch} disabled={searching}
        className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
          searching ? 'bg-gray-400 cursor-not-allowed text-white'
          : 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-lg hover:scale-105 transform'}`}>
        {searching ? <><Loader2 className="w-5 h-5 animate-spin" />Buscando vídeos...</> : <><Youtube className="w-5 h-5" />Buscar no YouTube</>}
      </button>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {result && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-red-500" />
            <span className="font-semibold text-gray-900 dark:text-white">{result.message}</span>
          </div>
          {result.results.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Nenhum vídeo encontrado.</p>
          ) : (
            <div className="space-y-4">
              {result.results.map(video => (
                <div key={video.video_id} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                  <div className="flex gap-3 mb-3">
                    {video.thumbnail && <img src={video.thumbnail} alt="" className="w-24 h-16 object-cover rounded shrink-0" />}
                    <div className="flex-1 min-w-0">
                      <a href={video.video_url} target="_blank" rel="noopener noreferrer"
                        className="font-medium text-gray-900 dark:text-white text-sm hover:text-red-500 line-clamp-2">{video.title}</a>
                      <p className="text-xs text-gray-500 mt-1">{video.channel} · {video.published_at ? new Date(video.published_at).toLocaleDateString('pt-BR') : ''}</p>
                    </div>
                  </div>

                  {video.whatsapp_links.length > 0 && (
                    <div className="mb-2 flex flex-wrap gap-2">
                      {video.whatsapp_links.map(link => (
                        <a key={link} href={link} target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-1 px-2 py-1 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs rounded-full hover:bg-green-200 transition-colors">
                          <ExternalLink className="w-3 h-3" />WhatsApp direto
                        </a>
                      ))}
                    </div>
                  )}

                  {video.landing_urls.length > 0 && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Landing pages na descrição:</p>
                      {video.landing_urls.slice(0, 3).map(url => {
                        const isAdded = addedUrls.has(url);
                        const isAdding = addingUrl === url;
                        return (
                          <div key={url} className="flex items-center gap-2">
                            <a href={url} target="_blank" rel="noopener noreferrer"
                              className="text-xs text-blue-500 hover:underline flex items-center gap-1 flex-1 min-w-0 truncate">
                              <ExternalLink className="w-3 h-3 shrink-0" /><span className="truncate">{url}</span>
                            </a>
                            {isAdded ? (
                              <span className="text-xs text-gray-400 shrink-0">Adicionada</span>
                            ) : (
                              <button onClick={() => handleAdd(url, video.title)} disabled={isAdding}
                                className="flex items-center gap-1 px-2 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors disabled:opacity-50 shrink-0">
                                {isAdding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}Monitorar
                              </button>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {video.whatsapp_links.length === 0 && video.landing_urls.length === 0 && (
                    <p className="text-xs text-gray-400 italic">Sem links diretos — verifique a descrição do vídeo manualmente.</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
