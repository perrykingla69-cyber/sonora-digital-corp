'use client'
import { motion } from 'framer-motion'
import Link from 'next/link'
import clsx from 'clsx'

const PLANS = [
  {
    name: 'Free',
    price: '0',
    period: '/mes',
    description: 'Para empezar a automatizar',
    features: [
      '1 agente activo',
      '100 mensajes/mes',
      'Canal Telegram',
      'Soporte por email',
    ],
    cta: 'Empezar gratis',
    href: '/auth/signup',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '499',
    period: '/mes',
    description: 'Para negocios en crecimiento',
    features: [
      '5 agentes activos',
      '5,000 mensajes/mes',
      'Telegram + WhatsApp',
      'Analytics avanzados',
      'Soporte prioritario',
      'Integraciones: Stripe, Slack',
    ],
    cta: 'Empezar Pro',
    href: '/auth/signup?plan=pro',
    highlighted: true,
    badge: 'Más popular',
  },
  {
    name: 'Enterprise',
    price: '1,999',
    period: '/mes',
    description: 'Para empresas que escalan',
    features: [
      'Agentes ilimitados',
      'Mensajes ilimitados',
      'Todos los canales',
      'SLA 99.9% uptime',
      'Soporte dedicado 24/7',
      'Integraciones personalizadas',
      'On-premise disponible',
    ],
    cta: 'Contactar ventas',
    href: 'mailto:sonoradigitalcorp@gmail.com',
    highlighted: false,
  },
]

export default function PricingTable() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
      {PLANS.map((plan, i) => (
        <motion.div
          key={plan.name}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className={clsx(
            'relative rounded-2xl p-8 flex flex-col',
            plan.highlighted
              ? 'bg-brand-500/10 border-2 border-brand-500/40 ring-1 ring-brand-500/20'
              : 'glass'
          )}
        >
          {plan.badge && (
            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
              <span className="px-3 py-1 rounded-full bg-brand-500 text-white text-xs font-semibold">
                {plan.badge}
              </span>
            </div>
          )}

          <div className="mb-6">
            <h3 className="text-lg font-bold text-white">{plan.name}</h3>
            <p className="text-white/50 text-sm mt-1">{plan.description}</p>
            <div className="flex items-baseline gap-1 mt-4">
              <span className="text-white/40 text-sm">MXN $</span>
              <span className="text-4xl font-bold text-white">{plan.price}</span>
              <span className="text-white/40 text-sm">{plan.period}</span>
            </div>
          </div>

          <ul className="flex-1 space-y-3 mb-8">
            {plan.features.map(f => (
              <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                <svg className="w-4 h-4 text-brand-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {f}
              </li>
            ))}
          </ul>

          <Link
            href={plan.href}
            className={clsx(
              'block text-center py-3 rounded-xl font-semibold text-sm transition-all duration-200',
              plan.highlighted
                ? 'btn-primary'
                : 'btn-secondary'
            )}
          >
            {plan.cta}
          </Link>
        </motion.div>
      ))}
    </div>
  )
}
