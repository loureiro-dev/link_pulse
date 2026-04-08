'use client';

import { useState } from 'react';
import { Search, Facebook, Info, ShieldCheck, AlertTriangle, XCircle, Plus, Loader2 } from 'lucide-react';
import { runFacebookLibraryDiscovery, addDiscoveredPage } from '@/lib/api';

export default function FacebookSection() {
  const [queries, setQueries] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);

  const handleSearch = async () => {
    if (!queries.trim()) return;
    setLoading(true);
    setResults([]);
    
    try {
      const qList = queries.split(',').map(q => q.trim());
      const response = await runFacebookLibraryDiscovery({
        queries: qList,
        scroll_times: 3,
        max_ads_per_query: 20,
        use_ai: true,
        auto_add: false
      });
      
      if (response.success) {
        setResults(response.pages);
        setStats({
          total: response.pages_found,
          approved: response.approved,
          review: response.review,
          rejected: response.rejected
        });
      }
    } catch (error) {
      console.error('Erro na busca do Facebook:', error);
      alert('Erro ao realizar busca na Biblioteca de Anúncios.');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (url: string, name: string) => {
    try {
      await addDiscoveredPage(url, name);
      setResults(prev => prev.map(p => p.url === url ? { ...p, added: true } : p));
    } catch (error) {
      alert('Erro ao adicionar página.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-blue-600 rounded-lg text-white">
            <Facebook className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Facebook Ad Library</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Encontre lançamentos ativos através de anúncios no Facebook</p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Palavras-chave (separadas por vírgula)
            </label>
            <div className="relative">
              <input
                type="text"
                value={queries}
                onChange={(e) => setQueries(e.target.value)}
                placeholder="ex: lançamento, grupo vip, desafio 21 dias"
                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              />
              <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            </div>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleSearch}
              disabled={loading || !queries.trim()}
              className="w-full md:w-auto px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
              {loading ? 'Minerando...' : 'Pesquisar'}
            </button>
          </div>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl border border-blue-100 dark:border-blue-900/30">
            <p className="text-xs text-blue-600 dark:text-blue-400 font-bold uppercase">Total Encontrado</p>
            <p className="text-2xl font-black text-blue-900 dark:text-blue-100">{stats.total}</p>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl border border-green-100 dark:border-green-900/30">
            <p className="text-xs text-green-600 dark:text-green-400 font-bold uppercase">Aprovados (IA)</p>
            <p className="text-2xl font-black text-green-900 dark:text-green-100">{stats.approved}</p>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl border border-yellow-100 dark:border-yellow-900/30">
            <p className="text-xs text-yellow-600 dark:text-yellow-400 font-bold uppercase">Revisar</p>
            <p className="text-2xl font-black text-yellow-900 dark:text-yellow-100">{stats.review}</p>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl border border-red-100 dark:border-red-900/30">
            <p className="text-xs text-red-600 dark:text-red-400 font-bold uppercase">Rejeitados</p>
            <p className="text-2xl font-black text-red-900 dark:text-red-100">{stats.rejected}</p>
          </div>
        </div>
      )}

      {results.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-100 dark:border-gray-700">
              <tr>
                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Página Descoberta</th>
                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Nicho (IA)</th>
                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase text-right">Ação</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {results.map((page, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-gray-900 dark:text-gray-100 truncate max-w-xs">{page.name}</div>
                    <div className="text-xs text-gray-500 truncate max-w-xs">{page.url}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded text-[10px] font-bold">
                      {page.ai_niche || 'Não Identificado'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {page.ai_status === 'approved' ? (
                      <div className="flex items-center gap-1 text-green-600 font-bold text-xs">
                        <ShieldCheck className="w-4 h-4" /> APROVADO
                      </div>
                    ) : page.ai_status === 'rejected' ? (
                      <div className="flex items-center gap-1 text-red-500 font-bold text-xs">
                        <XCircle className="w-4 h-4" /> REJEITADO
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-yellow-600 font-bold text-xs">
                        <AlertTriangle className="w-4 h-4" /> REVISAR
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleAdd(page.url, page.name)}
                      disabled={page.added}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        page.added 
                        ? 'bg-gray-100 text-gray-400 cursor-default' 
                        : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md shadow-blue-500/10'
                      }`}
                    >
                      {page.added ? 'Adicionado' : 'Adicionar'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
