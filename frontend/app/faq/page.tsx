'use client';

import { useState } from 'react';
import { 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  Zap, 
  MessageSquare, 
  Brain, 
  PlayCircle,
  ExternalLink,
  Settings
} from 'lucide-react';
import Link from 'next/link';

interface AccordionItemProps {
  title: string;
  icon: any;
  children: React.ReactNode;
}

function AccordionItem({ title, icon: Icon, children }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-white dark:bg-gray-800 transition-all hover:shadow-md">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 text-left bg-gray-50/50 dark:bg-gray-900/10"
      >
        <div className="flex items-center gap-4">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
            <Icon className="w-5 h-5" />
          </div>
          <span className="font-semibold text-gray-900 dark:text-white">{title}</span>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
      </button>
      {isOpen && (
        <div className="p-6 border-t border-gray-100 dark:border-gray-700 text-gray-600 dark:text-gray-400 text-sm leading-relaxed space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
          {children}
        </div>
      )}
    </div>
  );
}

export default function FAQPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center p-3 bg-blue-600 rounded-2xl shadow-xl shadow-blue-500/20 mb-4">
          <HelpCircle className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-black text-gray-900 dark:text-white tracking-tight">FAQS E TUTORIAIS</h1>
        <p className="text-gray-600 dark:text-gray-400 text-lg">
          Aprenda a configurar e dominar o LinkPulse IA v3.2
        </p>
      </div>

      <div className="space-y-4">
        {/* API SETUP */}
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-8 mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-blue-500" />
          Configuração de APIs
        </h2>

        <AccordionItem title="Como configurar o Bot do Telegram?" icon={MessageSquare}>
          <div className="space-y-4">
            <p>O Telegram é essencial para receber notificações de novos links em tempo real.</p>
            <ol className="list-decimal list-inside space-y-2">
              <li>Fale com o <strong>@BotFather</strong> no Telegram para criar seu bot e obter o <strong>Token</strong>.</li>
              <li>Consiga seu <strong>Chat ID</strong> usando o bot <strong>@userinfobot</strong>.</li>
              <li>Acesse a página de <Link href="/telegram" className="text-blue-600 font-bold hover:underline inline-flex items-center gap-1">Configurações <ExternalLink className="w-3 h-3"/></Link> e salve os dados.</li>
              <li>Clique em <strong>Testar Notificação</strong> para garantir que está funcionando.</li>
            </ol>
          </div>
        </AccordionItem>

        <AccordionItem title="Como ativar a Inteligência Artificial (Gemini)?" icon={Brain}>
          <div className="space-y-4">
            <p>O Gemini é o motor que classifica os links e identifica se são de lançamentos reais.</p>
            <ol className="list-decimal list-inside space-y-2">
              <li>Acesse o <a href="https://aistudio.google.com/app/apikey" target="_blank" className="underline font-bold">Google AI Studio</a>.</li>
              <li>Crie uma chave de API gratuita para o modelo <strong>Gemini 1.5 Flash</strong>.</li>
              <li>Vá em <Link href="/telegram" className="text-blue-600 font-bold hover:underline inline-flex items-center gap-1">Configurações → IA / Gemini <ExternalLink className="w-3 h-3"/></Link>.</li>
              <li>Ative a <strong>"Mineração Seletiva"</strong> para filtrar apenas links de alta qualidade.</li>
            </ol>
          </div>
        </AccordionItem>

        {/* OPERATION */}
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-8 mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-500" />
          Operação do Sistema
        </h2>

        <AccordionItem title="Qual a diferença entre Coleta e Mineração?" icon={Zap}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-900/40 rounded-lg">
              <h4 className="font-bold text-blue-600 mb-2">Coleta (Scraper)</h4>
              <p>Visita as páginas que <strong>você já conhece</strong>. É ideal para monitorar links em lançamentos específicos que você já cadastrou.</p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-900/40 rounded-lg">
              <h4 className="font-bold text-emerald-600 mb-2">Mineração (Descoberta)</h4>
              <p>O sistema <strong>busca na internet</strong> (Facebook Ads, YouTube, Google) por novas páginas que você ainda não conhece, usando palavras-chave.</p>
            </div>
          </div>
          <div className="mt-4 p-4 border-l-4 border-indigo-500 bg-indigo-50 dark:bg-indigo-900/10">
            <p className="font-bold italic">💡 Dica: Use a Mineração para encontrar o que a concorrência está fazendo e a Coleta para monitorar o grupo final.</p>
          </div>
        </AccordionItem>

        <AccordionItem title="Como funciona o Agendamento Automático?" icon={PlayCircle}>
          <p>O LinkPulse IA trabalha enquanto você dorme!</p>
          <ul className="list-disc list-inside mt-3 space-y-2">
            <li>As coletas automáticas ocorrem às <strong>08h, 14h e 20h (Brasília)</strong>.</li>
            <li>O sistema verifica 100% das páginas salvas em <Link href="/pages-manager" className="text-blue-600 font-bold hover:underline underline-offset-2 inline-flex items-center gap-1">Gerenciar Páginas <ExternalLink className="w-3 h-3"/></Link>.</li>
            <li>Se a IA estiver ativa, apenas links validados serão notificados no seu Telegram.</li>
          </ul>
        </AccordionItem>

        <AccordionItem title="Como usar as etiquetas de Mineração?" icon={Zap}>
          <p>Para deixar a sua mineração mais seletiva, configure termos alvo.</p>
          <div className="mt-2 space-y-2">
            <p>Vá em <Link href="/discovery" className="text-blue-600 font-bold underline underline-offset-2 inline-flex items-center gap-1">Minerar <ExternalLink className="w-3 h-3"/></Link> e use termos como:</p>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600 italic">"Grupo VIP"</span>
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600 italic">"Workshop Gratuito"</span>
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600 italic">"Inscrição Aberta"</span>
            </div>
          </div>
        </AccordionItem>
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 text-center text-white shadow-xl">
        <h3 className="text-2xl font-bold mb-3">Ainda tem dúvidas?</h3>
        <p className="opacity-90 mb-6 max-w-lg mx-auto">
          Nosso console de logs mostra em tempo real o que o sistema está processando. Se encontrar problemas, verifique os logs na tela de coleta ou mineração.
        </p>
        <Link 
          href="/dashboard"
          className="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transition-all transform hover:scale-105"
        >
          Ir para o Dashboard
        </Link>
      </div>
    </div>
  );
}
