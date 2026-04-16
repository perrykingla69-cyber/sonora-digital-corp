'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

const pilares = [
  {
    id: 1,
    titulo: 'Automatización Inteligente',
    descripcion: 'Reduce tareas manuales en 80%. Nuestros agentes aprenden de cada interacción.',
    icon: '⚙️',
    position: 'left',
  },
  {
    id: 2,
    titulo: 'Vende 24/7',
    descripcion: 'No duerme. No se cansa. Captura cada oportunidad de negocio.',
    icon: '💰',
    position: 'right',
  },
  {
    id: 3,
    titulo: 'Integración Instantánea',
    descripcion: 'Conecta con WhatsApp, Telegram, tu sitio web. En minutos, no semanas.',
    icon: '🔗',
    position: 'left',
  },
  {
    id: 4,
    titulo: 'Análisis Profundo',
    descripcion: 'Entiende clientes, predice tendencias, toma decisiones basadas en datos.',
    icon: '📊',
    position: 'right',
  },
]

interface PilarProps {
  pilar: typeof pilares[0]
  index: number
}

function Pilar({ pilar, index }: PilarProps) {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  })

  const isLeft = pilar.position === 'left'

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: isLeft ? -50 : 50 }}
      animate={inView ? { opacity: 1, x: 0 } : { opacity: 0, x: isLeft ? -50 : 50 }}
      transition={{ duration: 0.8, delay: index * 0.1 }}
      className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center py-16"
    >
      {isLeft ? (
        <>
          {/* Left: Icon/Image */}
          <motion.div
            whileHover={{ scale: 1.05, rotate: 5 }}
            transition={{ duration: 0.3 }}
            className="relative h-64 md:h-80 flex items-center justify-center"
          >
            <div className="relative w-64 h-64 bg-gradient-to-br from-secondary to-accent/20 rounded-2xl border-2 border-accent/30 flex items-center justify-center">
              <div className="absolute inset-0 bg-card-gradient opacity-30 rounded-2xl"></div>
              <span className="text-8xl">{pilar.icon}</span>
            </div>
          </motion.div>

          {/* Right: Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.8, delay: index * 0.1 + 0.2 }}
            className="space-y-4"
          >
            <h3 className="text-4xl font-display font-bold text-light">
              {pilar.titulo}
            </h3>
            <p className="text-xl text-light/60 leading-relaxed">
              {pilar.descripcion}
            </p>
            <motion.button
              whileHover={{ x: 5 }}
              className="text-accent hover:text-white font-semibold mt-4 flex items-center gap-2"
            >
              Aprende más →
            </motion.button>
          </motion.div>
        </>
      ) : (
        <>
          {/* Right layout (reversed) */}
          {/* Left: Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.8, delay: index * 0.1 + 0.2 }}
            className="space-y-4 order-2 md:order-1"
          >
            <h3 className="text-4xl font-display font-bold text-light">
              {pilar.titulo}
            </h3>
            <p className="text-xl text-light/60 leading-relaxed">
              {pilar.descripcion}
            </p>
            <motion.button
              whileHover={{ x: -5 }}
              className="text-accent hover:text-white font-semibold mt-4 flex items-center gap-2"
            >
              ← Aprende más
            </motion.button>
          </motion.div>

          {/* Right: Icon/Image */}
          <motion.div
            whileHover={{ scale: 1.05, rotate: -5 }}
            transition={{ duration: 0.3 }}
            className="relative h-64 md:h-80 flex items-center justify-center order-1 md:order-2"
          >
            <div className="relative w-64 h-64 bg-gradient-to-br from-accent/20 to-secondary rounded-2xl border-2 border-accent/30 flex items-center justify-center">
              <div className="absolute inset-0 bg-card-gradient opacity-30 rounded-2xl"></div>
              <span className="text-8xl">{pilar.icon}</span>
            </div>
          </motion.div>
        </>
      )}
    </motion.div>
  )
}

export function Pilares() {
  return (
    <section className="relative w-full py-16 bg-primary-dark overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1/2 left-0 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl"></div>
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
            NUESTROS PILARES
          </motion.p>
          <h2 className="text-h2 font-display font-bold text-light">
            Tecnología que<span className="gradient-text"> impulsa tu negocio</span>
          </h2>
        </motion.div>

        {/* Pilares */}
        <div className="space-y-12">
          {pilares.map((pilar, index) => (
            <Pilar key={pilar.id} pilar={pilar} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}
