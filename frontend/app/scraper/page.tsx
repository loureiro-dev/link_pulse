'use client';

import { useState, useEffect } from 'react';
import { runScraper, getLastRun, ScraperResponse } from '@/lib/api';
import { PlayCircle, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export default function ScraperPage() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ScraperResponse | null>(null);
  const [lastRun, setLastRun] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const loadLastRun = async () => {
    try {
      const data = await getLastRun();
      setLastRun(data.last_run);
    } catch (err) {
      // Ignore errors
    }
  };

  useEffect(() => {
    loadLastRun();
  }, []);

  const handleRun = async () => {
    if (!confirm('Deseja executar o scraper agora? Isso pode levar alguns minutos.')) {
      return;
    }

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Rodar Coleta</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Execute o scraper para coletar links de todas as páginas cadastradas
        </p>
      </div>

      {/* Main Action Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-6">
            <PlayCircle className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Executar Coleta de Links
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            O scraper irá visitar todas as páginas cadastradas e coletar links de grupos WhatsApp
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
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
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

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
          <div>
            <p className="font-medium text-red-800 dark:text-red-200">Erro</p>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className={`p-6 rounded-xl border ${
          result.success
            ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
            : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
        }`}>
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
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{result.total_checked}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Links Encontrados</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{result.links_found}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Last Run */}
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
    </div>
  );
}

