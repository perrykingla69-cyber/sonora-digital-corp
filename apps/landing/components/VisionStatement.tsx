'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function VisionStatement() {
  const textRef = useRef<HTMLHeadingElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!textRef.current || !containerRef.current) return

    // Scan effect - clip-path animation from left to right
    gsap.fromTo(
      textRef.current,
      {
        clipPath: 'polygon(0 0, 0 0, 0 100%, 0 100%)',
      },
      {
        clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
        duration: 1.5,
        ease: 'power2.inOut',
        scrollTrigger: {
          trigger: containerRef.current,
          start: 'top 70%',
          toggleActions: 'play none none none',
          markers: false,
        },
      }
    )

    // Light scan effect overlay
    const scanLight = document.createElement('div')
    scanLight.className = 'scan-light'
    if (containerRef.current) {
      containerRef.current.appendChild(scanLight)
    }

    gsap.to(scanLight, {
      left: '100%',
      duration: 1.5,
      ease: 'power2.inOut',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 70%',
        toggleActions: 'play none none none',
      },
    })

    return () => {
      scanLight.remove()
    }
  }, [])

  return (
    <section
      ref={containerRef}
      className="relative w-full py-32 bg-primary-dark overflow-hidden"
    >
      {/* Background elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-secondary rounded-full mix-blend-multiply filter blur-3xl"></div>
      </div>

      <style>{`
        .scan-light {
          position: absolute;
          top: 0;
          left: 0;
          width: 80px;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(0, 217, 255, 0.3), transparent);
          pointer-events: none;
          z-index: 10;
        }
      `}</style>

      <div className="relative z-20 max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-8"
        >
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-accent font-mono text-sm tracking-widest"
          >
            NUESTRA VISIÓN
          </motion.p>

          <h2
            ref={textRef}
            className="text-5xl lg:text-6xl font-display font-bold text-light leading-tight"
          >
            Cada negocio merece un asistente IA.{' '}
            <span className="gradient-text">Sin código. Sin setup. Sin límites.</span>
          </h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-light/60 max-w-2xl mx-auto font-light"
          >
            Transformamos la forma en que los negocios operan. Una plataforma. Un
            agent. Infinitas posibilidades.
          </motion.p>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="grid grid-cols-3 gap-6 pt-8 max-w-2xl mx-auto"
          >
            {[
              { value: '99.9%', label: 'Uptime' },
              { value: '<1ms', label: 'Latencia' },
              { value: '∞', label: 'Escala' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl font-mono font-bold text-accent">
                  {stat.value}
                </p>
                <p className="text-light/50 text-sm mt-2">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
