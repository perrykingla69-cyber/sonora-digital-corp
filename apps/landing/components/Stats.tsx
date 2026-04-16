'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const stats = [
  { value: 500, label: 'Empresas', suffix: '+' },
  { value: 2.3, label: 'Transacciones', suffix: 'M+' },
  { value: 99.9, label: 'Uptime', suffix: '%' },
]

export function Stats() {
  const containerRef = useRef<HTMLDivElement>(null)
  const refs = useRef<HTMLDivElement[]>([])

  useEffect(() => {
    refs.current.forEach((ref, index) => {
      const stat = stats[index]
      const countElement = ref.querySelector('[data-count]')

      if (!countElement) return

      gsap.fromTo(
        { value: 0 },
        {
          value: stat.value,
          duration: 2,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 70%',
            toggleActions: 'play none none none',
          },
          onUpdate(self) {
            const currentValue = self.progress() === 1
              ? stat.value
              : Math.floor(self.targets()[0].value * 10) / 10

            countElement.textContent =
              stat.label === 'Transacciones'
                ? currentValue.toFixed(1)
                : Math.floor(currentValue).toString()
          },
        }
      )
    })
  }, [])

  return (
    <section
      ref={containerRef}
      className="relative w-full py-32 bg-primary-dark overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
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
            NÚMEROS QUE HABLAN
          </motion.p>
          <h2 className="text-h2 font-display font-bold text-light">
            Prueba de nuestro<span className="gradient-text"> impacto</span>
          </h2>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              ref={(el) => {
                if (el) refs.current[index] = el
              }}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="relative p-8 text-center"
            >
              {/* Background card */}
              <div className="absolute inset-0 bg-card-gradient rounded-2xl border border-accent/20 -z-10"></div>

              {/* Content */}
              <motion.div
                initial={{ scale: 0.5 }}
                whileInView={{ scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 + 0.2 }}
              >
                <div className="text-6xl font-display font-bold gradient-text">
                  <span data-count>0</span>
                  <span className="text-accent">{stat.suffix}</span>
                </div>
                <p className="text-light/60 text-lg mt-4">{stat.label}</p>
              </motion.div>
            </motion.div>
          ))}
        </div>

        {/* Divider */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="my-16 h-px bg-gradient-to-r from-transparent via-accent to-transparent opacity-30"
        />

        {/* Trust metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center"
        >
          {[
            { icon: '✓', label: 'Certificado ISO 27001' },
            { icon: '🔒', label: 'Encriptación AES-256' },
            { icon: '📊', label: 'Analytics en tiempo real' },
            { icon: '⚡', label: 'API ultra-rápida' },
          ].map((item, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -5 }}
              className="text-light/50 text-sm"
            >
              <p className="text-2xl mb-2">{item.icon}</p>
              {item.label}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
