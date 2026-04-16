'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const demoMessages = [
  { type: 'user', text: 'Hola, quiero un presupuesto para 50 pasteles' },
  { type: 'agent', text: 'Claro! Cuéntame más detalles:\n• ¿Qué tipo de pasteles?\n• ¿Cuándo los necesitas?\n• ¿Entregas a domicilio?' },
  { type: 'user', text: 'Chocolate, para el viernes, sí entregas' },
  { type: 'agent', text: 'Perfecto! El presupuesto es de $2,500 MXN.\nEntregar viernes 6pm. ¿Confirmas?' },
  { type: 'user', text: 'Sí, confirmo. Me envías detalles de pago?' },
  { type: 'agent', text: 'Listo! Te envié link de pago al WhatsApp.\nNo hay que hacer nada más. Agradecemos tu compra 🙌' },
]

export function DemoChat() {
  const [displayedMessages, setDisplayedMessages] = useState<typeof demoMessages>([])
  const [isVisible, setIsVisible] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.3 }
    )

    if (containerRef.current) {
      observer.observe(containerRef.current)
    }

    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!isVisible) return

    // Simulate messages appearing one by one
    const timeouts: NodeJS.Timeout[] = []

    demoMessages.forEach((msg, index) => {
      const timeout = setTimeout(() => {
        setDisplayedMessages((prev) => [...prev, msg])
      }, index * 1000)
      timeouts.push(timeout)
    })

    return () => timeouts.forEach((t) => clearTimeout(t))
  }, [isVisible])

  return (
    <section
      ref={containerRef}
      className="relative w-full py-32 bg-primary-dark overflow-hidden"
    >
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
            DEMO INTERACTIVA
          </motion.p>
          <h2 className="text-h2 font-display font-bold text-light">
            Mira cómo funciona en<span className="gradient-text"> acción</span>
          </h2>
        </motion.div>

        {/* Chat container */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="relative max-w-2xl mx-auto"
        >
          {/* Chat window */}
          <div className="bg-card-gradient rounded-2xl border border-accent/20 overflow-hidden shadow-lg">
            {/* Header */}
            <div className="bg-gradient-to-r from-secondary to-accent/20 px-6 py-4 flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-accent animate-pulse"></div>
              <span className="font-semibold text-light">Agent Sonora - Pastelería</span>
            </div>

            {/* Messages */}
            <div className="h-96 overflow-y-auto p-6 space-y-4 bg-primary-dark/50">
              <AnimatePresence>
                {displayedMessages.map((msg, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className={`flex ${
                      msg.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-xs px-4 py-2 rounded-lg ${
                        msg.type === 'user'
                          ? 'bg-accent text-primary-dark'
                          : 'bg-secondary/30 text-light border border-accent/30'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-line leading-relaxed">
                        {msg.text}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing indicator */}
              {displayedMessages.length < demoMessages.length && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-2"
                >
                  <div className="w-2 h-2 rounded-full bg-accent/50 animate-bounce"></div>
                  <div
                    className="w-2 h-2 rounded-full bg-accent/50 animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  ></div>
                  <div
                    className="w-2 h-2 rounded-full bg-accent/50 animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                </motion.div>
              )}
            </div>

            {/* Input area */}
            <div className="border-t border-accent/20 px-6 py-4 bg-dark-bg/50">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Escribe un mensaje..."
                  disabled
                  className="flex-1 bg-primary-dark border border-accent/20 rounded-lg px-4 py-2 text-light placeholder-light/30 text-sm disabled:opacity-50"
                />
                <button className="px-4 py-2 bg-accent text-primary-dark rounded-lg font-semibold text-sm hover:shadow-glow-lg transition-all">
                  Enviar
                </button>
              </div>
            </div>
          </div>

          {/* Parallax agent behind chat */}
          <motion.div
            animate={{
              y: [0, -20, 0],
            }}
            transition={{ duration: 4, repeat: Infinity }}
            className="absolute -right-20 -bottom-20 text-8xl opacity-20 pointer-events-none"
          >
            🤖
          </motion.div>
        </motion.div>

        {/* CTA after demo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="text-center mt-12"
        >
          <p className="text-light/60 mb-4">
            ¿Listo para automatizar tu negocio?
          </p>
          <motion.button
            whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(0, 217, 255, 0.4)' }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 bg-accent text-primary-dark rounded-lg font-bold hover:shadow-glow-lg transition-all"
          >
            Solicita Demo Completa
          </motion.button>
        </motion.div>
      </div>
    </section>
  )
}
