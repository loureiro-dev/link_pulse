'use client';

import { useState, useEffect } from 'react';
import { getLinks, getStats, Link, Stats } from '@/lib/api';
import StatsCard from '@/components/StatsCard';
import LinksTable from '@/components/LinksTable';
import PagesManager from '@/components/PagesManager';
import ScraperControl from '@/components/ScraperControl';
import TelegramConfig from '@/components/TelegramConfig';
import { Link as LinkIcon, Users, FileText, Activity } from 'lucide-react';

export default function Home() {
  const [links, setLinks] = useState<Link[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [linksData, statsData] = await Promise.all([
        getLinks(1000),
        getStats(),
      ]);
      setLinks(linksData);
      setStats(statsData);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Recarrega dados a cada 30 segundos
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            LinkPulse Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitoramento e coleta de links de grupos WhatsApp
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg">
            <p className="font-medium">Erro: {error}</p>
            <button
              onClick={loadData}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Total de Links"
              value={stats.total_links}
              icon={<LinkIcon className="w-8 h-8" />}
            />
            <StatsCard
              title="Links Únicos"
              value={stats.unique_links}
              icon={<LinkIcon className="w-8 h-8" />}
            />
            <StatsCard
              title="Campanhas"
              value={stats.campaigns}
              icon={<Users className="w-8 h-8" />}
            />
            <StatsCard
              title="Páginas Monitoradas"
              value={stats.total_pages}
              icon={<FileText className="w-8 h-8" />}
            />
          </div>
        )}

        {/* Controls Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ScraperControl />
          <TelegramConfig />
        </div>

        {/* Pages Manager */}
        <div className="mb-8">
          <PagesManager />
        </div>

        {/* Links Table */}
        <div className="mb-8">
          <LinksTable links={links} />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            LinkPulse v1.0.0 - Sistema de monitoramento de links WhatsApp
          </p>
        </div>
      </footer>
    </div>
  );
}

