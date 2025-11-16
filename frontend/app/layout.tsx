import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LinkPulse - Dashboard',
  description: 'Dashboard para monitoramento e coleta de links de grupos WhatsApp',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}

