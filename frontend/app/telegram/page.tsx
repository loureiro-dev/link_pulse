'use client';

import { useState, useEffect } from 'react';
import { getTelegramConfig, saveTelegramConfig, testTelegram, getYoutubeConfig, saveYoutubeApiKey, validateYoutubeKey, getAiConfig, saveAiConfig, validateAiKey } from '@/lib/api';
import { CheckCircle, AlertCircle, Send, MessageSquare, Youtube, Settings, Brain, Zap } from 'lucide-react';

type Tab = 'telegram' | 'youtube' | 'ai';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('telegram');

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <Settings className="w-8 h-8 text-gray-500" />
          Configurações
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Configure integrações e chaves de API do LinkPulse
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-3">
        <button
          onClick={() => setActiveTab('telegram')}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl border-2 text-sm font-semibold transition-all ${
            activeTab === 'telegram'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Telegram
        </button>
        <button
          onClick={() => setActiveTab('youtube')}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl border-2 text-sm font-semibold transition-all ${
            activeTab === 'youtube'
              ? 'border-red-500 bg-red-50 text-red-700'
              : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
          }`}
        >
          <Youtube className="w-4 h-4" />
          YouTube API
        </button>
        <button
          onClick={() => setActiveTab('ai')}
          className={`flex items-center gap-2 px-5 py-3 rounded-xl border-2 text-sm font-semibold transition-all ${
            activeTab === 'ai'
              ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
              : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
          }`}
        >
          <Brain className="w-4 h-4" />
          IA / Gemini
        </button>
      </div>

      {activeTab === 'telegram' && <TelegramTab />}
      {activeTab === 'youtube' && <YoutubeTab />}
      {activeTab === 'ai' && <AiTab />}
    </div>
  );
}

/* ─── ABA TELEGRAM ─── */
function TelegramTab() {
  const [config, setConfig] = useState({ bot_token: '', chat_id: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    getTelegramConfig()
      .then((d) => setConfig({ bot_token: d.bot_token || '', chat_id: d.chat_id || '' }))
      .catch(() => setMessage({ type: 'error', text: 'Erro ao carregar configuração' }))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await saveTelegramConfig(config);
      setMessage({ type: 'success', text: 'Configuração salva!' });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro ao salvar' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage(null);
    try {
      await testTelegram();
      setMessage({ type: 'success', text: 'Mensagem de teste enviada!' });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro no teste' });
    } finally {
      setTesting(false);
    }
  };

  if (loading) return <div className="text-gray-500 text-sm py-8 text-center">Carregando...</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
          <MessageSquare className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Bot Telegram</h2>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 space-y-1">
        <p className="font-semibold">Como configurar:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Bot Token: crie um bot com <strong>@BotFather</strong> no Telegram</li>
          <li>Chat ID: use <strong>@userinfobot</strong> para obter o seu</li>
          <li>O bot também pode receber URLs na aba <strong>Descoberta → Coleta Rápida</strong></li>
        </ul>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bot Token</label>
          <input
            type="text"
            value={config.bot_token}
            onChange={(e) => setConfig({ ...config, bot_token: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Chat ID</label>
          <input
            type="text"
            value={config.chat_id}
            onChange={(e) => setConfig({ ...config, chat_id: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="-1001234567890"
          />
        </div>

        {message && (
          <div className={`p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {message.type === 'success'
              ? <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              : <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />}
            <p className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
              {message.text}
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all font-medium disabled:opacity-50"
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
          <button
            type="button"
            onClick={handleTest}
            disabled={testing || !config.bot_token || !config.chat_id}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Send className="w-4 h-4" />
            {testing ? 'Enviando...' : 'Testar'}
          </button>
        </div>
      </form>
    </div>
  );
}

