'use client'

import { motion } from 'framer-motion'

export function Footer() {
  return (
    <section
      id="contacto"
      className="relative w-full py-24 bg-primary-dark overflow-hidden"
    >
      {/* Animated gradient background */}
      <motion.div
        animate={{
          backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
        }}
        transition={{ duration: 8, repeat: Infinity }}
        className="absolute inset-0 opacity-30"
        style={{
          background: 'linear-gradient(-45deg, #6D28D9, #00D9FF, #6D28D9, #00D9FF)',
          backgroundSize: '400% 400%',
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-h2 font-display font-bold text-light mb-6">
            ¿Listo para{' '}
            <span className="gradient-text">automatizar tu negocio?</span>
          </h2>
          <p className="text-xl text-light/60 max-w-2xl mx-auto mb-8">
            Únete a las 500+ empresas que ya están transformando su forma de
            operar con Sonora Digital Corp.
          </p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(0, 217, 255, 0.4)' }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-accent text-primary-dark rounded-lg font-bold hover:shadow-glow-lg transition-all"
            >
              Solicita Demo
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 border-2 border-accent text-accent rounded-lg font-bold hover:bg-accent/10 transition-all"
            >
              Ver Precios
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Divider */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="my-12 h-px bg-gradient-to-r from-transparent via-accent to-transparent opacity-30"
        />

        {/* Contact info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
        >
          {[
            {
              icon: '📧',
              label: 'Email',
              value: 'contacto@sonoradigital.com',
            },
            {
              icon: '📱',
              label: 'WhatsApp',
              value: '+52 (555) 123-4567',
            },
            {
              icon: '🌐',
              label: 'Ubicación',
              value: 'México, CDMX',
            },
          ].map((contact, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -5 }}
              className="text-center p-6 bg-card-gradient rounded-xl border border-accent/20 hover:border-accent/50 transition-colors"
            >
              <p className="text-3xl mb-2">{contact.icon}</p>
              <p className="text-light/60 text-sm mb-2">{contact.label}</p>
              <p className="text-accent font-semibold">{contact.value}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Footer content */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12"
        >
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-accent to-secondary rounded-lg flex items-center justify-center">
                <span className="text-primary-dark font-bold text-sm">SD</span>
              </div>
              <span className="font-display font-bold text-lg text-light">
                Sonora
              </span>
            </div>
            <p className="text-light/60 text-sm leading-relaxed">
              Agentes IA que trabajan 24/7 para tu negocio.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold text-light mb-4">Producto</h4>
            <ul className="space-y-2 text-sm text-light/60">
              {['Características', 'Precios', 'Casos de uso', 'API'].map(
                (item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="hover:text-accent transition-colors"
                    >
                      {item}
                    </a>
                  </li>
                )
              )}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold text-light mb-4">Empresa</h4>
            <ul className="space-y-2 text-sm text-light/60">
              {['Sobre nosotros', 'Blog', 'Careers', 'Contacto'].map(
                (item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="hover:text-accent transition-colors"
                    >
                      {item}
                    </a>
                  </li>
                )
              )}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-semibold text-light mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-light/60">
              {['Términos', 'Privacidad', 'Cookies', 'Seguridad'].map(
                (item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="hover:text-accent transition-colors"
                    >
                      {item}
                    </a>
                  </li>
                )
              )}
            </ul>
          </div>
        </motion.div>

        {/* Bottom bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="border-t border-accent/20 pt-8 flex flex-col md:flex-row items-center justify-between"
        >
          <p className="text-light/50 text-sm">
            © 2026 Sonora Digital Corp. Todos los derechos reservados.
          </p>
          <div className="flex gap-6 mt-4 md:mt-0">
            {['Twitter', 'LinkedIn', 'Instagram', 'GitHub'].map((social) => (
              <a
                key={social}
                href="#"
                className="text-light/50 hover:text-accent transition-colors text-sm"
              >
                {social}
              </a>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
