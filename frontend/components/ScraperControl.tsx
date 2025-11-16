'use client';

import { useState, useEffect } from 'react';
import { runScraper, getLastRun, ScraperResponse } from '@/lib/api';

export default function ScraperControl() {
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
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Controle do Scraper
        </h2>
      </div>
      <div className="p-6 space-y-4">
        <button
          onClick={handleRun}
          disabled={running}
          className={`w-full px-4 py-3 rounded-md font-medium transition ${
            running
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {running ? 'Executando...' : '🚀 Executar Scraper Agora'}
        </button>

        {error && (
          <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded">
            {error}
          </div>
        )}

        {result && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded">
            <p className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              {result.success ? '✅ Sucesso!' : '⚠️ Aviso'}
            </p>
            <p className="text-sm text-blue-800 dark:text-blue-200 mb-1">
              {result.message}
            </p>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              Páginas verificadas: {result.total_checked} | Links encontrados: {result.links_found}
            </p>
          </div>
        )}

        {lastRun && (
          <div className="p-3 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Última execução:
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">{lastRun}</p>
          </div>
        )}
      </div>
    </div>
  );
}

