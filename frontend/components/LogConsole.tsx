'use client';

import { useState, useEffect, useRef } from 'react';
import { getRecentLogs } from '@/lib/api';
import { Terminal, Copy, Trash2, RefreshCw } from 'lucide-react';

interface LogConsoleProps {
  active: boolean;
  title?: string;
  maxHeight?: string;
}

export default function LogConsole({ active, title = "Console de Operações", maxHeight = "300px" }: LogConsoleProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    try {
      const data = await getRecentLogs(50);
      setLogs(data.logs);
    } catch (err) {
      console.error("Erro ao buscar logs:", err);
    }
  };

  // Poll logs when active
  useEffect(() => {
    let interval: any;
    if (active) {
      setLoading(true);
      fetchLogs().finally(() => setLoading(false));
      interval = setInterval(fetchLogs, 2000);
    } else {
      // Fetch once when inactive to show the result
      fetchLogs();
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [active]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const copyLogs = () => {
    navigator.clipboard.writeText(logs.join('\n'));
    alert('Logs copiados para a área de transferência!');
  };

  const clearLogView = () => {
    setLogs([]);
  };

  const formatLog = (line: string) => {
    const isError = line.toLowerCase().includes('erro') || line.toLowerCase().includes('failed') || line.includes('❌');
    const isSuccess = line.includes('✅') || line.includes('sucesso') || line.includes('finalizado');
    const isWarning = line.includes('⚠️') || line.includes('aviso');

    if (isError) return <span className="text-red-400">{line}</span>;
    if (isSuccess) return <span className="text-green-400">{line}</span>;
    if (isWarning) return <span className="text-yellow-400">{line}</span>;
    return <span>{line}</span>;
  };

  return (
    <div className="mt-6 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden shadow-sm bg-gray-900 text-gray-300 font-mono text-xs">
      {/* Toolbar */}
      <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-gray-200">{title}</span>
          {active && <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>}
        </div>
        <div className="flex gap-2">
          <button onClick={fetchLogs} title="Recarregar" className="hover:text-white transition-colors">
            <RefreshCw className={`w-3.5 h-3.5 ${active ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={copyLogs} title="Copiar" className="hover:text-white transition-colors">
            <Copy className="w-3.5 h-3.5" />
          </button>
          <button onClick={clearLogView} title="Limpar Tela" className="hover:text-white transition-colors">
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Log View */}
      <div 
        ref={scrollRef}
        className="p-4 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent"
        style={{ maxHeight }}
      >
        {logs.length === 0 ? (
          <p className="text-gray-600 italic">Nenhum log registrado recentemente...</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, i) => (
              <div key={i} className="whitespace-pre-wrap flex gap-3 border-b border-gray-800/30 pb-1 last:border-0">
                <span className="text-gray-600 select-none">{(i + 1).toString().padStart(2, '0')}</span>
                <div className="flex-1">{formatLog(log)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="bg-gray-800/50 px-4 py-1.5 border-t border-gray-700 text-[10px] text-gray-500 flex justify-between">
        <span>LinkPulse v3.2 IA Console</span>
        <span>{active ? 'Status: Rodando...' : 'Status: Pronto'}</span>
      </div>
    </div>
  );
}
