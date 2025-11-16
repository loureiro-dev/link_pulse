'use client';

import { Bell, Settings, User, LogOut, Shield } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { logout, getCurrentUser } from '@/lib/auth';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Header() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string; name?: string; is_admin?: boolean } | null>(null);

  useEffect(() => {
    // Load current user
    const loadUser = async () => {
      const userData = await getCurrentUser();
      setUser(userData);
    };
    loadUser();
    
    // Reload user every 30 seconds to catch admin status changes
    const interval = setInterval(loadUser, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            LinkPulse
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Sistema de Monitoramento de Links WhatsApp
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {user && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {user.name || user.email}
            </div>
          )}
          {user?.is_admin && (
            <Link
              href="/admin"
              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Painel de Administração"
            >
              <Shield className="w-5 h-5" />
            </Link>
          )}
          <Link
            href="/profile"
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Meu Perfil"
          >
            <User className="w-5 h-5" />
          </Link>
          <button
            onClick={handleLogout}
            className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Sair"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}

