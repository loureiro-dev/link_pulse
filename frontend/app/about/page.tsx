'use client';

import { Code, Database, Zap, Shield, Github, Link as LinkIcon } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Sobre o LinkPulse</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Sistema profissional SaaS para monitoramento e coleta automatizada de links
        </p>
      </div>

      {/* Main Info */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
            <LinkIcon className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">LinkPulse</h2>
            <p className="text-gray-600 dark:text-gray-400">Sistema de Monitoramento de Links</p>
          </div>
        </div>

        <p className="text-gray-700 dark:text-gray-300 mb-6">
          O LinkPulse é uma solução completa que combina um frontend moderno (Next.js) com um backend 
          robusto (FastAPI) para automatizar a descoberta e rastreamento de links importantes. O sistema 
          monitora páginas web, extrai links de grupos WhatsApp e envia notificações em tempo real.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Code className="w-5 h-5 text-blue-600" />
              Tecnologias
            </h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Next.js 14 com TypeScript</li>
              <li>• Tailwind CSS</li>
              <li>• FastAPI (Python)</li>
              <li>• SQLite Database</li>
            </ul>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-600" />
              Funcionalidades
            </h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Coleta automatizada de links</li>
              <li>• Dashboard em tempo real</li>
              <li>• Notificações Telegram</li>
              <li>• Gráficos e estatísticas</li>
            </ul>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Database className="w-5 h-5 text-green-600" />
              Armazenamento
            </h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Banco SQLite</li>
              <li>• Logs detalhados</li>
              <li>• Configurações persistentes</li>
            </ul>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-600" />
              Segurança
            </h3>
            <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <li>• CORS configurado</li>
              <li>• Validação de dados</li>
              <li>• Tratamento de erros</li>
            </ul>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Como Funciona</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Adicione Páginas</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Cadastre as URLs das páginas de captura que deseja monitorar
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Execute a Coleta</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                O scraper visita todas as páginas e extrai links de grupos WhatsApp
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">Receba Notificações</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Configure o Telegram para receber alertas de novos links encontrados
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

