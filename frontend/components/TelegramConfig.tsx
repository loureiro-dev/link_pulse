'use client';

import { useState, useEffect } from 'react';
import { getTelegramConfig, saveTelegramConfig, testTelegram } from '@/lib/api';

export default function TelegramConfig() {
  const [config, setConfig] = useState({ bot_token: '', chat_id: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const data = await getTelegramConfig();
      setConfig({ bot_token: data.bot_token || '', chat_id: data.chat_id || '' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao carregar configuração' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await saveTelegramConfig(config);
      setMessage({ type: 'success', text: 'Configuração salva com sucesso!' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Erro ao salvar configuração' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage(null);

    try {
      await testTelegram();
      setMessage({ type: 'success', text: 'Mensagem de teste enviada com sucesso!' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Erro ao enviar teste' });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6">
        <p className="text-gray-500 dark:text-gray-400">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Configuração do Telegram
        </h2>
      </div>
      <form onSubmit={handleSave} className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Bot Token
          </label>
          <input
            type="text"
            value={config.bot_token}
            onChange={(e) => setConfig({ ...config, bot_token: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Chat ID
          </label>
          <input
            type="text"
            value={config.chat_id}
            onChange={(e) => setConfig({ ...config, chat_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="-1001234567890"
          />
        </div>

        {message && (
          <div
            className={`p-3 rounded border ${
              message.type === 'success'
                ? 'bg-green-100 dark:bg-green-900 border-green-400 text-green-700 dark:text-green-300'
                : 'bg-red-100 dark:bg-red-900 border-red-400 text-red-700 dark:text-red-300'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition"
          >
            {saving ? 'Salvando...' : 'Salvar Configuração'}
          </button>
          <button
            type="button"
            onClick={handleTest}
            disabled={testing || !config.bot_token || !config.chat_id}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition"
          >
            {testing ? 'Enviando...' : 'Testar Notificação'}
          </button>
        </div>
      </form>
    </div>
  );
}

