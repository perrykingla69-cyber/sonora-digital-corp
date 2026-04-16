'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import gsap from 'gsap'

export function Hero() {
  const botRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || !botRef.current) return

    // 3D light source follows scroll Y
    const handleScroll = () => {
      if (!botRef.current || !containerRef.current) return

      const scrollY = window.scrollY
      const containerTop = containerRef.current.offsetTop
      const relativeScroll = scrollY - containerTop

      gsap.to(botRef.current, {
        rotationY: (relativeScroll * 0.05) % 360,
        rotationX: Math.sin(relativeScroll * 0.01) * 10,
        duration: 0.3,
        ease: 'power2.out',
        transformOrigin: '50% 50% 0',
        transformStyle: 'preserve-3d' as any,
      })
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <section
      ref={containerRef}
      className="relative w-full min-h-screen bg-hero-gradient flex items-center justify-center overflow-hidden pt-20"
    >
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-20 left-10 w-72 h-72 bg-secondary rounded-full mix-blend-multiply filter blur-3xl animate-float"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-accent rounded-full mix-blend-multiply filter blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-8"
        >
          <div className="space-y-4">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-h1 font-display font-bold text-light leading-tight"
            >
              Agentes que{' '}
              <span className="gradient-text">trabajan por ti</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl text-light/70 font-light max-w-md"
            >
              Automatiza tu negocio con inteligencia artificial. Sin código. Sin
              complicaciones. Disponible 24/7.
            </motion.p>
          </div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 pt-4"
          >
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(0, 217, 255, 0.4)' }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-accent text-primary-dark rounded-lg font-bold hover:shadow-glow-lg transition-all"
            >
              Demo Interactivo
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 border-2 border-accent text-accent rounded-lg font-bold hover:bg-accent/10 transition-all"
            >
              Contacta Ventas
            </motion.button>
          </motion.div>

          {/* Trust Badge */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="flex items-center gap-3 pt-4"
          >
            <div className="flex -space-x-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-secondary border-2 border-primary-dark"
                />
              ))}
            </div>
            <div className="text-sm text-light/60">
              +500 empresas confían en nosotros
            </div>
          </motion.div>
        </motion.div>

        {/* Right 3D Bot Container */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="relative h-96 lg:h-full flex items-center justify-center"
        >
          <div
            ref={botRef}
            className="relative w-64 h-64 lg:w-80 lg:h-80"
            style={{
              perspective: '1000px',
            }}
          >
            {/* Spline placeholder - 3D bot mockup */}
            <div className="absolute inset-0 bg-gradient-to-br from-secondary to-accent/20 rounded-3xl border-2 border-accent/30 flex items-center justify-center overflow-hidden group">
              <div className="absolute inset-0 bg-card-gradient opacity-50"></div>

              {/* Animated gradient orb inside */}
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  opacity: [0.5, 0.8, 0.5],
                }}
                transition={{ duration: 4, repeat: Infinity }}
                className="w-40 h-40 bg-gradient-to-r from-accent to-secondary rounded-full blur-3xl"
              />

              {/* Center text */}
              <div className="absolute inset-0 flex items-center justify-center">
                <p className="text-accent font-mono text-sm text-center px-4 relative z-10">
                  [3D Agent Bot]<br />
                  <span className="text-xs text-light/50 mt-2 block">
                    Spline Object
                  </span>
                </p>
              </div>
            </div>

            {/* Glow ring */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              className="absolute inset-0 border-2 border-transparent border-t-accent border-r-accent rounded-3xl"
            />
          </div>

          {/* Scroll hint */}
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center"
          >
            <p className="text-accent text-sm mb-2">Scroll para explorar</p>
            <div className="w-6 h-10 border-2 border-accent rounded-full flex items-start justify-center p-2">
              <motion.div
                animate={{ y: [0, 6, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-1 h-2 bg-accent rounded-full"
              />
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
