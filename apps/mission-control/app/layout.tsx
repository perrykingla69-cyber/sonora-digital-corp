import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Mission Control - HERMES OS',
  description: 'Real-time monitoring dashboard for HERMES OS',
  viewport: 'width=device-width, initial-scale=1.0',
  robots: 'noindex,nofollow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
