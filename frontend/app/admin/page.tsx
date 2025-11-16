'use client';

import { useState, useEffect } from 'react';
import { getPendingUsers, getAllUsers, approveUser, rejectUser, User } from '@/lib/api';
import { Shield, Check, X, Users, UserCheck, UserX, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';

export default function AdminPage() {
  const router = useRouter();
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showAllUsers, setShowAllUsers] = useState(false);

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    try {
      const user = await getCurrentUser();
      console.log('Admin page - Current user:', user);
      console.log('Admin page - is_admin:', user?.is_admin);
      
      if (!user) {
        console.log('Admin page - No user, redirecting to login');
        router.push('/login');
        return;
      }
      
      if (!user.is_admin) {
        console.log('Admin page - User is not admin, redirecting to dashboard');
        router.push('/dashboard');
        return;
      }
      
      console.log('Admin page - User is admin, loading users');
      setCurrentUser(user);
      loadUsers();
    } catch (err) {
      console.error('Admin page - Error checking access:', err);
      router.push('/dashboard');
    }
  };

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const [pending, all] = await Promise.all([
        getPendingUsers(),
        getAllUsers(true),
      ]);
      setPendingUsers(pending);
      setAllUsers(all);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId: number) => {
    setProcessing(userId);
    setError(null);
    try {
      await approveUser(userId);
      await loadUsers(); // Reload users
    } catch (err: any) {
      setError(err.message || 'Erro ao aprovar usuário');
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (userId: number) => {
    if (!confirm('Tem certeza que deseja rejeitar e excluir este usuário?')) {
      return;
    }
    
    setProcessing(userId);
    setError(null);
    try {
      await rejectUser(userId);
      await loadUsers(); // Reload users
    } catch (err: any) {
      setError(err.message || 'Erro ao rejeitar usuário');
    } finally {
      setProcessing(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
          <p className="text-sm text-gray-500 mt-2">Verificando permissões de administrador...</p>
        </div>
      </div>
    );
  }

  // If we get here but currentUser is null or not admin, show error
  if (!currentUser || !currentUser.is_admin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-lg shadow">
          <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Acesso Negado</h2>
          <p className="text-gray-600 mb-4">Você não tem permissão para acessar esta página.</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Voltar ao Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="w-8 h-8" />
            Painel de Administração
          </h1>
          <p className="mt-2 text-gray-600">Gerencie usuários e aprovações</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Usuários Pendentes</p>
                <p className="text-2xl font-bold text-yellow-600">{pendingUsers.length}</p>
              </div>
              <UserX className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total de Usuários</p>
                <p className="text-2xl font-bold text-blue-600">{allUsers.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Usuários Aprovados</p>
                <p className="text-2xl font-bold text-green-600">
                  {allUsers.filter(u => u.approved).length}
                </p>
              </div>
              <UserCheck className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        {/* Pending Users */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <UserX className="w-5 h-5" />
              Usuários Pendentes de Aprovação
            </h2>
          </div>

          <div className="p-6">
            {pendingUsers.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Nenhum usuário pendente</p>
            ) : (
              <div className="space-y-4">
                {pendingUsers.map((user) => (
                  <div
                    key={user.id}
                    className="border border-gray-200 rounded-lg p-4 flex items-center justify-between hover:bg-gray-50"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Users className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {user.name || 'Sem nome'}
                          </p>
                          <p className="text-sm text-gray-600">{user.email}</p>
                          {user.created_at && (
                            <p className="text-xs text-gray-500">
                              Registrado em: {new Date(user.created_at).toLocaleDateString('pt-BR')}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleApprove(user.id)}
                        disabled={processing === user.id}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        <Check className="w-4 h-4" />
                        {processing === user.id ? 'Aprovando...' : 'Aprovar'}
                      </button>
                      <button
                        onClick={() => handleReject(user.id)}
                        disabled={processing === user.id}
                        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        <X className="w-4 h-4" />
                        Rejeitar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* All Users */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Todos os Usuários
            </h2>
            <button
              onClick={() => setShowAllUsers(!showAllUsers)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAllUsers ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>

          {showAllUsers && (
            <div className="p-6">
              {allUsers.length === 0 ? (
                <p className="text-gray-500 text-center py-8">Nenhum usuário cadastrado</p>
              ) : (
                <div className="space-y-4">
                  {allUsers.map((user) => (
                    <div
                      key={user.id}
                      className="border border-gray-200 rounded-lg p-4 flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            user.is_admin ? 'bg-purple-100' : 'bg-gray-100'
                          }`}>
                            <Users className={`w-5 h-5 ${
                              user.is_admin ? 'text-purple-600' : 'text-gray-600'
                            }`} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-gray-900">
                                {user.name || 'Sem nome'}
                              </p>
                              {user.is_admin && (
                                <span className="px-2 py-1 text-xs font-semibold bg-purple-100 text-purple-800 rounded">
                                  Admin
                                </span>
                              )}
                              {user.approved ? (
                                <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 rounded">
                                  Aprovado
                                </span>
                              ) : (
                                <span className="px-2 py-1 text-xs font-semibold bg-yellow-100 text-yellow-800 rounded">
                                  Pendente
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600">{user.email}</p>
                            {user.created_at && (
                              <p className="text-xs text-gray-500">
                                Registrado em: {new Date(user.created_at).toLocaleDateString('pt-BR')}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

