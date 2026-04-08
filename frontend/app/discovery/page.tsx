"use client";

import { useState } from "react";
import DuckDuckGoSection from "@/components/discovery/DuckDuckGoSection";
import YoutubeSection from "@/components/discovery/YoutubeSection";
import QuickCollectSection from "@/components/discovery/QuickCollectSection";
import FacebookSection from "@/components/discovery/FacebookSection";
import LogConsole from "@/components/LogConsole";

type Tab = "quick" | "duckduckgo" | "youtube" | "facebook";

const TABS: { id: Tab; label: string; icon: string; description: string }[] = [
  {
    id: "quick",
    label: "Coleta Rápida",
    icon: "⚡",
    description: "Cole uma URL ou ative o bot Telegram",
  },
  {
    id: "facebook",
    label: "Anúncios FB",
    icon: "📱",
    description: "Busca na Biblioteca de Anúncios do Facebook",
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
  const [activeTab, setActiveTab] = useState<Tab>("facebook");

  const active = TABS.find((t) => t.id === activeTab)!;

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-black text-gray-900 dark:text-white bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
          Minerar Leads IA
        </h1>
        <p className="text-gray-500 dark:text-gray-400 max-w-2xl">
          Utilize motores de busca e inteligência artificial para encontrar páginas de captura e grupos de WhatsApp em tempo real.
        </p>
      </div>

      {/* Tabs Menu */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-gray-100 dark:bg-gray-800/50 rounded-2xl w-fit border border-gray-200 dark:border-gray-700">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-200 ${
              activeTab === tab.id
                ? "bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-md ring-1 ring-gray-200 dark:ring-gray-600"
                : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-700/50"
            }`}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* active.description badge */}
      <div className="flex items-center gap-2 px-4 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg text-xs font-bold w-fit border border-blue-100 dark:border-blue-800/30">
        <span className="animate-pulse">{active.icon}</span>
        {active.description}
      </div>

      {/* Tab Content */}
      <div className="transition-all duration-300">
        {activeTab === "quick" && <QuickCollectSection />}
        {activeTab === "facebook" && <FacebookSection />}
        {activeTab === "duckduckgo" && <DuckDuckGoSection />}
        {activeTab === "youtube" && <YoutubeSection />}
      </div>

      {/* Console de Logs da Mineração */}
      <div className="pt-8 border-t border-gray-100 dark:border-gray-800">
        <LogConsole active={false} title="Monitor de Mineração IA" maxHeight="200px" />
      </div>
    </div>
  );
}
