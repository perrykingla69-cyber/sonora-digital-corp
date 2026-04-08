'use client'

import { LucideIcon } from 'lucide-react'

interface Feature {
  icon: LucideIcon
  title: string
  description: string
}

interface FeaturesProps {
  features: Feature[]
  variant?: 'contador' | 'artista' | 'general'
  title?: string
}

export function Features({ features, variant = 'general', title = 'Funcionalidades' }: FeaturesProps) {
  const accentColor = variant === 'contador' ? 'bg-blue-500/10 text-blue-400' : variant === 'artista' ? 'bg-purple-500/10 text-purple-400' : 'bg-[#D4AF37]/10 text-[#D4AF37]'
  const borderHover = variant === 'contador' ? 'hover:border-blue-400/30' : variant === 'artista' ? 'hover:border-purple-400/30' : 'hover:border-[#D4AF37]/30'

  return (
    <section className="relative py-20 px-4 max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl sm:text-4xl font-black">{title}</h2>
      </div>

      <div className="grid sm:grid-cols-2 gap-6">
        {features.map(({ icon: Icon, title: featureTitle, description }) => (
          <div
            key={featureTitle}
            className={`bg-white/5 border border-white/10 rounded-2xl p-6 flex gap-4 transition ${borderHover}`}
          >
            <div className={`shrink-0 w-12 h-12 rounded-xl ${accentColor} flex items-center justify-center`}>
              <Icon className="w-6 h-6" />
            </div>
            <div className="text-left">
              <h3 className="font-bold text-white mb-2">{featureTitle}</h3>
              <p className="text-sm text-white/50 leading-relaxed">{description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
