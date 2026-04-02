'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Check, Zap, Star, Crown, Sparkles, ExternalLink, AlertCircle } from 'lucide-react'

interface Plan {
  id: string
  label: string
  precio_mxn: number
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const PLAN_ICONS: Record<string, any> = {
  basico:   <Zap size={24} className="text-gray-500" />,
  business: <Star size={24} className="text-blue-500" />,
  pro:      <Crown size={24} className="text-purple-500" />,
  magia:    <Sparkles size={24} className="text-amber-500" />,
}

const PLAN_FEATURES: Record<string, string[]> = {
  basico: [
    'Dashboard financiero',
    'Facturas CFDI 4.0',
    'Brain IA básico (5 preguntas/día)',
    'Cierre mensual',
    '1 usuario',
  ],
  business: [
    'Todo lo de Básico',
    'Brain IA ilimitado + WhatsApp',
    'Nómina (hasta 10 empleados)',
    'MVE / Comercio exterior',
    'Telegram Bot',
    '3 usuarios',
  ],
  pro: [
    'Todo lo de Business',
    'Multi-tenant (hasta 3 empresas)',
    'Reportes avanzados PDF',
    'Integración N8N workflows',
    'Soporte prioritario',
    '10 usuarios',
  ],
  magia: [
    'Todo lo de Pro',
    'AI OS completo (4 agentes)',
    'Brain Swarm (análisis paralelo)',
    'Tenants ilimitados',
    'API access',
    'Usuarios ilimitados',
  ],
}

const PLAN_COLORS: Record<string, string> = {
  basico:   'border-gray-200 hover:border-gray-400',
  business: 'border-blue-200 hover:border-blue-400',
  pro:      'border-purple-200 hover:border-purple-400',
  magia:    'border-amber-200 hover:border-amber-400 bg-amber-50/30',
}

const PLAN_BTN: Record<string, string> = {
  basico:   'bg-gray-700 hover:bg-gray-800 text-white',
  business: 'bg-blue-600 hover:bg-blue-700 text-white',
  pro:      'bg-purple-600 hover:bg-purple-700 text-white',
  magia:    'bg-amber-500 hover:bg-amber-600 text-white',
}

export default function BillingPage() {
  const [planes, setPlanes] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [procesando, setProcesando] = useState<string | null>(null)
  const [mpError, setMpError] = useState('')

  useEffect(() => {
    api.get<Plan[]>('/payments/planes').then(setPlanes).catch(() => null).finally(() => setLoading(false))
  }, [])

  async function suscribir(planId: string) {
    setProcesando(planId); setMpError('')
    try {
      const res = await api.post<{ init_point?: string; error?: string; hint?: string }>(
        '/payments/mp/preference', { plan: planId }
      )
      if (res.init_point) {
        window.open(res.init_point, '_blank')
      } else if (res.error) {
        setMpError(`${res.error}${res.hint ? ' — ' + res.hint : ''}`)
      }
    } catch (e: unknown) {
      setMpError(e instanceof Error ? e.message : 'Error al crear preferencia de pago')
    } finally {
      setProcesando(null)
    }
  }

  if (loading) return (
    <div className="flex items-center gap-2 text-gray-400 text-sm mt-8">
      <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      Cargando planes...
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Suscripción — Hermes AI OS</h1>
        <p className="text-sm text-gray-500 mt-0.5">Elige el plan que mejor se adapte a tu empresa</p>
      </div>

      {mpError && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle size={18} className="text-amber-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800">Mercado Pago no configurado</p>
            <p className="text-xs text-amber-700 mt-0.5">{mpError}</p>
          </div>
        </div>
      )}

      {/* Grid de planes */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        {(planes.length > 0 ? planes : [
          { id: 'basico', label: 'Básico', precio_mxn: 499 },
          { id: 'business', label: 'Business', precio_mxn: 999 },
          { id: 'pro', label: 'Pro', precio_mxn: 1999 },
          { id: 'magia', label: 'Magia IA', precio_mxn: 3999 },
        ]).map(plan => (
          <div key={plan.id}
            className={`relative border-2 rounded-2xl p-5 transition-all ${PLAN_COLORS[plan.id] || 'border-gray-200'} ${plan.id === 'pro' ? 'ring-2 ring-purple-400 ring-offset-2' : ''}`}>
            {plan.id === 'pro' && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs font-bold px-3 py-0.5 rounded-full">
                MÁS POPULAR
              </div>
            )}

            <div className="flex items-center gap-2 mb-3">
              {PLAN_ICONS[plan.id]}
              <h3 className="text-base font-bold text-gray-900">{plan.label}</h3>
            </div>

            <div className="mb-4">
              <span className="text-3xl font-extrabold text-gray-900">
                ${plan.precio_mxn.toLocaleString('es-MX')}
              </span>
              <span className="text-sm text-gray-500"> MXN/mes</span>
            </div>

            <ul className="space-y-2 mb-5 min-h-[160px]">
              {(PLAN_FEATURES[plan.id] || []).map(f => (
                <li key={f} className="flex items-start gap-2 text-sm text-gray-600">
                  <Check size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={() => suscribir(plan.id)}
              disabled={procesando !== null}
              className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-colors disabled:opacity-50 ${PLAN_BTN[plan.id] || 'bg-gray-700 text-white'}`}
            >
              {procesando === plan.id ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <ExternalLink size={14} />
                  Contratar con Mercado Pago
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Info adicional */}
      <Card className="p-5 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">¿Cómo funciona el pago?</h3>
        <ul className="space-y-1.5 text-sm text-gray-500">
          <li className="flex items-start gap-2">
            <Check size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
            Al hacer clic en "Contratar" se abre Mercado Pago con tu preferencia de pago
          </li>
          <li className="flex items-start gap-2">
            <Check size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
            Paga con tarjeta, OXXO, transferencia o wallet de MP
          </li>
          <li className="flex items-start gap-2">
            <Check size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
            Al confirmar el pago, tu plan se actualiza automáticamente
          </li>
          <li className="flex items-start gap-2">
            <Check size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
            Factura disponible — sonoradigitalcorp@gmail.com
          </li>
        </ul>
      </Card>
    </div>
  )
}