/* ─── ABA YOUTUBE ─── */
function YoutubeTab() {
  const [apiKey, setApiKey] = useState('');
  const [configured, setConfigured] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    getYoutubeConfig()
      .then((d) => {
        setConfigured(d.configured);
        setApiKey(d.api_key_preview || '');
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) { setMessage({ type: 'error', text: 'Informe a chave de API.' }); return; }
    setSaving(true);
    setMessage(null);
    try {
      const res = await saveYoutubeApiKey(apiKey.trim());
      setConfigured(true);
      setMessage({ type: 'success', text: res.message || 'Chave salva!' });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro ao salvar' });
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    setMessage(null);
    try {
      const res = await validateYoutubeKey();
      setMessage({ type: res.success ? 'success' : 'error', text: res.message });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro na validação' });
    } finally {
      setValidating(false);
    }
  };

  if (loading) return <div className="text-gray-500 text-sm py-8 text-center">Carregando...</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-red-600 rounded-lg">
          <Youtube className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">YouTube Data API</h2>
          {configured && (
            <span className="text-xs text-green-600 font-medium">✅ Configurada</span>
          )}
        </div>
      </div>

      <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-800 space-y-1">
        <p className="font-semibold">Como obter a chave:</p>
        <ol className="list-decimal list-inside space-y-1">
          <li>Acesse <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="underline">console.cloud.google.com</a></li>
          <li>Crie um projeto → Ative a <strong>YouTube Data API v3</strong></li>
          <li>Vá em <strong>Credenciais → Criar credencial → Chave de API</strong></li>
          <li>Cole a chave abaixo</li>
        </ol>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Chave de API</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:ring-2 focus:ring-red-500 focus:border-transparent"
            placeholder={configured ? '••••••••••••••••' : 'AIzaSy...'}
          />
        </div>

        {message && (
          <div className={`p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {message.type === 'success'
              ? <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              : <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />}
            <p className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
              {message.text}
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium disabled:opacity-50 transition-colors"
          >
            {saving ? 'Salvando...' : 'Salvar Chave'}
          </button>
          {configured && (
            <button
              type="button"
              onClick={handleValidate}
              disabled={validating}
              className="flex-1 px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium disabled:opacity-50 transition-colors"
            >
              {validating ? 'Validando...' : 'Validar Chave'}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

/* ─── ABA AI / GEMINI ─── */
function AiTab() {
  const [config, setConfig] = useState({ 
    api_key: '', 
    provider: 'gemini', 
    min_confidence: 0.6, 
    enabled: true 
  });
  const [configured, setConfigured] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    getAiConfig()
      .then((d) => {
        setConfigured(d.configured);
        setConfig({
          api_key: d.api_key_preview || '',
          provider: d.provider || 'gemini',
          min_confidence: d.min_confidence || 0.6,
          enabled: d.enabled !== false
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await saveAiConfig(config);
      setConfigured(true);
      setMessage({ type: 'success', text: 'Configurações de IA salvas!' });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro ao salvar' });
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    setMessage(null);
    try {
      const res = await validateAiKey();
      setMessage({ type: res.success ? 'success' : 'error', text: res.message });
    } catch (err: unknown) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Erro na validação' });
    } finally {
      setValidating(false);
    }
  };

  if (loading) return <div className="text-gray-500 text-sm py-8 text-center">Carregando...</div>;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-600 rounded-lg">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Inteligência Artificial (Gemini)</h2>
          {configured && (
            <span className="text-xs text-green-600 font-medium">✅ Configurada</span>
          )}
        </div>
      </div>

      <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-sm text-indigo-800 space-y-3">
        <div className="flex items-center gap-2 font-semibold">
          <Zap className="w-4 h-4" />
          Como funciona a Mineração Seletiva:
        </div>
        <p>
          A IA analisa as páginas e anúncios encontrados em tempo real. Ela busca por gatilhos de lançamentos 
          digitais como <strong>"grupo vip"</strong>, <strong>"workshop"</strong> e <strong>"masterclass"</strong>.
        </p>
        <p className="text-xs opacity-75 italic">
          * A mineração consome tokens da sua cota do Gemini (versão 1.5-flash é gratuita até certo limite).
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-4">
        <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700">
          <input
            type="checkbox"
            id="ai_enabled"
            checked={config.enabled}
            onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
            className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
          />
          <label htmlFor="ai_enabled" className="text-sm font-semibold text-gray-700 dark:text-gray-300 cursor-pointer">
            Ativar Mineração Seletiva e Classificação de Nichos
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Chave de API do Gemini</label>
          <input
            type="password"
            value={config.api_key}
            onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder={configured ? '••••••••••••••••' : 'AIzaSy...'}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nível de Confiança Mínimo: {(config.min_confidence * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={config.min_confidence}
            onChange={(e) => setConfig({ ...config, min_confidence: parseFloat(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <div className="flex justify-between text-[10px] text-gray-500 px-1 mt-1">
            <span>Mais resultados (menos preciso)</span>
            <span>Mais seletivo (mais preciso)</span>
          </div>
        </div>

        {message && (
          <div className={`p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {message.type === 'success'
              ? <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              : <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />}
            <p className={`text-sm ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
              {message.text}
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium shadow-md shadow-indigo-200 transition-all disabled:opacity-50"
          >
            {saving ? 'Salvando...' : 'Salvar Configurações'}
          </button>
          <button
            type="button"
            onClick={handleValidate}
            disabled={validating || !config.api_key}
            className="flex-1 px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {validating ? 'Validando...' : 'Testar Conexão'}
          </button>
        </div>
      </form>
    </div>
  );
}
