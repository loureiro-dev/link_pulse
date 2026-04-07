"use client";

import { useState } from "react";
import { getAuthToken } from "@/lib/auth";

interface QuickResult {
  url: string;
  name: string;
  page_added: boolean;
  links_found: number;
  links: string[];
  success: boolean;
  message: string;
}

interface QuickResponse {
  success: boolean;
  urls_processed: number;
  total_links_found: number;
  results: QuickResult[];
  message: string;
}

export default function QuickCollectSection() {
  const [urlInput, setUrlInput] = useState("");
  const [sourceName, setSourceName] = useState("Via Telegram");
  const [addToPages, setAddToPages] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QuickResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Webhook Telegram
  const [backendUrl, setBackendUrl] = useState("");
  const [webhookStatus, setWebhookStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [webhookMsg, setWebhookMsg] = useState("");

  async function handleCollect() {
    const lines = urlInput
      .split(/[\n,]+/)
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (lines.length === 0) {
      setError("Cole pelo menos uma URL.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = getAuthToken();
      const res = await fetch("http://localhost:8000/api/discovery/quick", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          urls: lines,
          source_name: sourceName || "Envio Manual",
          add_to_pages: addToPages,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Erro na coleta");
      }

      const data: QuickResponse = await res.json();
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erro inesperado");
    } finally {
      setLoading(false);
    }
  }

  async function handleActivateWebhook() {
    setWebhookStatus("loading");
    setWebhookMsg("");
    try {
      const token = getAuthToken();
      const res = await fetch("http://localhost:8000/api/telegram/set-webhook", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setWebhookStatus("ok");
        setWebhookMsg(data.message);
      } else {
        setWebhookStatus("error");
        setWebhookMsg(data.detail || "Erro ao ativar webhook");
      }
    } catch (e: unknown) {
      setWebhookStatus("error");
      setWebhookMsg(e instanceof Error ? e.message : "Erro inesperado");
    }
  }

  async function handleRemoveWebhook() {
    setWebhookStatus("loading");
    try {
      const token = getAuthToken();
      const res = await fetch("http://localhost:8000/api/telegram/set-webhook", {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setWebhookStatus(data.success ? "idle" : "error");
      setWebhookMsg(data.success ? "Webhook removido." : data.detail || "Erro");
    } catch {
      setWebhookStatus("error");
      setWebhookMsg("Erro ao remover webhook");
    }
  }

  return (
    <div className="space-y-8">
      {/* Info principal */}
      <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
        <span className="text-2xl">⚡</span>
        <div>
          <p className="font-semibold text-green-800">Coleta Imediata via URL</p>
          <p className="text-sm text-green-700 mt-1">
            Cole aqui qualquer URL que você recebeu no Telegram (ou outra fonte). O sistema
            adiciona ao monitoramento e <strong>coleta os grupos WhatsApp na hora</strong>.
          </p>
        </div>
      </div>

      {/* Formulário de coleta */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <h3 className="font-semibold text-gray-800 text-lg">Colar URLs para coleta imediata</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            URL(s) — uma por linha ou separadas por vírgula
          </label>
          <textarea
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder={"https://vendas.exemplo.com/lancamento\nhttps://outro-site.com/oferta"}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-green-400 resize-none"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Origem / Label</label>
            <input
              type="text"
              value={sourceName}
              onChange={(e) => setSourceName(e.target.value)}
              placeholder="Ex: Via Telegram, Grupo X"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
          </div>
          <div className="flex items-center gap-3 pt-6">
            <input
              type="checkbox"
              id="addToPages"
              checked={addToPages}
              onChange={(e) => setAddToPages(e.target.checked)}
              className="w-4 h-4 text-green-600 rounded"
            />
            <label htmlFor="addToPages" className="text-sm text-gray-700">
              Adicionar às páginas monitoradas
            </label>
          </div>
        </div>

        <button
          onClick={handleCollect}
          disabled={loading}
          className="w-full sm:w-auto px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white font-semibold rounded-xl transition-colors shadow-sm"
        >
          {loading ? "Coletando..." : "⚡ Coletar Agora"}
        </button>
      </div>

      {/* Erro */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Resultado */}
      {result && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-xl">
            <span className="text-3xl">{result.total_links_found > 0 ? "🎯" : "🔍"}</span>
            <div>
              <p className="font-semibold text-gray-800">{result.message}</p>
              <p className="text-sm text-gray-500">
                {result.urls_processed} URL(s) processada(s)
              </p>
            </div>
          </div>

          {result.results.map((r, i) => (
            <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-800 text-sm truncate max-w-xs">{r.url}</p>
                  <p className="text-xs text-gray-500">{r.name}</p>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  {r.page_added && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full">Adicionada</span>
                  )}
                  <span
                    className={`px-2 py-1 rounded-full font-semibold ${
                      r.links_found > 0
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {r.links_found} grupo(s)
                  </span>
                </div>
              </div>

              {r.links.length > 0 && (
                <div className="p-4 space-y-2">
                  {r.links.map((link, j) => (
                    <a
                      key={j}
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-3 py-2 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 hover:bg-green-100 transition-colors"
                    >
                      <span>💬</span>
                      <span className="font-mono truncate">{link}</span>
                    </a>
                  ))}
                </div>
              )}

              {r.links.length === 0 && (
                <div className="p-4 text-sm text-gray-500 italic">{r.message}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ─── SEÇÃO: BOT TELEGRAM AUTOMÁTICO ─── */}
      <div className="border-t border-gray-200 pt-8">
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🤖</span>
            <div>
              <p className="font-semibold text-blue-800 text-lg">Bot Telegram Automático</p>
              <p className="text-sm text-blue-700 mt-1">
                Ative o webhook e o bot do LinkPulse passa a ouvir mensagens. Você encontrou uma URL
                no Telegram? Encaminhe para o bot — ele <strong>coleta automaticamente</strong> e te
                responde com os grupos encontrados.
              </p>
            </div>
          </div>

          <ol className="text-sm text-blue-700 space-y-1 ml-2 list-decimal list-inside">
            <li>Configure o bot em <strong>Configurações → Telegram</strong> (token + chat ID).</li>
            <li>
              Adicione <code className="bg-blue-100 px-1 rounded">BACKEND_URL=https://seu-backend.com</code> no{" "}
              <code className="bg-blue-100 px-1 rounded">.env</code> (precisa ser acessível pela internet).
            </li>
            <li>Clique em <strong>"Ativar Webhook"</strong> abaixo.</li>
            <li>Envie qualquer URL para o bot no Telegram — ele coleta e responde!</li>
          </ol>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleActivateWebhook}
              disabled={webhookStatus === "loading"}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-sm font-semibold rounded-lg transition-colors"
            >
              {webhookStatus === "loading" ? "Ativando..." : "🔗 Ativar Webhook"}
            </button>
            <button
              onClick={handleRemoveWebhook}
              disabled={webhookStatus === "loading"}
              className="px-5 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-semibold rounded-lg transition-colors"
            >
              Desativar
            </button>
          </div>

          {webhookStatus === "ok" && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
              ✅ {webhookMsg}
            </div>
          )}
          {webhookStatus === "error" && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              ❌ {webhookMsg}
            </div>
          )}
          {webhookStatus === "idle" && webhookMsg && (
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-600 text-sm">
              {webhookMsg}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
