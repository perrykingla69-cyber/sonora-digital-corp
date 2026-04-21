import React from 'react';

export const metadata = {
  title: 'Sonora Digital Corp - Automatización de Negocios',
  description: 'Plataforma SaaS para automatizar contabilidad, CRM y análisis inteligente para PYMEs mexicanas',
};

export default function SonoraLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
        <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-400 to-orange-600 flex items-center justify-center">
              <span className="text-xl font-black text-white">S</span>
            </div>
            <span className="text-xl font-bold text-white">Sonora Digital</span>
          </div>
          <div className="flex gap-6 items-center">
            <a href="#features" className="text-slate-300 hover:text-white text-sm">Características</a>
            <a href="#pricing" className="text-slate-300 hover:text-white text-sm">Precios</a>
            <a href="/auth/login" className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition">
              Acceso
            </a>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 py-24 text-center">
        <h1 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight">
          Automatiza tu Negocio<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">
            con IA Mexicana
          </span>
        </h1>
        <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-12">
          Contabilidad automática, análisis de impuestos en tiempo real, CRM inteligente y alertas fiscales. Todo integrado en una plataforma.
        </p>
        <div className="flex gap-4 justify-center">
          <button className="px-8 py-3 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-lg transition transform hover:scale-105">
            Comienza Gratis
          </button>
          <button className="px-8 py-3 border border-slate-600 text-white font-bold rounded-lg hover:border-slate-400 transition">
            Ver Demo
          </button>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-16">Potenciado por IA</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: '📊',
              title: 'Contabilidad Automática',
              desc: 'CFDI validación, cuadres automáticos, reportes de compliance'
            },
            {
              icon: '🤖',
              title: 'Análisis Fiscal IA',
              desc: 'Cálculos ISR/IVA determinísticos, alertas de obligaciones, optimizador de deducciones'
            },
            {
              icon: '💬',
              title: 'Chat IA (HERMES)',
              desc: 'Consulta cualquier duda contable o fiscal en WhatsApp en tiempo real'
            },
            {
              icon: '📈',
              title: 'CRM Inteligente',
              desc: 'Gestiona clientes, proyecciones, historial de servicios en un lugar'
            },
            {
              icon: '🎯',
              title: 'Gamificación',
              desc: 'Gana insignias, sube de nivel, aprende mientras trabajas y ganas'
            },
            {
              icon: '⚡',
              title: 'Integración Multicanal',
              desc: 'Telegram, WhatsApp, Email - automatiza en cualquier canal'
            }
          ].map((feature, i) => (
            <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-amber-500/50 transition">
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400 text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-16">Planes Simples</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              name: 'Starter',
              price: '$5',
              features: ['Hasta 3 clientes', 'Contabilidad básica', 'Chat HERMES', 'Email support']
            },
            {
              name: 'Pro',
              price: '$25',
              features: ['Hasta 20 clientes', 'Análisis fiscal avanzado', 'Alertas automáticas', 'WhatsApp premium', 'Phone support'],
              highlight: true
            },
            {
              name: 'Enterprise',
              price: 'Contacto',
              features: ['Clientes ilimitados', 'Integración SAT API', 'Training personalizado', 'SLA 99.9%', 'Dedicated manager']
            }
          ].map((plan, i) => (
            <div key={i} className={`p-8 rounded-xl border transition ${
              plan.highlight
                ? 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/50 transform scale-105'
                : 'bg-slate-800/50 border-slate-700'
            }`}>
              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <div className="text-3xl font-black text-amber-400 mb-6">{plan.price}<span className="text-sm text-slate-400">/mes</span></div>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-2 text-slate-300">
                    <span className="text-amber-400">✓</span> {feature}
                  </li>
                ))}
              </ul>
              <button className={`w-full py-3 rounded-lg font-bold transition ${
                plan.highlight
                  ? 'bg-amber-500 hover:bg-amber-600 text-white'
                  : 'border border-slate-600 text-white hover:border-slate-400'
              }`}>
                Escoger Plan
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Final */}
      <section className="max-w-4xl mx-auto px-4 py-20 text-center">
        <div className="p-12 rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30">
          <h2 className="text-3xl font-bold text-white mb-4">Listo para escalar tu negocio?</h2>
          <p className="text-slate-300 mb-8">Únete a 100+ contadores y PYMEs que automatizan con Sonora Digital.</p>
          <button className="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-bold rounded-lg transition transform hover:scale-105 text-lg">
            Comienza Ahora - Gratis
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 bg-slate-900/50 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-400 text-sm">
          <p>&copy; 2026 Sonora Digital Corp. Todos los derechos reservados.</p>
          <p className="mt-2">Desarrollado con IA • Operado 24/7 • Compliance México</p>
        </div>
      </footer>
    </div>
  );
}
