'use client';

import { useState, useEffect, useCallback } from 'react';
import { Plus, X, Loader2, Save, RefreshCw } from 'lucide-react';
import { getCustomQueries, saveCustomQueries } from '@/lib/api';

interface KeywordManagerProps {
  module: string;
  label: string;
  defaultQueries: string[];
}

export default function KeywordManager({ module, label, defaultQueries }: KeywordManagerProps) {
  const [queries, setQueries] = useState<string[]>([]);
  const [newQuery, setNewQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const loadQueries = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getCustomQueries(module);
      setQueries(data.queries || []);
    } catch (err) {
      console.error('Erro ao carregar queries:', err);
    } finally {
      setLoading(false);
    }
  }, [module]);

  useEffect(() => {
    loadQueries();
  }, [loadQueries]);

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuery.trim()) return;
    if (queries.includes(newQuery.trim())) {
      setNewQuery('');
      return;
    }
    setQueries([...queries, newQuery.trim()]);
    setNewQuery('');
  };

  const handleRemove = (index: number) => {
    setQueries(queries.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await saveCustomQueries(module, queries);
      setMessage({ type: 'success', text: 'Salvo com sucesso!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Erro ao salvar' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {label}
        </label>
        <button 
          onClick={loadQueries}
          disabled={loading}
          className="text-gray-400 hover:text-indigo-500 transition-colors"
          title="Recarregar do banco"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-3">
        {/* Lista de Keywords */}
        <div className="flex flex-wrap gap-2 min-h-[40px] p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg">
          {queries.length === 0 && !loading && (
            <span className="text-xs text-gray-400 italic p-1">Nenhuma palavra-chave customizada...</span>
          )}
          {queries.map((q, i) => (
            <span 
              key={i} 
              className="flex items-center gap-1 px-2 py-1 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 text-xs rounded-md border border-indigo-200 dark:border-indigo-800"
            >
              {q}
              <button 
                onClick={() => handleRemove(i)}
                className="hover:text-red-500 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {loading && <Loader2 className="w-4 h-4 animate-spin text-gray-400 self-center" />}
        </div>

        {/* Input para Adicionar */}
        <form onSubmit={handleAdd} className="flex gap-2">
          <input
            type="text"
            value={newQuery}
            onChange={(e) => setNewQuery(e.target.value)}
            placeholder="Ex: grupo whatsapp mentoria"
            className="flex-1 px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none dark:text-white"
          />
          <button
            type="submit"
            className="p-2 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors"
          >
            <Plus className="w-5 h-5" />
          </button>
        </form>

        {/* Rodapé com Botão Salvar */}
        <div className="flex items-center justify-between pt-2">
          <div className="text-[10px] text-gray-500 dark:text-gray-400 max-w-[60%]">
            Estes termos serão usados na busca automática além dos termos padrão do sistema.
          </div>
          <div className="flex items-center gap-3">
            {message && (
              <span className={`text-xs font-medium ${message.type === 'success' ? 'text-green-500' : 'text-red-500'}`}>
                {message.text}
              </span>
            )}
            <button
              onClick={handleSave}
              disabled={saving || loading}
              className="flex items-center gap-2 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-all shadow-sm disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Salvar
            </button>
          </div>
        </div>
      </div>

      <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-lg">
        <p className="text-[10px] text-amber-800 dark:text-amber-200 leading-tight">
          <strong>Queries Padrão (Fixas):</strong> {defaultQueries.join(', ')}
        </p>
      </div>
    </div>
  );
}
