'use client'

import { ReactNode } from 'react'

interface HeroProps {
  badge?: string
  title: ReactNode
  subtitle: string
  cta: {
    text: string
    href: string
  }
  variant?: 'contador' | 'artista' | 'general'
}

export function Hero({ badge, title, subtitle, cta, variant = 'general' }: HeroProps) {
  const bgColor = variant === 'contador' ? 'bg-blue-900/20' : variant === 'artista' ? 'bg-purple-900/20' : 'bg-white/5'
  const accentColor = variant === 'contador' ? 'text-blue-400' : variant === 'artista' ? 'text-purple-400' : 'text-[#D4AF37]'

  return (
    <section className="relative min-h-[80vh] flex flex-col items-center justify-center text-center px-4 py-20">
      {badge && (
        <div className={`mb-8 inline-flex items-center gap-2 ${bgColor} border border-white/20 rounded-full px-5 py-2`}>
          <span className={`text-sm font-semibold ${accentColor}`}>{badge}</span>
        </div>
      )}

      <h1 className={`text-5xl sm:text-6xl font-black leading-tight mb-6 max-w-3xl`}>
        {title}
      </h1>

      <p className="text-lg sm:text-xl text-white/60 mb-10 max-w-2xl leading-relaxed">
        {subtitle}
      </p>

      <button
        onClick={() => window.location.href = cta.href}
        className={`px-8 py-4 rounded-xl font-bold text-base hover:scale-105 transition ${
          variant === 'contador'
            ? 'bg-blue-500 text-white hover:bg-blue-600'
            : variant === 'artista'
            ? 'bg-purple-500 text-white hover:bg-purple-600'
            : 'bg-[#D4AF37] text-black hover:bg-[#f0c842]'
        }`}
      >
        {cta.text} →
      </button>

      <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-white/40">
        <span>✓ Sin configuración</span>
        <span>✓ Resultado inmediato</span>
        <span>✓ Garantizado</span>
      </div>
    </section>
  )
}
