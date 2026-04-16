'use client'

/**
 * HeroMusicos — Sección hero personalizada por artista/nicho musical.
 *
 * Soporta:
 * - gradient animado negro→púrpura (Framer Motion)
 * - Nombre artista + avatar dinámico
 * - Subtítulo personalizado según subtipo (productor, beatmaker, etc.)
 * - CTA principal con efecto glow
 * - Partículas flotantes de fondo
 */

import { motion } from 'framer-motion'
import Image from 'next/image'

export type MusicoSubtype = 'productor' | 'beatmaker' | 'cantante' | 'dj' | 'banda' | 'general'

interface HeroMusicosProps {
  /** Nombre artístico del músico */
  artistName?: string
  /** URL del avatar/foto del artista */
  avatarUrl?: string
  /** Subtipo para personalizar el mensaje */
  subtype?: MusicoSubtype
  /** Slug para el link del CTA */
  slug: string
}

/** Subtítulos personalizados por subtipo */
const SUBTITLES: Record<MusicoSubtype, string> = {
  productor: 'Administra tus beats, clientes y regalías desde un solo lugar. Sin hojas de cálculo, sin caos.',
  beatmaker: 'Vende tus beats 24/7, automatiza seguimientos y cobra sin intermediarios.',
  cantante: 'Gestiona bookings, contratos y royalties mientras te enfocas en tu música.',
  dj: 'Automatiza cotizaciones, agenda fechas y trackea tus ingresos por evento.',
  banda: 'Coordina tu banda, fechas en vivo y distribución de ganancias sin dramas.',
  general: 'Gestiona tu carrera musical con inteligencia artificial. Booking, promo y finanzas automáticas.',
}

/** Partícula flotante para el fondo */
function Particle({ x, y, delay, size }: { x: number; y: number; delay: number; size: number }) {
  return (
    <motion.div
      className="absolute rounded-full bg-accent/20 pointer-events-none"
      style={{ left: `${x}%`, top: `${y}%`, width: size, height: size }}
      animate={{
        y: [0, -20, 0],
        opacity: [0.2, 0.6, 0.2],
      }}
      transition={{
        duration: 4 + delay,
        repeat: Infinity,
        delay,
        ease: 'easeInOut',
      }}
    />
  )
}

const PARTICLES = [
  { x: 10, y: 20, delay: 0, size: 6 },
  { x: 80, y: 15, delay: 1.2, size: 4 },
  { x: 50, y: 70, delay: 2.1, size: 8 },
  { x: 30, y: 85, delay: 0.7, size: 5 },
  { x: 90, y: 60, delay: 1.8, size: 3 },
  { x: 65, y: 35, delay: 3.0, size: 7 },
  { x: 15, y: 55, delay: 2.5, size: 4 },
]

export default function HeroMusicos({
  artistName,
  avatarUrl,
  subtype = 'general',
  slug,
}: HeroMusicosProps) {
  const subtitle = SUBTITLES[subtype]

  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      aria-label="Hero principal"
    >
      {/* Fondo animado negro → púrpura */}
      <motion.div
        className="absolute inset-0 z-0"
        animate={{
          background: [
            'linear-gradient(135deg, #0F0F0F 0%, #1a0a2e 50%, #0F0F0F 100%)',
            'linear-gradient(135deg, #0F0F0F 0%, #2d1060 50%, #0c1a40 100%)',
            'linear-gradient(135deg, #0F0F0F 0%, #1a0a2e 50%, #0F0F0F 100%)',
          ],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Mesh gradient overlay */}
      <div className="absolute inset-0 z-0 opacity-30"
        style={{
          backgroundImage: 'radial-gradient(ellipse at 20% 50%, #6D28D9 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, #00D9FF 0%, transparent 50%)',
        }}
      />

      {/* Partículas */}
      {PARTICLES.map((p, i) => (
        <Particle key={i} {...p} />
      ))}

      {/* Contenido */}
      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">

        {/* Avatar + nombre artista (condicional) */}
        {(artistName || avatarUrl) && (
          <motion.div
            className="flex flex-col items-center gap-3 mb-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {avatarUrl && (
              <div className="relative w-20 h-20 rounded-full border-2 border-accent shadow-glow overflow-hidden">
                <Image
                  src={avatarUrl}
                  alt={artistName ?? 'Avatar artista'}
                  fill
                  className="object-cover"
                  sizes="80px"
                />
              </div>
            )}
            {artistName && (
              <span className="text-accent text-sm font-medium tracking-widest uppercase">
                {artistName}
              </span>
            )}
          </motion.div>
        )}

        {/* Heading principal */}
        <motion.h1
          className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
        >
          Tu asistente musical.{' '}
          <span className="gradient-text">
            Booking, promo, royalties.
          </span>{' '}
          Automático.
        </motion.h1>

        {/* Subtítulo personalizado */}
        <motion.p
          className="text-white/70 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25 }}
        >
          {subtitle}
        </motion.p>

        {/* CTA */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          <a
            href={`/dashboard/musicos/mi-musica?slug=${slug}`}
            className="
              inline-flex items-center justify-center gap-2
              px-8 py-4 rounded-xl font-semibold text-lg
              bg-accent text-primary-dark
              shadow-glow hover:shadow-glow-lg
              hover:scale-105 active:scale-95
              transition-all duration-300
              focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-primary-dark
            "
            aria-label="Acceder a mi panel de músico"
          >
            Acceder a mi panel
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>

          <a
            href="#features"
            className="
              inline-flex items-center justify-center gap-2
              px-8 py-4 rounded-xl font-semibold text-lg
              border border-white/20 text-white/80
              hover:border-accent/50 hover:text-white hover:bg-white/5
              transition-all duration-300
              focus:outline-none focus:ring-2 focus:ring-white/30
            "
          >
            Ver cómo funciona
          </a>
        </motion.div>

        {/* Trust badge */}
        <motion.p
          className="mt-8 text-white/30 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          Sin tarjeta de crédito · 24h gratis · Cancela cuando quieras
        </motion.p>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        aria-hidden="true"
      >
        <svg className="w-6 h-6 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
        </svg>
      </motion.div>
    </section>
  )
}
