'use client';

import { useState } from 'react';
import { runDuckDuckGoDiscovery, addDiscoveredPage, DDGPage } from '@/lib/api';
import { Search, CheckCircle, AlertCircle, Plus, ExternalLink, Loader2, Info } from 'lucide-react';

export default function DuckDuckGoSection() {
  const [searching, setSearching] = useState(false);
  const [result, setResult] = useState<{ pages: DDGPage[]; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [maxResults, setMaxResults] = useState(5);
  const [autoAdd, setAutoAdd] = useState(false);
  const [addedUrls, setAddedUrls] = useState<Set<string>>(new Set());
  const [addingUrl, setAddingUrl] = useState<string | null>(null);

  const handleSearch = async () => {
    setSearching(true);
    setError(null);
    setResult(null);
    setAddedUrls(new Set());
    try {
      const res = await runDuckDuckGoDiscovery({ max_results_per_query: maxResults, verify: true, only_with_whatsapp: true, auto_add: autoAdd });
      setResult(res);
      if (autoAdd) setAddedUrls(new Set(res.pages.filter(p => p.added).map(p => p.url)));
    } catch (err: any) {
      setError(err.message || 'Erro na busca');
    } finally {
      setSearching(false);
    }
  };

  const handleAdd = async (page: DDGPage) => {
    setAddingUrl(page.url);
    try {
      await addDiscoveredPage(page.url, page.name);
      setAddedUrls(prev => new Set(prev).add(page.url));
    } catch { } finally { setAddingUrl(null); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-2 p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg">
        <Info className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
        <p className="text-xs text-emerald-700 dark:text-emerald-300">
          Busca gratuita com <strong>9 termos pré-configurados</strong> focados em lançamentos brasileiros.
          Cada página é verificada automaticamente para confirmar a presença de links WhatsApp.
          Não requer chave de API.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Resultados por termo</label>
          <select value={maxResults} onChange={e => setMaxResults(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value={3}>3 resultados (rápido)</option>
            <option value={5}>5 resultados (recomendado)</option>
            <option value={10}>10 resultados (completo)</option>
          </select>
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-3 cursor-pointer">
            <div className="relative">
              <input type="checkbox" checked={autoAdd} onChange={e => setAutoAdd(e.target.checked)} className="sr-only" />
              <div className={`w-11 h-6 rounded-full transition-colors ${autoAdd ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'}`}>
                <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${autoAdd ? 'translate-x-5' : ''}`} />
              </div>
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">Adicionar automaticamente</span>
          </label>
        </div>
      </div>

      <button onClick={handleSearch} disabled={searching}
        className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
          searching ? 'bg-gray-400 cursor-not-allowed text-white'
          : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg hover:scale-105 transform'}`}>
        {searching ? <><Loader2 className="w-5 h-5 animate-spin" />Buscando... (1-2 min)</> : <><Search className="w-5 h-5" />Buscar Páginas</>}
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
            <CheckCircle className="w-5 h-5 text-emerald-500" />
            <span className="font-semibold text-gray-900 dark:text-white">{result.message}</span>
          </div>
          {result.pages.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Nenhuma página com grupos WhatsApp encontrada. Tente aumentar os resultados.</p>
          ) : (
            <div className="space-y-3">
              {result.pages.map(page => {
                const isAdded = addedUrls.has(page.url);
                const isAdding = addingUrl === page.url;
                return (
                  <div key={page.url} className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white text-sm truncate">{page.name}</p>
                      <a href={page.url} target="_blank" rel="noopener noreferrer"
                        className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-0.5 truncate">
                        <ExternalLink className="w-3 h-3 shrink-0" /><span className="truncate">{page.url}</span>
                      </a>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {page.has_whatsapp && <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs rounded-full">WhatsApp ✓</span>}
                      {isAdded ? (
                        <span className="px-3 py-1.5 bg-gray-200 dark:bg-gray-600 text-gray-500 text-xs rounded-lg">Adicionada</span>
                      ) : (
                        <button onClick={() => handleAdd(page)} disabled={isAdding}
                          className="flex items-center gap-1 px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white text-xs rounded-lg transition-colors disabled:opacity-50">
                          {isAdding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}Monitorar
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
