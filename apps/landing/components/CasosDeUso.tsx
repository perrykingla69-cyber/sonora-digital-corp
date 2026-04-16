'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

const casos = [
  {
    id: 1,
    titulo: 'Pastelería',
    descripcion: 'Recibe pedidos, gestiona horarios y confirma entregas automáticamente.',
    icon: '🧁',
    color: 'from-pink-500 to-rose-600',
    features: ['Pedidos 24/7', 'Confirmación automática', 'Recordatorios entrega'],
  },
  {
    id: 2,
    titulo: 'Restaurante',
    descripcion: 'Reservas, menú interactivo y atención al cliente en tiempo real.',
    icon: '🍽️',
    color: 'from-orange-500 to-amber-600',
    features: ['Reservas en línea', 'Menú digital', 'Soporte 24/7'],
  },
  {
    id: 3,
    titulo: 'Abogado',
    descripcion: 'Consultorías iniciales, seguimiento de casos y documentación automática.',
    icon: '⚖️',
    color: 'from-blue-500 to-indigo-600',
    features: ['Consultas iniciales', 'Seguimiento de casos', 'Docs automáticas'],
  },
]

export function CasosDeUso() {
  const [hoveredId, setHoveredId] = useState<number | null>(null)

  return (
    <section id="casos" className="relative w-full py-32 bg-primary-dark overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl"></div>
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
            CASOS DE USO
          </motion.p>
          <h2 className="text-h2 font-display font-bold text-light mb-4">
            Automatiza cualquier{' '}
            <span className="gradient-text">negocio</span>
          </h2>
          <p className="text-light/60 max-w-2xl mx-auto">
            Desde restaurantes hasta despachos legales, nuestros agentes se adaptan a tu industria.
          </p>
        </motion.div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {casos.map((caso, index) => (
            <motion.div
              key={caso.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              onHoverStart={() => setHoveredId(caso.id)}
              onHoverEnd={() => setHoveredId(null)}
              className="group relative"
            >
              {/* Card */}
              <motion.div
                animate={{
                  y: hoveredId === caso.id ? -10 : 0,
                  boxShadow:
                    hoveredId === caso.id
                      ? '0 20px 40px rgba(0, 217, 255, 0.2)'
                      : '0 0 20px rgba(0, 217, 255, 0.1)',
                }}
                transition={{ duration: 0.3 }}
                className="relative p-8 bg-card-gradient rounded-2xl border border-accent/20 hover:border-accent/50 transition-colors h-full"
              >
                {/* Background gradient */}
                <motion.div
                  animate={{
                    opacity: hoveredId === caso.id ? 1 : 0,
                  }}
                  transition={{ duration: 0.3 }}
                  className={`absolute inset-0 bg-gradient-to-br ${caso.color} opacity-0 rounded-2xl blur-xl -z-10`}
                />

                {/* Icon */}
                <motion.div
                  animate={{
                    scale: hoveredId === caso.id ? 1.2 : 1,
                    rotate: hoveredId === caso.id ? 10 : 0,
                  }}
                  transition={{ duration: 0.3 }}
                  className="text-5xl mb-6 origin-left"
                >
                  {caso.icon}
                </motion.div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-light mb-3">
                  {caso.titulo}
                </h3>
                <p className="text-light/60 mb-6 leading-relaxed">
                  {caso.descripcion}
                </p>

                {/* Features */}
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{
                    opacity: hoveredId === caso.id ? 1 : 0,
                    height: hoveredId === caso.id ? 'auto' : 0,
                  }}
                  transition={{ duration: 0.3 }}
                  className="space-y-2 overflow-hidden"
                >
                  {caso.features.map((feature, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-accent text-sm"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
                      {feature}
                    </div>
                  ))}
                </motion.div>

                {/* CTA */}
                <motion.button
                  animate={{
                    opacity: hoveredId === caso.id ? 1 : 0,
                  }}
                  transition={{ duration: 0.3 }}
                  className="mt-6 text-accent hover:text-white text-sm font-semibold transition-colors"
                >
                  Ver más →
                </motion.button>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
