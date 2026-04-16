'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'

const testimonios = [
  {
    id: 1,
    quote: 'Implementar Sonora fue la mejor decisión. Ahora recibimos pedidos 24/7 sin intervención manual.',
    author: 'María García',
    company: 'Pastelería La Flor',
    rating: 5,
    avatar: '👩‍💼',
  },
  {
    id: 2,
    quote: 'El ROI en 3 meses fue increíble. Triplicamos nuestras ventas online sin aumentar staff.',
    author: 'Carlos López',
    company: 'Restaurante Casa Mar',
    rating: 5,
    avatar: '👨‍💼',
  },
  {
    id: 3,
    quote: 'Antes atendía consultas manuales. Ahora el agent lo hace. Más tiempo para lo importante.',
    author: 'Dra. Patricia Ruiz',
    company: 'Despacho Jurídico Ruiz',
    rating: 5,
    avatar: '👩‍⚖️',
  },
  {
    id: 4,
    quote: 'Soporte excepcional. El equipo de Sonora está siempre disponible para ayudar.',
    author: 'Juan Martínez',
    company: 'Constructora JM',
    rating: 5,
    avatar: '👷‍♂️',
  },
]

interface TestimonioCardProps {
  testimonio: typeof testimonios[0]
  isHovered: boolean
  onHover: () => void
  onHoverEnd: () => void
}

function TestimonioCard({
  testimonio,
  isHovered,
  onHover,
  onHoverEnd,
}: TestimonioCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [glowPos, setGlowPos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    if (!cardRef.current || !isHovered) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!cardRef.current) return

      const rect = cardRef.current.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      setMousePos({ x, y })
      setGlowPos({ x: x - 40, y: y - 40 })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [isHovered])

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      onHoverStart={onHover}
      onHoverEnd={onHoverEnd}
      className="relative h-full"
    >
      {/* Glow effect that follows cursor */}
      <motion.div
        animate={isHovered ? { opacity: 1 } : { opacity: 0 }}
        style={{
          left: glowPos.x,
          top: glowPos.y,
        }}
        className="absolute w-24 h-24 bg-accent rounded-full mix-blend-screen filter blur-3xl pointer-events-none z-0"
      />

      {/* Card */}
      <motion.div
        animate={{
          y: isHovered ? -10 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="relative p-8 bg-card-gradient rounded-2xl border border-accent/20 hover:border-accent/50 transition-colors h-full flex flex-col"
      >
        {/* Stars */}
        <div className="flex gap-1 mb-4">
          {Array(testimonio.rating)
            .fill(0)
            .map((_, i) => (
              <span key={i} className="text-lg">
                ⭐
              </span>
            ))}
        </div>

        {/* Quote */}
        <motion.p
          animate={{
            color: isHovered ? '#00D9FF' : '#F5F5F5',
          }}
          transition={{ duration: 0.3 }}
          className="text-light/80 italic flex-1 mb-6 leading-relaxed"
        >
          "{testimonio.quote}"
        </motion.p>

        {/* Author */}
        <div className="flex items-center gap-4 mt-auto">
          <div className="text-4xl">{testimonio.avatar}</div>
          <div>
            <p className="font-semibold text-light">{testimonio.author}</p>
            <p className="text-light/50 text-sm">{testimonio.company}</p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export function Testimonios() {
  const [hoveredId, setHoveredId] = useState<number | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)

  const checkScroll = () => {
    if (containerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = containerRef.current
      setCanScrollLeft(scrollLeft > 0)
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
    }
  }

  useEffect(() => {
    checkScroll()
    const container = containerRef.current
    container?.addEventListener('scroll', checkScroll)
    return () => container?.removeEventListener('scroll', checkScroll)
  }, [])

  const scroll = (direction: 'left' | 'right') => {
    if (!containerRef.current) return
    const amount = 400
    containerRef.current.scrollBy({
      left: direction === 'left' ? -amount : amount,
      behavior: 'smooth',
    })
  }

  return (
    <section className="relative w-full py-32 bg-primary-dark overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-accent font-mono text-sm tracking-widest mb-4"
          >
            TESTIMONIOS
          </motion.p>
          <h2 className="text-h2 font-display font-bold text-light">
            Lo que dicen nuestros<span className="gradient-text"> clientes</span>
          </h2>
        </motion.div>

        {/* Carousel */}
        <div className="relative group">
          {/* Scroll container */}
          <div
            ref={containerRef}
            className="overflow-x-auto scrollbar-hide scroll-smooth"
          >
            <div className="flex gap-6 pb-4">
              {testimonios.map((testimonio) => (
                <div key={testimonio.id} className="flex-shrink-0 w-96">
                  <TestimonioCard
                    testimonio={testimonio}
                    isHovered={hoveredId === testimonio.id}
                    onHover={() => setHoveredId(testimonio.id)}
                    onHoverEnd={() => setHoveredId(null)}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Navigation buttons */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => scroll('left')}
            className={`absolute left-0 top-1/2 -translate-y-1/2 -translate-x-6 w-12 h-12 rounded-full flex items-center justify-center transition-all ${
              canScrollLeft
                ? 'bg-accent text-primary-dark hover:shadow-glow-lg'
                : 'bg-accent/30 text-light/30 cursor-not-allowed'
            }`}
            disabled={!canScrollLeft}
          >
            ←
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => scroll('right')}
            className={`absolute right-0 top-1/2 -translate-y-1/2 translate-x-6 w-12 h-12 rounded-full flex items-center justify-center transition-all ${
              canScrollRight
                ? 'bg-accent text-primary-dark hover:shadow-glow-lg'
                : 'bg-accent/30 text-light/30 cursor-not-allowed'
            }`}
            disabled={!canScrollRight}
          >
            →
          </motion.button>

          {/* Hide scrollbar */}
          <style>{`
            .scrollbar-hide {
              -ms-overflow-style: none;
              scrollbar-width: none;
            }
            .scrollbar-hide::-webkit-scrollbar {
              display: none;
            }
          `}</style>
        </div>
      </div>
    </section>
  )
}
