'use client';

import { useState, useEffect } from 'react';
import { getLinks, getStats, Link, Stats } from '@/lib/api';
import StatsCard from '@/components/StatsCard';
import LinksTable from '@/components/LinksTable';
import ChartsSection from '@/components/ChartsSection';
import { Link as LinkIcon, Users, FileText, Activity, TrendingUp, Shield } from 'lucide-react';
import { getCurrentUser } from '@/lib/auth';
import NextLink from 'next/link';

export default function DashboardPage() {
  const [links, setLinks] = useState<Link[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<{ is_admin?: boolean } | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [linksData, statsData] = await Promise.all([
        getLinks(1000).catch((err) => {
          console.error('Erro ao buscar links:', err);
          return [];
        }),
        getStats().catch((err) => {
          console.error('Erro ao buscar stats:', err);
          // Retorna stats padrão se falhar
          return {
            total_links: 0,
            unique_links: 0,
            campaigns: 0,
            total_pages: 0,
            last_run: 'Erro ao carregar'
          };
        }),
      ]);
      
      setLinks(linksData);
      setStats(statsData);
    } catch (err: any) {
      console.error('Erro ao carregar dados:', err);
      setError(err.message || 'Erro ao carregar dados. Verifique se o backend está rodando na porta 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Load current user to check if admin
    getCurrentUser().then(user => {
      if (user) {
        setCurrentUser(user);
      }
    });
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Visão geral do sistema de monitoramento
          </p>
        </div>
        {currentUser?.is_admin && (
          <NextLink
            href="/admin"
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors shadow-md"
          >
            <Shield className="w-5 h-5" />
            <span>Painel de Administração</span>
          </NextLink>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-800 dark:text-red-200 font-medium">Erro: {error}</p>
          <button
            onClick={loadData}
            className="mt-2 text-sm text-red-600 dark:text-red-400 hover:underline"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatsCard
            title="Total de Links"
            value={stats.total_links}
            icon={<LinkIcon className="w-6 h-6" />}
            gradient="primary"
          />
          <StatsCard
            title="Links Únicos"
            value={stats.unique_links}
            icon={<LinkIcon className="w-6 h-6" />}
            gradient="info"
          />
          <StatsCard
            title="Campanhas"
            value={stats.campaigns}
            icon={<Users className="w-6 h-6" />}
            gradient="success"
          />
          <StatsCard
            title="Páginas Monitoradas"
            value={stats.total_pages}
            icon={<FileText className="w-6 h-6" />}
            gradient="warning"
          />
        </div>
      )}

      {/* Charts */}
      {links.length > 0 && <ChartsSection links={links} />}

      {/* Recent Links */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Links Coletados Recentes
          </h2>
          <button
            onClick={loadData}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Atualizar
          </button>
        </div>
        <LinksTable links={links.slice(0, 50)} />
      </div>
    </div>
  );
}

