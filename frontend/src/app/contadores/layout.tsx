import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'HERMES para Contadores | Normatividad MX + IA',
  description: 'Plataforma para contadores: NOMs, alertas fiscales, reportes DIOT/RESICO automáticos y IA sin alucinaciones. Reduce 30% tiempo administrativo.',
  keywords: ['contador', 'despacho fiscal', 'NOM-251', 'DIOT', 'RESICO', 'SAT', 'Mexico'],
  openGraph: {
    title: 'HERMES para Contadores',
    description: 'Normatividad fiscal MX + reportes automáticos. Sin leer PDFs. Sin multas.',
    type: 'website',
  },
}

export default function ContadoresLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
