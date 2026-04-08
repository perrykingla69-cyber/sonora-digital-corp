'use client'

import type { Metadata } from 'next'
import Link from 'next/link'
import {
  FileText, BarChart3, AlertCircle, Clock, Zap,
  CheckCircle2, TrendingUp, Shield
} from 'lucide-react'
import { Navigation } from '@/components/landing/Navigation'
import { Hero } from '@/components/landing/Hero'
import { Features } from '@/components/landing/Features'
import { CaseStudy } from '@/components/landing/CaseStudy'
import { Footer } from '@/components/landing/Footer'

const contadorFeatures = [
  {
    icon: FileText,
    title: 'NOMs y Normatividad MX',
    description: 'Acceso instantáneo a NOM-251, ISR, CFDI, RESICO y últimas actualizaciones SAT. Sin leer PDF.'
  },
  {
    icon: AlertCircle,
    title: 'Alertas de Impuestos',
    description: 'Recibe notificaciones automáticas en Telegram sobre fechas límites, cambios normativos y obligaciones pendientes.'
  },
  {
    icon: BarChart3,
    title: 'Reportes Automáticos',
    description: 'Genera DIOT, declaraciones de impuestos y estados financieros en segundos. Compatible con SAT.'
  },
  {
    icon: Clock,
    title: 'Cierre Mensual en 1 Clic',
    description: 'IVA, ISR y balances listos. Sin estar pegado a la oficina los últimos días del mes.'
  },
  {
    icon: Zap,
    title: 'Consultas IA sin Límite',
    description: '¿Cómo va el ISR en RESICO? ¿Me falta declarar algo? Pregunta y recibe respuesta legal en segundos.'
  },
  {
    icon: Shield,
    title: 'Protección Fiscal',
    description: 'Anti-multa automático. Verifica obligaciones pendientes antes de cada plazo SAT.'
  },
]

export default function ContadoresLanding() {
  return (
    <div className="relative min-h-screen bg-[#0a0500] text-white overflow-x-hidden">
      <Navigation showHome={true} />

      <Hero
        badge="Para Contadores y Despachos Fiscales"
        title={<>HERMES para<br /><span className="text-blue-400">Contadores</span></>}
        subtitle="Normatividad fiscal MX en IA. Reduce 30% del tiempo administrativo. Multiplica clientes sin crecer la nómina."
        cta={{ text: 'Solicita Demo Gratis', href: '/contadores/demo' }}
        variant="contador"
      />

      <Features
        features={contadorFeatures}
        variant="contador"
        title="Diseñado para tu despacho"
      />

      <CaseStudy
        variant="contador"
        title="Contador con 50 clientes"
        problem="Pasar 15 horas semanales en cambios normativos, alertas de fechas y responder 'dónde va esto' en WhatsApp. Todo mientras crece su cartera."
        solution="HERMES como asistente: suscriptores acceden a normatividad actualizada, reciben alertas automáticas, y el contador responde consultas complejas en minutos."
        result="Ahorra 30% tiempo administrativo. Puede tomar 15 clientes más sin contratar. Clientes más satisfechos (respuestas en segundos)."
        metric="15 horas/semana → 10 horas/semana"
      />

      <section className="relative py-20 px-4 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-black">Para empresas de cualquier tamaño</h2>
          <p className="text-white/60 mt-3">Independiente, despacho chico, corporativo — HERMES escala con vos</p>
        </div>

        <div className="grid sm:grid-cols-3 gap-6">
          {[
            { title: 'Independiente', users: '1-5 clientes', desc: 'Un contador con sus clientes. Acceso compartido a normatividad.' },
            { title: 'Despacho', users: '20-100 clientes', desc: 'Multi-contador. Cada uno ve su cartera. Reportes consolidados.' },
            { title: 'Corporativo', users: '100+ clientes', desc: 'API propia. White-label. SLA 99.9%.' },
          ].map(plan => (
            <div key={plan.title} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col">
              <h3 className="font-black text-xl mb-2 text-blue-400">{plan.title}</h3>
              <p className="text-sm text-white/60 mb-3">{plan.users}</p>
              <p className="text-white/70 flex-1 mb-4">{plan.desc}</p>
              <button
                onClick={() => window.location.href = '/contadores/demo'}
                className="w-full py-2 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 font-semibold text-sm transition"
              >
                Ver plan
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="relative py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-black">¿Por qué HERMES es mejor que una IA común?</h2>
        </div>

        <div className="grid sm:grid-cols-2 gap-6">
          {[
            { title: 'Normatividad MX', desc: 'Entrenada con NOMs reales, cambios SAT 2026 y jurisprudencia fiscal.' },
            { title: 'Sin alucinaciones', desc: 'Si no sabe, dice "no sé". Nunca inventa artículos o montos de impuestos.' },
            { title: 'Alertas inteligentes', desc: 'No es spam. Solo notificaciones relevantes para tu nicho fiscal.' },
            { title: 'Multi-cliente sin riesgo', desc: 'RLS por tenant. Cada cliente ve solo sus datos. Cumplimiento RGPD.' },
          ].map(item => (
            <div key={item.title} className="flex gap-4">
              <CheckCircle2 className="w-6 h-6 text-blue-400 shrink-0 mt-1" />
              <div>
                <h4 className="font-bold mb-1">{item.title}</h4>
                <p className="text-white/60 text-sm">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="relative py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="text-center">
          <h2 className="text-3xl sm:text-4xl font-black mb-6">Listo para empezar</h2>
          <p className="text-white/60 mb-8 max-w-xl mx-auto">
            Primeros 15 días gratis. Sin tarjeta. Acceso total a normatividad y reportes.
          </p>
          <button
            onClick={() => window.location.href = '/contadores/demo'}
            className="px-8 py-4 rounded-xl bg-blue-500 text-white font-bold hover:bg-blue-600 transition"
          >
            Solicitar Demo Ahora
          </button>
        </div>
      </section>

      <Footer />
    </div>
  )
}
