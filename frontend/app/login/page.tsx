'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { login } from '@/lib/auth';
import { isAuthenticated } from '@/lib/auth';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Check if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      const redirect = searchParams.get('redirect') || '/dashboard';
      router.push(redirect);
    }
  }, [router, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      const redirect = searchParams.get('redirect') || '/dashboard';
      router.push(redirect);
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-slate-900 px-4 overflow-hidden">
      
      {/* Background Gigante Logo */}
      <div className="absolute inset-0 z-0 flex items-center justify-center opacity-5 dark:opacity-10 pointer-events-none">
        <Image src="/logo.png" alt="" width={800} height={800} className="w-[80vw] max-w-[800px] object-contain scale-125 blur-[2px]" />
      </div>

      <div className="max-w-md w-full space-y-8 z-10 relative bg-white/70 dark:bg-gray-800/80 backdrop-blur-xl p-10 rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50">
        <div>
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-sky-400 to-blue-600 rounded-2xl shadow-lg p-0.5">
              <div className="w-full h-full bg-white dark:bg-gray-800 rounded-[14px] flex items-center justify-center p-2">
                <Image src="/logo.png" alt="Logo" width={64} height={64} className="w-full h-full object-contain" />
              </div>
            </div>
          </div>
          <h2 className="mt-2 text-center text-3xl font-extrabold bg-gradient-to-r from-sky-400 to-blue-600 bg-clip-text text-transparent">
            LinkPulse IA
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Acesse sua conta ou{' '}
            <a
              href="/register"
              className="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 transition-colors"
            >
              crie uma nova
            </a>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-lg bg-red-50 dark:bg-red-900/30 p-4 border border-red-200 dark:border-red-800/30">
              <div className="text-sm text-red-800 dark:text-red-300 font-medium text-center">{error}</div>
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300/50 placeholder-gray-400 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent sm:text-sm dark:bg-gray-900/50 dark:border-gray-600/50 dark:text-white transition-all bg-white/50 backdrop-blur-sm"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300/50 placeholder-gray-400 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent sm:text-sm dark:bg-gray-900/50 dark:border-gray-600/50 dark:text-white transition-all bg-white/50 backdrop-blur-sm"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3.5 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 shadow-lg shadow-blue-500/30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:ring-offset-gray-50 dark:focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:-translate-y-0.5 duration-200"
            >
              {loading ? 'Autenticando...' : 'Entrar no Sistema'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-gray-600 dark:text-gray-400">Carregando...</div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}


