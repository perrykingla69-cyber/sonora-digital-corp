import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HERMES — SaaS IA para tu negocio',
  description: 'Contabilidad automática, WhatsApp IA, facturación CFDI y normatividad fiscal en tiempo real para PYMEs mexicanas.',
  keywords: ['contabilidad', 'CFDI', 'SAT', 'IA', 'contadores', 'Mexico', 'SaaS'],
  openGraph: {
    title: 'HERMES — Tu contador IA',
    description: 'Sin mensualidades. Sin multas. Facturación CFDI, RESICO, anti-multa aduanal y Brain IA.',
    url: 'https://hermes.app',
    siteName: 'HERMES',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#D4AF37" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </head>
      <body>{children}</body>
    </html>
  )
}
