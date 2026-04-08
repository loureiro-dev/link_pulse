'use client';

import { usePathname, useRouter } from 'next/navigation';
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
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="p-3 bg-white dark:bg-gray-800 rounded-2xl shadow-xl shadow-blue-500/10 border border-gray-100 dark:border-gray-700">
            <img src="/logo.png" alt="LinkPulse Logo" className="w-16 h-16 object-contain hover:scale-105 transition-transform duration-300" />
          </div>
          <div>
            <p className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest">
              LinkPulse IA
            </p>
            <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">
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

