import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sonora Digital Corp - Agentes IA Inteligentes',
  description: 'Automatiza tu negocio con agentes IA sin código. Integración en minutos, resultados inmediatos.',
  keywords: ['IA', 'automatización', 'agentes digitales', 'negocio', 'México'],
  authors: [{ name: 'Sonora Digital Corp' }],
  openGraph: {
    title: 'Sonora Digital Corp',
    description: 'Automatiza tu negocio con agentes IA sin código',
    type: 'website',
    locale: 'es_MX',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
