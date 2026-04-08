import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'HERMES para Creadores | Distribución + Monetización Automática',
  description: 'Plataforma para músicos y creadores: distribución en 50+ plataformas, cálculo de regalías en tiempo real, promoción automática. De demo a Spotify en 48 horas.',
  keywords: ['música', 'distribución digital', 'Spotify', 'regalías', 'creador independiente', 'podcast'],
  openGraph: {
    title: 'HERMES para Creadores',
    description: 'Distribución + monetización automática. Primera canción en Spotify en 48 horas. Sin gestor.',
    type: 'website',
  },
}

export default function ArtistasLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
