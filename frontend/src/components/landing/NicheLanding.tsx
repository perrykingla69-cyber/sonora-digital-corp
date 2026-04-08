'use client'

import Link from 'next/link'
import { NicheConfig } from '@/lib/niche-config'
import { ChevronRight, Check } from 'lucide-react'

interface NicheLandingProps {
  niche: NicheConfig
}

export default function NicheLanding({ niche }: NicheLandingProps) {
  const loginUrl = process.env.NEXT_PUBLIC_LOGIN_URL || '/login'
  const demoUrl = process.env.NEXT_PUBLIC_DEMO_URL || '/demo'

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur border-b border-slate-700">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-amber-400">
            HERMES
          </Link>
          <nav className="hidden md:flex gap-8">
            <a href="#features" className="hover:text-amber-400 transition">
              Características
            </a>
            <a href="#pricing" className="hover:text-amber-400 transition">
              Precios
            </a>
            <a href="#faq" className="hover:text-amber-400 transition">
              FAQ
            </a>
          </nav>
          <Link
            href={loginUrl}
            className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold rounded-lg transition"
          >
            Iniciar Sesión
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">{niche.icon}</div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 text-white">
          {niche.title}
        </h1>
        <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
          {niche.subtitle}
        </p>
        <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
          {niche.description}
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link
            href={loginUrl}
            className={`px-8 py-4 bg-gradient-to-r ${niche.color} text-white font-bold rounded-lg hover:shadow-lg hover:shadow-amber-500/50 transition transform hover:scale-105 flex items-center justify-center gap-2`}
          >
            {niche.cta}
            <ChevronRight className="w-5 h-5" />
          </Link>
          <Link
            href={demoUrl}
            className="px-8 py-4 border-2 border-amber-500 text-amber-400 font-bold rounded-lg hover:bg-amber-500/10 transition"
          >
            Ver Demo
          </Link>
        </div>

        {/* Trust Badges */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center text-slate-400 mb-20">
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-500" />
            <span>14 días gratis, sin tarjeta</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-500" />
            <span>Facturación CFDI automática</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-500" />
            <span>Soporte en vivo por WhatsApp</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-slate-800/50 py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">Lo que obtienes</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {niche.features.map((feature, idx) => (
              <div
                key={idx}
                className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 hover:border-amber-500 transition"
              >
                <div className="flex gap-4 items-start">
                  <Check className="w-6 h-6 text-amber-400 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-bold text-lg mb-2">{feature}</h3>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 max-w-6xl mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-16">Planes transparentes</h2>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Starter */}
          <div className="bg-slate-700/50 border border-slate-600 rounded-lg p-8 hover:border-amber-500 transition">
            <h3 className="text-2xl font-bold mb-2">Empezar</h3>
            <p className="text-slate-400 mb-6">Para negocios pequeños</p>
            <div className="text-4xl font-bold mb-6">
              $0<span className="text-lg text-slate-400">/mes primeros 14 días</span>
            </div>
            <ul className="space-y-4 mb-8">
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-500" />
                <span>Todas las características básicas</span>
              </li>
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-500" />
                <span>Hasta 100 transacciones/mes</span>
              </li>
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-500" />
                <span>Soporte por email</span>
              </li>
            </ul>
            <Link
              href={loginUrl}
              className="w-full py-3 bg-slate-600 hover:bg-slate-500 rounded-lg font-bold text-center transition"
            >
              Empezar Gratis
            </Link>
          </div>

          {/* Pro */}
          <div className="bg-gradient-to-br from-amber-600 to-orange-600 rounded-lg p-8 ring-2 ring-amber-400 transform scale-105">
            <div className="bg-amber-500 text-slate-900 inline-block px-4 py-1 rounded-full text-sm font-bold mb-4">
              Más popular
            </div>
            <h3 className="text-2xl font-bold mb-2 text-white">Profesional</h3>
            <p className="text-amber-100 mb-6">Para crecer sin límites</p>
            <div className="text-4xl font-bold mb-6 text-white">
              $299<span className="text-lg text-amber-100">/mes</span>
            </div>
            <ul className="space-y-4 mb-8 text-white">
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-300" />
                <span>Todo incluido + premium</span>
              </li>
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-300" />
                <span>Transacciones ilimitadas</span>
              </li>
              <li className="flex gap-2 items-center">
                <Check className="w-5 h-5 text-green-300" />
                <span>Soporte WhatsApp 24/7</span>
              </li>
            </ul>
            <Link
              href={loginUrl}
              className="w-full py-3 bg-white hover:bg-gray-100 text-slate-900 rounded-lg font-bold text-center transition"
            >
              Probar Ahora
            </Link>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="bg-slate-800/50 py-20">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16">Preguntas frecuentes</h2>
          <div className="space-y-6">
            {[
              {
                q: '¿Cuáles son los métodos de pago?',
                a: 'Aceptamos todas las tarjetas crédito/débito, transferencia bancaria y MercadoPago.'
              },
              {
                q: '¿Puedo usar HERMES en mi teléfono?',
                a: 'Sí, HERMES es una PWA completamente responsiva. Funciona en iPhone y Android sin descargar nada.'
              },
              {
                q: '¿Qué pasa si cancelo mi suscripción?',
                a: 'Tus datos quedan 30 días en nuestros servidores. Puedes exportar todo antes de cancelar.'
              },
              {
                q: '¿Hay contrato de permanencia?',
                a: 'No. Puedes cancelar en cualquier momento. Sin penalización.'
              }
            ].map((faq, idx) => (
              <div
                key={idx}
                className="bg-slate-700/50 border border-slate-600 rounded-lg p-6 hover:border-amber-500 transition"
              >
                <h3 className="font-bold text-lg mb-3">{faq.q}</h3>
                <p className="text-slate-300">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-gradient-to-r from-slate-900 to-slate-800 py-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">¿Listo para transformar tu negocio?</h2>
          <p className="text-xl text-slate-400 mb-8">
            Más de 500 negocios ya usan HERMES para ahorrar tiempo y ganar más.
          </p>
          <Link
            href={loginUrl}
            className={`inline-block px-10 py-4 bg-gradient-to-r ${niche.color} text-white font-bold rounded-lg hover:shadow-lg transition transform hover:scale-105`}
          >
            Comenzar Ahora — Gratis
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-700 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-500 text-sm">
          <p>© 2026 Sonora Digital Corp. Todos los derechos reservados. HERMES es un producto de IA para PYMEs mexicanas.</p>
          <div className="mt-4 space-x-6">
            <a href="/privacy" className="hover:text-amber-400">Privacidad</a>
            <a href="/terms" className="hover:text-amber-400">Términos</a>
            <a href="mailto:support@hermes.app" className="hover:text-amber-400">Contacto</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
