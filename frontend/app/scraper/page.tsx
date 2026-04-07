'use client';

import { useState, useEffect } from 'react';
import {
  runScraper,
  getLastRun,
  ScraperResponse,
  runDiscovery,
  addDiscoveredPage,
  DiscoveryResponse,
  DiscoveredPage,
  getFacebookConfig,
  saveFacebookToken,
  validateFacebookToken,
  runFacebookDiscovery,
  FacebookDiscoveryResponse,
  FacebookAdResult,
} from '@/lib/api';
import {
  PlayCircle,
  CheckCircle,
  AlertCircle,
  Clock,
  Search,
  Plus,
  ExternalLink,
  Loader2,
  Info,
  Facebook,
  KeyRound,
  Eye,
  EyeOff,
  Zap,
} from 'lucide-react';

export default function ScraperPage() {
  // --- Scraper ---
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ScraperResponse | null>(null);
  const [lastRun, setLastRun] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  // --- DuckDuckGo Discovery ---
  const [discovering, setDiscovering] = useState(false);
  const [discoveryResult, setDiscoveryResult] = useState<DiscoveryResponse | null>(null);
  const [discoveryError, setDiscoveryError] = useState<string | null>(null);
  const [maxResults, setMaxResults] = useState(5);
  const [autoAdd, setAutoAdd] = useState(false);
  const [addedUrls, setAddedUrls] = useState<Set<string>>(new Set());
  const [addingUrl, setAddingUrl] = useState<string | null>(null);

  // --- Facebook Ad Library ---
  const [fbTokenInput, setFbTokenInput] = useState('');
  const [fbTokenConfigured, setFbTokenConfigured] = useState(false);
  const [fbTokenVisible, setFbTokenVisible] = useState(false);
  const [fbSaving, setFbSaving] = useState(false);
  const [fbValidating, setFbValidating] = useState(false);
  const [fbSearching, setFbSearching] = useState(false);
  const [fbResult, setFbResult] = useState<FacebookDiscoveryResponse | null>(null);
  const [fbError, setFbError] = useState<string | null>(null);
  const [fbMessage, setFbMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [fbLimitPerQuery, setFbLimitPerQuery] = useState(20);
  const [fbAutoAdd, setFbAutoAdd] = useState(false);
  const [fbAddedUrls, setFbAddedUrls] = useState<Set<string>>(new Set());
  const [fbAddingUrl, setFbAddingUrl] = useState<string | null>(null);

  const loadLastRun = async () => {
    try {
      const data = await getLastRun();
      setLastRun(data.last_run);
    } catch {
      // ignore
    }
  };

  const loadFbConfig = async () => {
    try {
      const data = await getFacebookConfig();
      setFbTokenConfigured(data.configured);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    loadLastRun();
    loadFbConfig();
  }, []);

  const handleRun = async () => {
    if (!confirm('Deseja executar o scraper agora? Isso pode levar alguns minutos.')) return;
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const response = await runScraper();
      setResult(response);
      loadLastRun();
    } catch (err: any) {
      setError(err.message || 'Erro ao executar scraper');
    } finally {
      setRunning(false);
    }
  };

  const handleDiscover = async () => {
    setDiscovering(true);
    setDiscoveryError(null);
    setDiscoveryResult(null);
    setAddedUrls(new Set());
    try {
      const response = await runDiscovery({
        max_results_per_query: maxResults,
        verify: true,
        only_with_whatsapp: true,
        auto_add: autoAdd,
      });
      setDiscoveryResult(response);
      if (autoAdd) {
        setAddedUrls(new Set(response.pages.filter((p) => p.added).map((p) => p.url)));
      }
    } catch (err: any) {
      setDiscoveryError(err.message || 'Erro na descoberta');
    } finally {
      setDiscovering(false);
    }
  };

  const handleAddPage = async (page: DiscoveredPage) => {
    setAddingUrl(page.url);
    try {
      await addDiscoveredPage(page.url, page.name);
      setAddedUrls((prev) => new Set(prev).add(page.url));
    } catch {
      // ignore
    } finally {
      setAddingUrl(null);
    }
  };

  const handleSaveFbToken = async () => {
    if (!fbTokenInput.trim()) return;
    setFbSaving(true);
    setFbMessage(null);
    try {
      await saveFacebookToken(fbTokenInput.trim());
      setFbTokenConfigured(true);
      setFbTokenInput('');
      setFbMessage({ type: 'success', text: 'Token salvo com sucesso!' });
    } catch (err: any) {
      setFbMessage({ type: 'error', text: err.message || 'Erro ao salvar token' });
    } finally {
      setFbSaving(false);
    }
  };

  const handleValidateFbToken = async () => {
    setFbValidating(true);
    setFbMessage(null);
    try {
      const res = await validateFacebookToken();
      setFbMessage({ type: 'success', text: res.message });
    } catch (err: any) {
      setFbMessage({ type: 'error', text: err.message || 'Token inválido ou sem permissão' });
    } finally {
      setFbValidating(false);
    }
  };

  const handleFbSearch = async () => {
    setFbSearching(true);
    setFbError(null);
    setFbResult(null);
    setFbAddedUrls(new Set());
    try {
      const res = await runFacebookDiscovery({
        limit_per_query: fbLimitPerQuery,
        auto_add_with_url: fbAutoAdd,
      });
      setFbResult(res);
      if (fbAutoAdd) {
        const added = new Set<string>();
        res.results.forEach((r) => r.added_urls.forEach((u) => added.add(u)));
        setFbAddedUrls(added);
      }
    } catch (err: any) {
      setFbError(err.message || 'Erro na busca');
    } finally {
      setFbSearching(false);
    }
  };

  const handleAddFbPage = async (url: string, name: string) => {
    setFbAddingUrl(url);
    try {
      await addDiscoveredPage(url, name);
      setFbAddedUrls((prev) => new Set(prev).add(url));
    } catch {
      // ignore
    } finally {
      setFbAddingUrl(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Coleta de Links</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Execute o scraper nas páginas cadastradas ou descubra novas páginas automaticamente
        </p>
      </div>

      {/* ─── SCRAPER MANUAL ─── */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-6">
            <PlayCircle className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Executar Coleta de Links
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Visita todas as páginas cadastradas e coleta links de grupos WhatsApp
          </p>
          <button
            onClick={handleRun}
            disabled={running}
            className={`px-8 py-4 rounded-lg font-semibold text-lg transition-all ${
              running
                ? 'bg-gray-400 cursor-not-allowed text-white'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-xl transform hover:scale-105'
            }`}
          >
            {running ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                Executando...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <PlayCircle className="w-5 h-5" />
                Iniciar Coleta
              </span>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
          <div>
            <p className="font-medium text-red-800 dark:text-red-200">Erro</p>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div
          className={`p-6 rounded-xl border ${
            result.success
              ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
          }`}
        >
          <div className="flex items-start gap-3 mb-4">
            {result.success ? (
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            ) : (
              <AlertCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            )}
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {result.success ? 'Coleta Concluída!' : 'Aviso'}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{result.message}</p>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Páginas Verificadas</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {result.total_checked}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Links Encontrados</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {result.links_found}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {lastRun && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Última Execução</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">{lastRun}</p>
            </div>
          </div>
        </div>
      )}

      {/* ─── DESCOBERTA AUTOMÁTICA ─── */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full">
            <Search className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Descoberta Automática de Páginas
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Busca no DuckDuckGo por páginas de lançamento com grupos WhatsApp
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2 p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-lg mb-6 mt-4">
          <Info className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mt-0.5 shrink-0" />
          <p className="text-xs text-emerald-700 dark:text-emerald-300">
            Usa 9 termos de busca pré-configurados focados em lançamentos brasileiros (Hotmart, Kiwify, etc.).
            Cada página encontrada é verificada automaticamente para confirmar a presença de links WhatsApp.
          </p>
        </div>

        {/* Configurações */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Resultados por termo de busca
            </label>
            <select
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value={3}>3 resultados (mais rápido)</option>
              <option value={5}>5 resultados (recomendado)</option>
              <option value={10}>10 resultados (mais completo)</option>
            </select>
          </div>

          <div className="flex items-end">
            <label className="flex items-center gap-3 cursor-pointer">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={autoAdd}
                  onChange={(e) => setAutoAdd(e.target.checked)}
                  className="sr-only"
                />
                <div
                  className={`w-11 h-6 rounded-full transition-colors ${
                    autoAdd ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                >
                  <div
                    className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      autoAdd ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </div>
              </div>
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Adicionar páginas automaticamente ao monitoramento
              </span>
            </label>
          </div>
        </div>

        <button
          onClick={handleDiscover}
          disabled={discovering}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            discovering
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-lg transform hover:scale-105'
          }`}
        >
          {discovering ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Buscando páginas... (pode levar 1-2 min)
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Search className="w-5 h-5" />
              Descobrir Páginas Agora
            </span>
          )}
        </button>

        {/* Erro da descoberta */}
        {discoveryError && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
            <div>
              <p className="font-medium text-red-800 dark:text-red-200">Erro na descoberta</p>
              <p className="text-sm text-red-700 dark:text-red-300">{discoveryError}</p>
            </div>
          </div>
        )}

        {/* Resultados da descoberta */}
        {discoveryResult && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                <span className="font-semibold text-gray-900 dark:text-white">
                  {discoveryResult.message}
                </span>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {discoveryResult.pages_found} página{discoveryResult.pages_found !== 1 ? 's' : ''}
              </span>
            </div>

            {discoveryResult.pages.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                Nenhuma página com grupos WhatsApp encontrada nesta busca.
                Tente aumentar os resultados por termo.
              </div>
            ) : (
              <div className="space-y-3">
                {discoveryResult.pages.map((page) => {
                  const isAdded = addedUrls.has(page.url);
                  const isAdding = addingUrl === page.url;
                  return (
                    <div
                      key={page.url}
                      className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 dark:text-white text-sm truncate">
                          {page.name}
                        </p>
                        <a
                          href={page.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-0.5 truncate"
                        >
                          <ExternalLink className="w-3 h-3 shrink-0" />
                          <span className="truncate">{page.url}</span>
                        </a>
                        {page.query && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            via: {page.query}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {page.has_whatsapp && (
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs rounded-full font-medium">
                            WhatsApp ✓
                          </span>
                        )}

                        {isAdded ? (
                          <span className="px-3 py-1.5 bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400 text-xs rounded-lg">
                            Adicionada
                          </span>
                        ) : (
                          <button
                            onClick={() => handleAddPage(page)}
                            disabled={isAdding}
                            className="flex items-center gap-1 px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white text-xs rounded-lg transition-colors disabled:opacity-50"
                          >
                            {isAdding ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <Plus className="w-3 h-3" />
                            )}
                            Monitorar
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
      {/* ─── META AD LIBRARY ─── */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-full">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              Meta Ad Library
              <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium">
                Lançamentos Ativos
              </span>
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Encontra anúncios rodando AGORA no Facebook/Instagram sobre lançamentos com grupos WhatsApp
            </p>
          </div>
        </div>

        <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg mb-6 mt-4">
          <Info className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 shrink-0" />
          <p className="text-xs text-blue-700 dark:text-blue-300">
            API oficial e gratuita do Meta. Retorna apenas anúncios <strong>ativos no Brasil</strong> — significa
            que o lançamento está acontecendo <strong>agora</strong>. Muito mais preciso que buscas no Google.
          </p>
        </div>

        {/* Config do token */}
        <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-5 mb-6 border border-gray-200 dark:border-gray-600">
          <div className="flex items-center gap-2 mb-3">
            <KeyRound className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            <h3 className="font-semibold text-gray-800 dark:text-gray-200 text-sm">
              Token de Acesso Meta
              {fbTokenConfigured && (
                <span className="ml-2 px-2 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs rounded-full">
                  Configurado
                </span>
              )}
            </h3>
          </div>

          <div className="text-xs text-gray-500 dark:text-gray-400 mb-3 space-y-1">
            <p>1. Acesse <a href="https://developers.facebook.com/tools/explorer/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">developers.facebook.com/tools/explorer</a></p>
            <p>2. Clique em <strong>Generate Access Token</strong> (não precisa de app review)</p>
            <p>3. Cole o token abaixo e salve</p>
          </div>

          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                type={fbTokenVisible ? 'text' : 'password'}
                value={fbTokenInput}
                onChange={(e) => setFbTokenInput(e.target.value)}
                placeholder={fbTokenConfigured ? 'Token já configurado — cole um novo para atualizar' : 'Cole seu token aqui...'}
                className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              />
              <button
                type="button"
                onClick={() => setFbTokenVisible(!fbTokenVisible)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {fbTokenVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <button
              onClick={handleSaveFbToken}
              disabled={fbSaving || !fbTokenInput.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors disabled:opacity-50 font-medium"
            >
              {fbSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Salvar'}
            </button>
            {fbTokenConfigured && (
              <button
                onClick={handleValidateFbToken}
                disabled={fbValidating}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 text-sm rounded-lg transition-colors disabled:opacity-50 font-medium"
              >
                {fbValidating ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Validar'}
              </button>
            )}
          </div>

          {fbMessage && (
            <div className={`mt-3 p-3 rounded-lg flex items-start gap-2 text-xs ${
              fbMessage.type === 'success'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300 border border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800'
            }`}>
              {fbMessage.type === 'success'
                ? <CheckCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                : <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />}
              {fbMessage.text}
            </div>
          )}
        </div>

        {/* Configurações de busca */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Anúncios por termo de busca
            </label>
            <select
              value={fbLimitPerQuery}
              onChange={(e) => setFbLimitPerQuery(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            >
              <option value={10}>10 anúncios (mais rápido)</option>
              <option value={20}>20 anúncios (recomendado)</option>
              <option value={50}>50 anúncios (mais completo)</option>
            </select>
          </div>

          <div className="flex items-end">
            <label className="flex items-center gap-3 cursor-pointer">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={fbAutoAdd}
                  onChange={(e) => setFbAutoAdd(e.target.checked)}
                  className="sr-only"
                />
                <div className={`w-11 h-6 rounded-full transition-colors ${fbAutoAdd ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}>
                  <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${fbAutoAdd ? 'translate-x-5' : 'translate-x-0'}`} />
                </div>
              </div>
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Adicionar páginas com URL automaticamente
              </span>
            </label>
          </div>
        </div>

        <button
          onClick={handleFbSearch}
          disabled={fbSearching || !fbTokenConfigured}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            !fbTokenConfigured
              ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
              : fbSearching
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:shadow-lg transform hover:scale-105'
          }`}
        >
          {fbSearching ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Buscando anúncios ativos...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              {fbTokenConfigured ? 'Buscar Lançamentos Ativos' : 'Configure o token para usar'}
            </span>
          )}
        </button>

        {/* Erro */}
        {fbError && (
          <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
            <div>
              <p className="font-medium text-red-800 dark:text-red-200">Erro na busca</p>
              <p className="text-sm text-red-700 dark:text-red-300">{fbError}</p>
            </div>
          </div>
        )}

        {/* Resultados */}
        {fbResult && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-gray-900 dark:text-white">{fbResult.message}</span>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {fbResult.ads_found} anúncio{fbResult.ads_found !== 1 ? 's' : ''}
              </span>
            </div>

            {fbResult.results.length === 0 ? (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                Nenhum anúncio ativo encontrado. Tente aumentar o limite ou verifique seu token.
              </div>
            ) : (
              <div className="space-y-3">
                {fbResult.results.map((ad) => (
                  <div
                    key={ad.ad_id}
                    className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 dark:text-white text-sm">
                          {ad.page_name || ad.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          Termo: {ad.search_term}
                          {ad.start_date && ` · Ativo desde: ${new Date(ad.start_date).toLocaleDateString('pt-BR')}`}
                        </p>
                      </div>
                      <div className="flex gap-2 shrink-0">
                        {ad.whatsapp_direct.length > 0 && (
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-400 text-xs rounded-full font-medium">
                            WhatsApp direto
                          </span>
                        )}
                        {ad.snapshot_url && (
                          <a
                            href={ad.snapshot_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 text-xs rounded-full hover:bg-blue-200 transition-colors"
                          >
                            <ExternalLink className="w-3 h-3" />
                            Ver anúncio
                          </a>
                        )}
                      </div>
                    </div>

                    {ad.ad_text && (
                      <p className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 p-2 rounded border border-gray-100 dark:border-gray-600 mb-2 line-clamp-2">
                        {ad.ad_text}
                      </p>
                    )}

                    {/* WhatsApp direto no anúncio */}
                    {ad.whatsapp_direct.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-2">
                        {ad.whatsapp_direct.map((link) => (
                          <a
                            key={link}
                            href={link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-green-600 dark:text-green-400 hover:underline flex items-center gap-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            {link.substring(0, 50)}...
                          </a>
                        ))}
                      </div>
                    )}

                    {/* Landing pages extraídas */}
                    {ad.landing_urls.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
                          Páginas de destino encontradas:
                        </p>
                        {ad.landing_urls.slice(0, 3).map((url) => {
                          const isAdded = fbAddedUrls.has(url);
                          const isAdding = fbAddingUrl === url;
                          return (
                            <div key={url} className="flex items-center gap-2">
                              <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-500 hover:underline flex items-center gap-1 flex-1 min-w-0 truncate"
                              >
                                <ExternalLink className="w-3 h-3 shrink-0" />
                                <span className="truncate">{url}</span>
                              </a>
                              {isAdded ? (
                                <span className="text-xs text-gray-400 shrink-0">Adicionada</span>
                              ) : (
                                <button
                                  onClick={() => handleAddFbPage(url, ad.page_name || ad.name)}
                                  disabled={isAdding}
                                  className="flex items-center gap-1 px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors disabled:opacity-50 shrink-0"
                                >
                                  {isAdding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}
                                  Monitorar
                                </button>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {ad.landing_urls.length === 0 && ad.whatsapp_direct.length === 0 && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 italic">
                        URL da página não extraída automaticamente — clique em &quot;Ver anúncio&quot; para verificar manualmente.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
