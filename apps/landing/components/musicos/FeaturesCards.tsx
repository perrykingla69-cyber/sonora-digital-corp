'use client'

/**
 * FeaturesCards — 4 tarjetas de características para músicos.
 *
 * Características:
 * 1. Bot Telegram/WhatsApp (Booking automático)
 * 2. Spotify integrado (Stats, playlist placements)
 * 3. Content Suite (Copy + fotos + videos)
 * 4. Gestión ingresos (Royalties, reportes)
 *
 * Animación: stagger al entrar en viewport, hover lift.
 */

import { motion } from 'framer-motion'

interface Feature {
  icon: string
  title: string
  description: string
  tags: string[]
  accentColor: string
}

const FEATURES: Feature[] = [
  {
    icon: '📱',
    title: 'Bot Telegram / WhatsApp',
    description:
      'Tu asistente virtual responde consultas, agenda presentaciones y procesa pagos automáticamente — sin que tengas que tocar el teléfono.',
    tags: ['Booking 24/7', 'Respuesta automática', 'Pagos integrados'],
    accentColor: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
  },
  {
    icon: '📊',
    title: 'Spotify Integrado',
    description:
      'Visualiza tus streams, oyentes mensuales y ubicación de fans en tiempo real. Detecta playlists con potencial y actúa al instante.',
    tags: ['Stats en vivo', 'Playlist radar', 'Fan locations'],
    accentColor: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
  },
  {
    icon: '🎨',
    title: 'Content Suite',
    description:
      'Genera copy para redes, variaciones de fotos y templates de video con IA. Publica en todos tus canales desde un solo lugar.',
    tags: ['Copy IA', 'Fotos IA', 'Video templates'],
    accentColor: 'from-purple-500/20 to-pink-500/20 border-purple-500/30',
  },
  {
    icon: '💰',
    title: 'Gestión de Ingresos',
    description:
      'Trackea royalties de streaming, ventas de beats y fees de presentaciones. Genera reportes fiscales automáticos cada mes.',
    tags: ['Royalties tracker', 'Reportes fiscales', 'Multi-fuente'],
    accentColor: 'from-yellow-500/20 to-orange-500/20 border-yellow-500/30',
  },
]

interface FeatureCardProps {
  feature: Feature
  index: number
}

function FeatureCard({ feature, index }: FeatureCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -6, transition: { duration: 0.2 } }}
      className={`
        relative rounded-2xl p-7 border bg-gradient-to-br
        ${feature.accentColor}
        hover:shadow-glow transition-shadow duration-300
        cursor-default
      `}
      aria-label={`Característica: ${feature.title}`}
    >
      {/* Icono */}
      <div className="text-4xl mb-5" aria-hidden="true">
        {feature.icon}
      </div>

      {/* Título */}
      <h3 className="font-display text-xl font-semibold text-white mb-3">
        {feature.title}
      </h3>

      {/* Descripción */}
      <p className="text-white/60 text-sm leading-relaxed mb-6">
        {feature.description}
      </p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2" role="list" aria-label="Funcionalidades incluidas">
        {feature.tags.map((tag) => (
          <span
            key={tag}
            role="listitem"
            className="
              px-3 py-1 rounded-full text-xs font-medium
              bg-white/10 text-white/70 border border-white/10
            "
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Corner glow */}
      <div
        className="absolute top-0 right-0 w-24 h-24 rounded-bl-full opacity-10 pointer-events-none"
        style={{ background: 'radial-gradient(circle, #00D9FF, transparent)' }}
        aria-hidden="true"
      />
    </motion.article>
  )
}

export default function FeaturesCards() {
  return (
    <section
      id="features"
      className="py-24 px-6 max-w-6xl mx-auto"
      aria-labelledby="features-heading"
    >
      {/* Header */}
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
      >
        <span className="text-accent text-sm font-medium tracking-widest uppercase">
          Todo en uno
        </span>
        <h2
          id="features-heading"
          className="font-display text-3xl sm:text-4xl font-bold text-white mt-3"
        >
          Herramientas que{' '}
          <span className="gradient-text">potencian tu carrera</span>
        </h2>
        <p className="text-white/50 mt-4 max-w-xl mx-auto">
          Una plataforma diseñada específicamente para músicos mexicanos que
          quieren crecer sin contratar un equipo de administración.
        </p>
      </motion.div>

      {/* Grid de tarjetas */}
      <div
        className="grid grid-cols-1 sm:grid-cols-2 gap-6"
        role="list"
        aria-label="Lista de características"
      >
        {FEATURES.map((feature, i) => (
          <FeatureCard key={feature.title} feature={feature} index={i} />
        ))}
      </div>
    </section>
  )
}
