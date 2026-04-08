'use client';

import { Link, deleteLink, deleteAllLinks } from '@/lib/api';
import { useState } from 'react';
import { Copy, ExternalLink, Filter, Trash2, RefreshCw, Users, ShieldAlert } from 'lucide-react';

interface LinksTableProps {
  links: Link[];
  onRefresh?: () => void;
}

export default function LinksTable({ links, onRefresh }: LinksTableProps) {
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
  const [filterSource, setFilterSource] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const handleDelete = async (url: string) => {
    if (!confirm('Você tem certeza que deseja apagar este link?')) return;
    try {
      await deleteLink(url);
      if (onRefresh) onRefresh();
    } catch (e: any) {
      alert(e.message || 'Erro ao deletar o link.');
    }
  };

  const handleDeleteAll = async () => {
    if (!confirm('ATENÇÃO: Você tem certeza que deseja LINPAR TODOS os links salvos? Isso não pode ser desfeito.')) return;
    try {
      await deleteAllLinks();
      if (onRefresh) onRefresh();
    } catch (e: any) {
      alert(e.message || 'Erro ao deletar os links.');
    }
  };

  // Contadores e Filtros
  const relaunchCount = links.filter(l => l.is_relaunch).length;
  const communityCount = links.filter(l => l.link_type === 'community').length;

  const uniqueSources = Array.from(new Set(links.map(l => l.source).filter(Boolean)));
  const filteredLinks = links.filter(link => {
    const matchesSource = filterSource === 'all' || link.source === filterSource;
    const matchesSearch = searchTerm === '' || 
      link.url.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (link.source && link.source.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSource && matchesSearch;
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Filter className="w-6 h-6 text-blue-500" />
              Links Coletados ({filteredLinks.length})
            </h2>
            <div className="flex gap-2">
              {relaunchCount > 0 && (
                <span className="flex items-center gap-1 px-2 py-0.5 bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-400 rounded-full text-[10px] font-bold border border-orange-200 dark:border-orange-800/50">
                  <RefreshCw className="w-3 h-3" />
                  {relaunchCount} RELANÇAMENTOS
                </span>
              )}
              {communityCount > 0 && (
                <span className="flex items-center gap-1 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-400 rounded-full text-[10px] font-bold border border-yellow-200 dark:border-yellow-800/50">
                  <Users className="w-3 h-3" />
                  {communityCount} COMUNIDADES
                </span>
              )}
            </div>
          </div>
          {links.length > 0 && (
            <button
              onClick={handleDeleteAll}
              className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 rounded-lg transition-colors font-semibold text-sm"
            >
              <Trash2 className="w-4 h-4" />
              Limpar Tudo
            </button>
          )}
        </div>
        
        {/* Filtros */}
        <div className="mt-4 flex gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Buscar por URL ou campanha..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todas as campanhas</option>
            {uniqueSources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900 sticky top-0">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Link do Grupo
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Campanha
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Data/Hora
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {filteredLinks.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center">
                  <div className="text-gray-500 dark:text-gray-400">
                    <p className="text-lg font-medium mb-2">Nenhum link encontrado</p>
                    <p className="text-sm">Tente ajustar os filtros ou execute o scraper</p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredLinks.map((link, index) => (
                <tr key={index} className={`transition-colors ${
                  link.is_relaunch 
                    ? 'bg-orange-50/50 dark:bg-orange-900/10 hover:bg-orange-100/50 dark:hover:bg-orange-900/20' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium text-sm flex items-center gap-2 group"
                      >
                        <span className="truncate max-w-md">{link.url}</span>
                        <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </a>
                      <div className="flex gap-2">
                        {link.link_type === 'community' && (
                          <span className="flex items-center gap-1 text-[10px] font-bold text-yellow-600 dark:text-yellow-500 bg-yellow-100/50 dark:bg-yellow-900/30 px-1.5 py-0.5 rounded border border-yellow-200/50 dark:border-yellow-800/30">
                            <ShieldAlert className="w-3 h-3" />
                            COMUNIDADE
                          </span>
                        )}
                        {link.is_relaunch && (
                          <span className="flex items-center gap-1 text-[10px] font-bold text-orange-600 dark:text-orange-500 bg-orange-100/50 dark:bg-orange-900/30 px-1.5 py-0.5 rounded border border-orange-200/50 dark:border-orange-800/30">
                            <RefreshCw className="w-3 h-3 animate-spin-slow" />
                            RELANÇAMENTO
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-xs font-medium">
                      {link.source || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                    {formatDate(link.found_at)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => copyToClipboard(link.url)}
                        className="flex items-center gap-2 px-3 py-1.5 bg-sky-50 dark:bg-sky-900/30 text-sky-700 dark:text-sky-400 rounded-lg hover:bg-sky-100 dark:hover:bg-sky-800/50 transition-colors text-sm font-medium"
                      >
                        <Copy className="w-4 h-4" />
                        {copiedUrl === link.url ? 'Copiado!' : 'Copiar'}
                      </button>
                      <button
                        onClick={() => handleDelete(link.url)}
                        title="Deletar Link"
                        className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
