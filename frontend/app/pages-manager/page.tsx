'use client';

import { useState, useEffect } from 'react';
import { getPages, createPage, deletePage, Page } from '@/lib/api';
import { Plus, Trash2, FileText, RefreshCw } from 'lucide-react';

export default function PagesManagerPage() {
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ url: '', name: '' });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadPages = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Carregando páginas...');
      const data = await getPages();
      console.log('Páginas carregadas:', data);
      setPages(data);
    } catch (err: any) {
      console.error('Erro ao carregar páginas:', err);
      const errorMessage = err.message || 'Erro ao carregar páginas';
      
      // Verifica se é erro de conexão
      if (errorMessage.includes('fetch') || 
          errorMessage.includes('Failed to fetch') || 
          errorMessage.includes('NetworkError') || 
          errorMessage.includes('conectar ao backend') ||
          errorMessage.includes('TypeError')) {
        setError('Não foi possível conectar ao backend. Verifique se o servidor está rodando na porta 8000.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPages();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      console.log('Adicionando página:', formData);
      await createPage(formData);
      setSuccess('Página adicionada com sucesso!');
      setFormData({ url: '', name: '' });
      setShowForm(false);
      // Recarrega a lista após adicionar
      await loadPages();
    } catch (err: any) {
      console.error('Erro ao adicionar página:', err);
      const errorMessage = err.message || 'Erro ao adicionar página';
      
      // Verifica se é erro de conexão
      if (errorMessage.includes('fetch') || 
          errorMessage.includes('Failed to fetch') || 
          errorMessage.includes('NetworkError') || 
          errorMessage.includes('conectar ao backend') ||
          errorMessage.includes('TypeError')) {
        setError('Não foi possível conectar ao backend. Verifique se o servidor está rodando na porta 8000.');
      } else if (errorMessage.includes('já cadastrada') || errorMessage.includes('já existe')) {
        setError('Esta URL já está cadastrada.');
      } else {
        setError(errorMessage);
      }
    }
  };

  const handleDelete = async (url: string) => {
    if (!confirm('Tem certeza que deseja excluir esta página?')) return;

    try {
      console.log('Excluindo página:', url);
      await deletePage(url);
      setSuccess('Página excluída com sucesso!');
      setError(null);
      // Recarrega a lista após excluir
      await loadPages();
    } catch (err: any) {
      console.error('Erro ao excluir página:', err);
      const errorMessage = err.message || 'Erro ao excluir página';
      
      // Verifica se é erro de conexão
      if (errorMessage.includes('fetch') || 
          errorMessage.includes('Failed to fetch') || 
          errorMessage.includes('NetworkError') || 
          errorMessage.includes('conectar ao backend') ||
          errorMessage.includes('TypeError')) {
        setError('Não foi possível conectar ao backend. Verifique se o servidor está rodando na porta 8000.');
      } else {
        setError(errorMessage);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Gerenciar Páginas</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Adicione e gerencie páginas para monitoramento
        </p>
      </div>

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-green-800 dark:text-green-200">{success}</p>
        </div>
      )}

      {/* Add Page Card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Adicionar Nova Página
          </h2>
          <div className="flex gap-2">
            <button
              onClick={loadPages}
              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Recarregar"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
            >
              <Plus className="w-4 h-4" />
              {showForm ? 'Cancelar' : 'Nova Página'}
            </button>
          </div>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                URL da Página
              </label>
              <input
                type="url"
                required
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://exemplo.com/landing"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nome da Campanha
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Nome da campanha"
              />
            </div>
            <button
              type="submit"
              className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all font-medium"
            >
              Adicionar Página
            </button>
          </form>
        )}
      </div>

      {/* Pages List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Páginas Cadastradas ({pages.length})
          </h2>
          <button
            onClick={loadPages}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Recarregar"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500 dark:text-gray-400">Carregando...</p>
          </div>
        ) : pages.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Nenhuma página cadastrada. Adicione uma página para começar o monitoramento.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {pages.map((page, index) => (
              <div
                key={index}
                className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center justify-between"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">{page.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{page.url}</p>
                </div>
                <button
                  onClick={() => handleDelete(page.url)}
                  className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
