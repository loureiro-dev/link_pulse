'use client';

import { Page } from '@/lib/api';
import { useState, useEffect } from 'react';
import { getPages, createPage, deletePage } from '@/lib/api';

export default function PagesManager() {
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ url: '', name: '' });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadPages = async () => {
    try {
      setLoading(true);
      const data = await getPages();
      setPages(data);
    } catch (err) {
      setError('Erro ao carregar páginas');
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
      await createPage(formData);
      setSuccess('Página adicionada com sucesso!');
      setFormData({ url: '', name: '' });
      setShowForm(false);
      loadPages();
    } catch (err: any) {
      setError(err.message || 'Erro ao adicionar página');
    }
  };

  const handleDelete = async (url: string) => {
    if (!confirm('Tem certeza que deseja excluir esta página?')) return;

    try {
      await deletePage(url);
      setSuccess('Página excluída com sucesso!');
      loadPages();
    } catch (err) {
      setError('Erro ao excluir página');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Páginas Monitoradas ({pages.length})
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition"
        >
          {showForm ? 'Cancelar' : '+ Adicionar Página'}
        </button>
      </div>

      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="mx-6 mt-4 p-3 bg-green-100 dark:bg-green-900 border border-green-400 text-green-700 dark:text-green-300 rounded">
          {success}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                URL da Página
              </label>
              <input
                type="url"
                required
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="https://exemplo.com/landing"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nome da Campanha
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Nome da campanha"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition"
            >
              Adicionar
            </button>
          </div>
        </form>
      )}

      <div className="p-6">
        {loading ? (
          <p className="text-gray-500 dark:text-gray-400">Carregando...</p>
        ) : pages.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 text-center py-4">
            Nenhuma página cadastrada. Adicione uma página para começar o monitoramento.
          </p>
        ) : (
          <div className="space-y-3">
            {pages.map((page, index) => (
              <div
                key={index}
                className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900 dark:text-white">{page.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">{page.url}</p>
                </div>
                <button
                  onClick={() => handleDelete(page.url)}
                  className="ml-4 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium text-sm"
                >
                  Excluir
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

