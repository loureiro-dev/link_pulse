'use client';

import { useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Image from 'next/image';
import { 
  LayoutDashboard, 
  FileText, 
  PlayCircle, 
  Zap,
  Settings,
  Info,
  Link as LinkIcon
} from 'lucide-react';

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/pages-manager', label: 'Gerenciar Páginas', icon: FileText },
  { path: '/scraper', label: 'Rodar Coleta', icon: PlayCircle },
  { path: '/discovery', label: 'Minerar', icon: Zap },
  { path: '/telegram', label: 'Configurações', icon: Settings },
  { path: '/about', label: 'Sobre', icon: Info },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Logo */}
      <div className="p-8 border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="w-full aspect-video relative flex items-center justify-center">
            <Image 
              src="/logo.png" 
              alt="LinkPulse Logo" 
              fill
              className="object-contain hover:scale-105 transition-transform duration-300" 
            />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-black text-blue-600 dark:text-blue-400 uppercase tracking-[0.2em]">
              LINKPULSE IA
            </p>
            <p className="text-[10px] font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Sistema de Monitoramento e Coleta
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          
          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all hover:-translate-y-0.5 duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-sky-400 to-blue-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-center text-gray-500 dark:text-gray-400">
          LinkPulse v3.2
        </p>
      </div>
    </aside>
  );
}

