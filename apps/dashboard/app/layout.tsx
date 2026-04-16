import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sonora Digital Corp — Dashboard',
  description: 'Plataforma de automatizaciones IA para tu negocio',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}
