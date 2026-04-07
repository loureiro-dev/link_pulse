"use client";

import { useState } from "react";
import DuckDuckGoSection from "@/components/discovery/DuckDuckGoSection";
import YoutubeSection from "@/components/discovery/YoutubeSection";
import QuickCollectSection from "@/components/discovery/QuickCollectSection";

type Tab = "quick" | "duckduckgo" | "youtube";

const TABS: { id: Tab; label: string; icon: string; description: string }[] = [
  {
    id: "quick",
    label: "Coleta Rápida",
    icon: "⚡",
    description: "Cole uma URL ou ative o bot Telegram",
  },
  {
    id: "duckduckgo",
    label: "DuckDuckGo",
    icon: "🔍",
    description: "Busca automática por lançamentos",
  },
  {
    id: "youtube",
    label: "YouTube",
    icon: "▶️",
    description: "Descobre via vídeos e descrições",
  },
];

export default function DiscoveryPage() {
  const [activeTab, setActiveTab] = useState<Tab>("quick");

  const active = TABS.find((t) => t.id === activeTab)!;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Descoberta Automática</h1>
        <p className="text-gray-500 mt-1">
          Encontre páginas de lançamento e colete grupos WhatsApp automaticamente.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-3">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl border-2 text-sm font-semibold transition-all ${
              activeTab === tab.id
                ? "border-indigo-500 bg-indigo-50 text-indigo-700 shadow-sm"
                : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
            }`}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Active tab description */}
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <span className="text-lg">{active.icon}</span>
        <span>{active.description}</span>
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        {activeTab === "quick" && <QuickCollectSection />}
        {activeTab === "duckduckgo" && <DuckDuckGoSection />}
        {activeTab === "youtube" && <YoutubeSection />}
      </div>
    </div>
  );
}
