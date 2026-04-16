'use client'

/**
 * TestimoniosCarousel — Carousel de testimonios de músicos.
 *
 * - Deslizamiento suave con Framer Motion
 * - Auto-play cada 5s
 * - Navegación manual con dots + flechas
 * - Accesible: roles ARIA correctos, focus visible
 * - Mobile-first: swipe funcional con drag
 */

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Testimonio {
  id: string
  nombre: string
  rol: string
  ciudad: string
  texto: string
  rating: number
  avatarInitial: string
  accentColor: string
}

/** Testimonios mock — reemplazar con datos reales de API */
const TESTIMONIOS: Testimonio[] = [
  {
    id: '1',
    nombre: 'Marco Ríos',
    rol: 'Productor Musical',
    ciudad: 'Monterrey, NL',
    texto:
      'Antes pasaba 3 horas diarias respondiendo WhatsApp de clientes. Con HERMES el bot lo hace todo solo. Ahora solo me enfoco en producir. Mis ingresos subieron 40% en 2 meses.',
    rating: 5,
    avatarInitial: 'M',
    accentColor: '#00D9FF',
  },
  {
    id: '2',
    nombre: 'Daniela Torres',
    rol: 'Cantautora',
    ciudad: 'CDMX',
    texto:
      'El tracker de royalties me salvó la vida. Finalmente sé exactamente cuánto me paga Spotify cada mes y de qué canciones. El reporte fiscal automático es oro puro.',
    rating: 5,
    avatarInitial: 'D',
    accentColor: '#6D28D9',
  },
  {
    id: '3',
    nombre: 'Los Sabaneros',
    rol: 'Banda de Regional Mexicano',
    ciudad: 'Culiacán, SIN',
    texto:
      'Somos 5 integrantes y ya no peleamos por cómo repartir ingresos — el dashboard lo hace automático. El bot agenda nuestras presentaciones y cobra el anticipo solo.',
    rating: 5,
    avatarInitial: 'L',
    accentColor: '#10B981',
  },
  {
    id: '4',
    nombre: 'DJ Phantom',
    rol: 'DJ Electrónico',
    ciudad: 'Guadalajara, JAL',
    texto:
      'Conecté mi Spotify y en 5 minutos vi que 3 de mis tracks estaban en playlists que no sabía. Eso me abrió puertas para contactar a los curadores directamente. Game changer.',
    rating: 5,
    avatarInitial: 'P',
    accentColor: '#F59E0B',
  },
  {
    id: '5',
    nombre: 'Beatriz Salinas',
    rol: 'Beatmaker & Productora',
    ciudad: 'Tijuana, BC',
    texto:
      'Vendo beats en mi bot de WhatsApp. El cliente elige, paga por Mercado Pago y recibe el archivo automático. Llevo 3 meses sin intervenir en ninguna venta. Increíble.',
    rating: 5,
    avatarInitial: 'B',
    accentColor: '#EC4899',
  },
]

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5" aria-label={`Calificación: ${rating} de 5 estrellas`} role="img">
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          className={`w-4 h-4 ${i < rating ? 'text-yellow-400' : 'text-white/20'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
    </div>
  )
}

export default function TestimoniosCarousel() {
  const [current, setCurrent] = useState(0)
  const [paused, setPaused] = useState(false)

  const prev = useCallback(() => {
    setCurrent((c) => (c - 1 + TESTIMONIOS.length) % TESTIMONIOS.length)
  }, [])

  const next = useCallback(() => {
    setCurrent((c) => (c + 1) % TESTIMONIOS.length)
  }, [])

  /** Auto-play cada 5s */
  useEffect(() => {
    if (paused) return
    const id = setInterval(next, 5000)
    return () => clearInterval(id)
  }, [paused, next])

  const testimonio = TESTIMONIOS[current]

  return (
    <section
      className="py-24 px-6 bg-dark-bg/50"
      aria-labelledby="testimonios-heading"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-14"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <span className="text-accent text-sm font-medium tracking-widest uppercase">
            Lo dicen ellos
          </span>
          <h2
            id="testimonios-heading"
            className="font-display text-3xl sm:text-4xl font-bold text-white mt-3"
          >
            Músicos que ya{' '}
            <span className="gradient-text">crecen sin límites</span>
          </h2>
        </motion.div>

        {/* Carousel */}
        <div
          className="relative"
          role="region"
          aria-roledescription="carrusel"
          aria-label="Testimonios de músicos"
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={testimonio.id}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.35 }}
              className="glass-effect rounded-2xl p-8 sm:p-10"
              drag="x"
              dragConstraints={{ left: 0, right: 0 }}
              dragElastic={0.2}
              onDragEnd={(_, info) => {
                if (info.offset.x < -50) next()
                else if (info.offset.x > 50) prev()
              }}
              aria-live="polite"
              aria-atomic="true"
            >
              {/* Quote */}
              <div
                className="text-5xl text-accent/30 font-serif leading-none mb-4 select-none"
                aria-hidden="true"
              >
                &ldquo;
              </div>

              <blockquote>
                <p className="text-white/80 text-lg leading-relaxed mb-8">
                  {testimonio.texto}
                </p>
              </blockquote>

              {/* Autor */}
              <div className="flex items-center gap-4">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                  style={{ backgroundColor: testimonio.accentColor + '40', border: `2px solid ${testimonio.accentColor}50` }}
                  aria-hidden="true"
                >
                  {testimonio.avatarInitial}
                </div>
                <div>
                  <div className="font-semibold text-white">{testimonio.nombre}</div>
                  <div className="text-sm text-white/50">{testimonio.rol} · {testimonio.ciudad}</div>
                  <div className="mt-1">
                    <StarRating rating={testimonio.rating} />
                  </div>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Botones navegación */}
          <div className="flex items-center justify-between mt-8">
            <button
              onClick={prev}
              className="
                w-10 h-10 rounded-full border border-white/20 flex items-center justify-center
                text-white/60 hover:text-white hover:border-accent/50
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-primary-dark
              "
              aria-label="Testimonio anterior"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Dots */}
            <div className="flex gap-2" role="tablist" aria-label="Seleccionar testimonio">
              {TESTIMONIOS.map((t, i) => (
                <button
                  key={t.id}
                  onClick={() => setCurrent(i)}
                  role="tab"
                  aria-selected={i === current}
                  aria-label={`Testimonio de ${t.nombre}`}
                  className={`
                    rounded-full transition-all duration-300
                    focus:outline-none focus:ring-2 focus:ring-accent
                    ${i === current
                      ? 'w-6 h-2 bg-accent'
                      : 'w-2 h-2 bg-white/30 hover:bg-white/50'
                    }
                  `}
                />
              ))}
            </div>

            <button
              onClick={next}
              className="
                w-10 h-10 rounded-full border border-white/20 flex items-center justify-center
                text-white/60 hover:text-white hover:border-accent/50
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-primary-dark
              "
              aria-label="Testimonio siguiente"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
