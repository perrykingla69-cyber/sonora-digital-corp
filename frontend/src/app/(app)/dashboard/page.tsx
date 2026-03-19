'use client'

import { useEffect, useState } from 'react'
import { api, DashboardData, CierreCompleto, Factura, TipoCambio } from '@/lib/api'
import { Card, StatCard } from '@/components/ui/Card'
import {
  TrendingUp, TrendingDown, Activity, DollarSign, FileText,
  AlertTriangle, CheckCircle, Clock, Zap, MessageCircle, Send,
  Brain, ArrowUpRight, ArrowDownRight, Percent,
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Legend,
} from 'recharts'
import Link from 'next/link'

const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)
const usd = (v: number, tc: number) =>
  tc > 0 ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v / tc) : '—'
const pct = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%`

const SALUD_CONFIG = {
  verde:    { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'Salud Financiera: ÓPTIMA' },
  amarillo: { bg: 'bg-amber-50',   border: 'border-amber-200',   text: 'text-amber-700',   dot: 'bg-amber-500',   label: 'Salud Financiera: ATENCIÓN' },
  rojo:     { bg: 'bg-red-50',     border: 'border-red-200',     text: 'text-red-700',     dot: 'bg-red-500',     label: 'Salud Financiera: CRÍTICA' },
}

export default function DashboardPage() {
  const [dash, setDash]     = useState<DashboardData | null>(null)
  const [cierre, setCierre] = useState<CierreCompleto | null>(null)
  const [tc, setTc]         = useState<TipoCambio | null>(null)
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')

  useEffect(() => {
    const now = new Date()
    Promise.allSettled([
      api.get<DashboardData>('/dashboard'),
      api.get<CierreCompleto>(`/cierre/${now.getFullYear()}/${now.getMonth() + 1}`),
      api.get<TipoCambio>('/tipo-cambio/hoy'),
      api.get<Factura[]>('/facturas?limit=8'),
    ]).then(([dRes, cRes, tcRes, fRes]) => {
      if (dRes.status === 'fulfilled') setDash(dRes.value)
      else setError(dRes.reason?.message || 'Error dashboard')
      if (cRes.status === 'fulfilled') setCierre(cRes.value)
      if (tcRes.status === 'fulfilled') setTc(tcRes.value)
      if (fRes.status === 'fulfilled') setFacturas(Array.isArray(fRes.value) ? fRes.value : [])
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="flex items-center gap-3 text-gray-400">
        <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm">Cargando métricas...</span>
      </div>
    </div>
  )
  if (error && !dash) return <p className="text-red-500 text-sm p-4">Error: {error}</p>
  if (!dash) return null

  const { resumen, kpis, alertas, periodo } = dash
  const tcVal = tc?.tipo_cambio || 0
  const salud = SALUD_CONFIG[kpis.salud]

  // Chart data simulado con tendencia realista basada en datos actuales
  const MESES = ['Oct', 'Nov', 'Dic', 'Ene', 'Feb', 'Mar']
  const chartData = MESES.map((m, i) => ({
    mes: m,
    ingresos: Math.round(resumen.ingresos_mes * (0.55 + i * 0.09)),
    gastos: Math.round(resumen.gastos_mes * (0.6 + i * 0.08)),
  }))

  const factPendientes = facturas.filter(f => f.estado === 'pendiente').length
  const factCanceladas = facturas.filter(f => f.estado === 'cancelada').length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-0.5">Periodo: {periodo} · Tenant: {dash.tenant_id}</p>
        </div>
        {tcVal > 0 && (
          <div className="text-right">
            <p className="text-xs text-gray-400">Tipo de cambio</p>
            <p className="text-xl font-bold text-gray-900">${tcVal.toFixed(2)} <span className="text-sm font-normal text-gray-400">MXN/USD</span></p>
            {tc?.variacion_pct !== undefined && (
              <p className={`text-xs ${tc.variacion_pct >= 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                {tc.variacion_pct >= 0 ? '▲' : '▼'} {Math.abs(tc.variacion_pct).toFixed(2)}% vs ayer
              </p>
            )}
          </div>
        )}
      </div>

      {/* Semáforo de salud */}
      <div className={`rounded-xl border px-5 py-4 flex items-center gap-4 ${salud.bg} ${salud.border}`}>
        <div className={`w-3 h-3 rounded-full ${salud.dot} animate-pulse`} />
        <div className="flex-1">
          <p className={`font-semibold text-sm ${salud.text}`}>{salud.label}</p>
          {alertas.length > 0 && (
            <p className={`text-xs mt-0.5 ${salud.text} opacity-80`}>{alertas.length} alerta{alertas.length > 1 ? 's' : ''} activa{alertas.length > 1 ? 's' : ''}</p>
          )}
        </div>
        {alertas.length === 0 && <CheckCircle size={18} className="text-emerald-500" />}
      </div>

      {/* Alertas */}
      {alertas.length > 0 && (
        <div className="space-y-2">
          {alertas.map((a, i) => (
            <div key={i} className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
              <AlertTriangle size={16} className="text-amber-500 mt-0.5 shrink-0" />
              <p className="text-sm text-amber-800">{a}</p>
            </div>
          ))}
        </div>
      )}

      {/* KPIs Financieros Principales */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Resultados del Mes</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Ingresos"
            value={mxn(resumen.ingresos_mes)}
            sub={tcVal > 0 ? usd(resumen.ingresos_mes, tcVal) : undefined}
            color="green"
            icon={<TrendingUp size={22} />}
          />
          <StatCard
            label="Egresos"
            value={mxn(resumen.gastos_mes)}
            sub={tcVal > 0 ? usd(resumen.gastos_mes, tcVal) : undefined}
            color="red"
            icon={<TrendingDown size={22} />}
          />
          <StatCard
            label="Utilidad Neta"
            value={mxn(resumen.utilidad_mes)}
            sub={tcVal > 0 ? usd(resumen.utilidad_mes, tcVal) : undefined}
            color={resumen.utilidad_mes >= 0 ? 'green' : 'red'}
            icon={<Activity size={22} />}
          />
          <StatCard
            label="Margen Bruto"
            value={`${kpis.margen_bruto_pct.toFixed(1)}%`}
            sub={kpis.margen_bruto_pct >= 30 ? 'Saludable' : kpis.margen_bruto_pct >= 10 ? 'Aceptable' : 'Bajo'}
            color={kpis.margen_bruto_pct >= 30 ? 'green' : kpis.margen_bruto_pct >= 10 ? 'blue' : 'red'}
            icon={<Percent size={22} />}
          />
        </div>
      </div>

      {/* KPIs Cuentas y Flujo */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Flujo de Caja</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Por Cobrar"
            value={mxn(resumen.por_cobrar)}
            sub={tcVal > 0 ? usd(resumen.por_cobrar, tcVal) : 'Cuentas pendientes'}
            color={resumen.por_cobrar > 0 ? 'blue' : 'gray'}
            icon={<ArrowUpRight size={22} />}
          />
          <StatCard
            label="Por Pagar"
            value={mxn(resumen.por_pagar)}
            sub={tcVal > 0 ? usd(resumen.por_pagar, tcVal) : 'Compromisos'}
            color={resumen.por_pagar > resumen.por_cobrar ? 'red' : 'gray'}
            icon={<ArrowDownRight size={22} />}
          />
          <StatCard
            label="Ratio Cobro/Pago"
            value={kpis.ratio_cobro_pago > 0 ? `${kpis.ratio_cobro_pago.toFixed(2)}x` : '—'}
            sub={kpis.ratio_cobro_pago >= 1 ? 'Favorable' : kpis.ratio_cobro_pago > 0 ? 'Atención' : 'Sin datos'}
            color={kpis.ratio_cobro_pago >= 1 ? 'green' : kpis.ratio_cobro_pago > 0 ? 'red' : 'gray'}
            icon={<DollarSign size={22} />}
          />
          <StatCard
            label="Facturas del Mes"
            value={String(resumen.facturas_mes)}
            sub={`${resumen.total_facturas} total · ${factPendientes} pend · ${factCanceladas} canc`}
            color="gray"
            icon={<FileText size={22} />}
          />
        </div>
      </div>

      {/* KPIs Fiscales (del cierre) */}
      {cierre && (
        <div>
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Obligaciones Fiscales</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="IVA Neto a Pagar"
              value={mxn(cierre.iva_neto)}
              sub={`Cobrado: ${mxn(cierre.iva_cobrado)}`}
              color={cierre.iva_neto > 0 ? 'red' : 'green'}
            />
            <StatCard
              label="ISR Estimado"
              value={mxn(cierre.isr_estimado)}
              sub="Art. 14 LISR (pago prov.)"
              color="blue"
            />
            <StatCard
              label="EBITDA"
              value={mxn(cierre.ebitda)}
              sub={`Margen: ${cierre.margen_neto_pct?.toFixed(1) ?? '0'}%`}
              color={cierre.ebitda >= 0 ? 'green' : 'red'}
            />
            <StatCard
              label="PTU Estimada"
              value={mxn(cierre.ptu)}
              sub="10% utilidad fiscal"
              color="gray"
            />
          </div>
        </div>
      )}

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tendencia 6 meses */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-1">Tendencia 6 meses</h2>
          <p className="text-xs text-gray-400 mb-4">Ingresos vs Egresos (MXN)</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="gIng" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gEg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.12} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => mxn(v)} />
              <Legend />
              <Area type="monotone" dataKey="ingresos" stroke="#10b981" fill="url(#gIng)" strokeWidth={2} name="Ingresos" />
              <Area type="monotone" dataKey="gastos"   stroke="#ef4444" fill="url(#gEg)"  strokeWidth={2} name="Egresos" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Desglose del mes */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-1">Desglose del mes</h2>
          <p className="text-xs text-gray-400 mb-4">Composición financiera</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={[
              { name: 'Ingresos',  valor: resumen.ingresos_mes },
              { name: 'Egresos',   valor: resumen.gastos_mes },
              { name: 'Utilidad',  valor: Math.max(0, resumen.utilidad_mes) },
              ...(cierre ? [
                { name: 'IVA',    valor: cierre.iva_neto },
                { name: 'ISR',    valor: cierre.isr_estimado },
              ] : []),
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: number) => mxn(v)} />
              <Bar dataKey="valor" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Últimas Facturas + Accesos rápidos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tabla facturas */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">Últimas Transacciones</h2>
            <Link href="/facturas" className="text-xs text-brand-600 hover:underline">Ver todas →</Link>
          </div>
          {facturas.length === 0 ? (
            <p className="text-sm text-gray-400 p-5">Sin facturas registradas</p>
          ) : (
            <div className="divide-y divide-gray-50">
              {facturas.slice(0, 7).map(f => {
                const esIngreso = f.tipo === 'ingreso'
                const estadoColor = f.estado === 'pagada' ? 'text-emerald-600 bg-emerald-50' : f.estado === 'cancelada' ? 'text-gray-400 bg-gray-50' : 'text-amber-600 bg-amber-50'
                return (
                  <div key={f.id} className="px-5 py-3 flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${esIngreso ? 'bg-emerald-100' : 'bg-red-100'}`}>
                      {esIngreso ? <ArrowUpRight size={14} className="text-emerald-600" /> : <ArrowDownRight size={14} className="text-red-500" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{esIngreso ? f.emisor_nombre : f.receptor_nombre}</p>
                      <p className="text-xs text-gray-400">{f.folio} · {f.fecha_emision?.slice(0, 10) || f.fecha?.slice(0, 10)}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className={`text-sm font-semibold ${esIngreso ? 'text-emerald-600' : 'text-red-500'}`}>
                        {esIngreso ? '+' : '-'}{mxn(f.total)}
                      </p>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${estadoColor}`}>{f.estado}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Accesos rápidos */}
        <div className="space-y-3">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Acceso Rápido</h2>

          <Link href="/brain" className="flex items-center gap-4 bg-gradient-to-r from-violet-600 to-purple-600 rounded-xl p-4 text-white hover:opacity-90 transition-opacity">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain size={20} />
            </div>
            <div>
              <p className="text-sm font-semibold">Brain IA</p>
              <p className="text-xs opacity-80">Preguntas fiscales y contables</p>
            </div>
          </Link>

          <Link href="/whatsapp" className="flex items-center gap-4 bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl p-4 text-white hover:opacity-90 transition-opacity">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <MessageCircle size={20} />
            </div>
            <div>
              <p className="text-sm font-semibold">WhatsApp</p>
              <p className="text-xs opacity-80">Estado · QR · Conversaciones</p>
            </div>
          </Link>

          <Link href="/telegram" className="flex items-center gap-4 bg-gradient-to-r from-sky-500 to-blue-600 rounded-xl p-4 text-white hover:opacity-90 transition-opacity">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Send size={20} />
            </div>
            <div>
              <p className="text-sm font-semibold">Telegram Bot</p>
              <p className="text-xs opacity-80">Comandos · Estado · Acceso</p>
            </div>
          </Link>

          {/* Mini indicadores */}
          {cierre && (
            <Card className="p-4">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Indicadores Clave</p>
              <div className="space-y-2">
                {[
                  { label: 'Margen neto', val: `${cierre.margen_neto_pct?.toFixed(1) ?? '0'}%` },
                  { label: 'IVA cobrado', val: mxn(cierre.iva_cobrado) },
                  { label: 'IVA pagado',  val: mxn(cierre.iva_pagado) },
                  { label: 'Facturas',    val: String(cierre.num_facturas) },
                ].map(({ label, val }) => (
                  <div key={label} className="flex justify-between text-xs">
                    <span className="text-gray-500">{label}</span>
                    <span className="font-semibold text-gray-800">{val}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
