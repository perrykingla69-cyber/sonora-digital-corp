'use client'

/**
 * AntesDespues — Sección visual antes/después para músicos.
 *
 * Muestra dos columnas contrastadas:
 * - ANTES: caos manual (WhatsApp, hojas de cálculo, stress)
 * - DESPUÉS: automatización HERMES (todo fluye solo)
 *
 * Animaciones: stagger fade-in al entrar en viewport.
 */

import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

interface PainPoint {
  icon: string
  text: string
}

interface GainPoint {
  icon: string
  text: string
}

const PAIN_POINTS: PainPoint[] = [
  { icon: '😩', text: 'Horas respondiendo WhatsApp de clientes' },
  { icon: '📊', text: 'Hojas de cálculo imposibles de mantener' },
  { icon: '💸', text: 'Sin idea de cuánto ganas por royalties' },
  { icon: '📱', text: 'Post manual en redes — agotador' },
  { icon: '🎤', text: 'Booking por DM sin sistema ni contrato' },
]

const GAIN_POINTS: GainPoint[] = [
  { icon: '🤖', text: 'Bot responde y agenda por ti, 24/7' },
  { icon: '📈', text: 'Dashboard con ingresos en tiempo real' },
  { icon: '💰', text: 'Royalties trackeados automáticamente' },
  { icon: '🎨', text: 'Contenido generado por IA en segundos' },
  { icon: '📅', text: 'Contratos y pagos procesados solos' },
]

/** Tarjeta de columna (antes/después) */
function Column({
  title,
  subtitle,
  items,
  variant,
  delay,
}: {
  title: string
  subtitle: string
  items: Array<{ icon: string; text: string }>
  variant: 'before' | 'after'
  delay: number
}) {
  const isBefore = variant === 'before'

  return (
    <motion.div
      initial={{ opacity: 0, x: isBefore ? -30 : 30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.6, delay }}
      className={`
        relative rounded-2xl p-8 border
        ${isBefore
          ? 'bg-red-950/20 border-red-500/20'
          : 'bg-green-950/20 border-green-500/20'
        }
      `}
      role="region"
      aria-label={`Situación ${isBefore ? 'actual (antes)' : 'con HERMES (después)'}`}
    >
      {/* Header */}
      <div className={`
        inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-semibold mb-4
        ${isBefore ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}
      `}>
        <span aria-hidden="true">{isBefore ? '😰' : '✨'}</span>
        {title}
      </div>

      <p className={`text-sm mb-6 ${isBefore ? 'text-red-300/60' : 'text-green-300/60'}`}>
        {subtitle}
      </p>

      {/* Items */}
      <ul className="space-y-4" role="list">
        {items.map((item, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: delay + 0.1 * i }}
            className="flex items-start gap-3"
          >
            <span className="text-xl flex-shrink-0" aria-hidden="true">{item.icon}</span>
            <span className="text-white/70 text-sm leading-relaxed">{item.text}</span>
          </motion.li>
        ))}
      </ul>
    </motion.div>
  )
}

export default function AntesDespues() {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section
      ref={ref}
      className="py-24 px-6 max-w-5xl mx-auto"
      aria-labelledby="antes-despues-heading"
    >
      {/* Título */}
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <span className="text-accent text-sm font-medium tracking-widest uppercase">
          El cambio es real
        </span>
        <h2
          id="antes-despues-heading"
          className="font-display text-3xl sm:text-4xl font-bold text-white mt-3"
        >
          De administrar a{' '}
          <span className="gradient-text">crear</span>
        </h2>
        <p className="text-white/50 mt-4 max-w-xl mx-auto">
          Deja de perder tiempo en tareas administrativas. HERMES las hace por ti
          mientras tú te enfocas en la música.
        </p>
      </motion.div>

      {/* Columnas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Column
          title="SIN HERMES"
          subtitle="Tu día a día sin automatización"
          items={PAIN_POINTS}
          variant="before"
          delay={0}
        />
        <Column
          title="CON HERMES"
          subtitle="Tu día a día automatizado"
          items={GAIN_POINTS}
          variant="after"
          delay={0.15}
        />
      </div>

      {/* Arrow connector en desktop */}
      <div
        className="hidden md:flex absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10 pointer-events-none"
        aria-hidden="true"
      >
        <div className="w-12 h-12 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center">
          <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>
      </div>
    </section>
  )
}
