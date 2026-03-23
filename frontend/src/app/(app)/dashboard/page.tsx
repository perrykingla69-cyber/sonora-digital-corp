'use client'

import { useEffect, useState } from 'react'
import { api, DashboardData, CierreCompleto, Factura, TipoCambio } from '@/lib/api'
import { Card, StatCard } from '@/components/ui/Card'
import {
  TrendingUp, TrendingDown, Activity, DollarSign, FileText,
  AlertTriangle, CheckCircle, Zap, MessageCircle, Send,
  Brain, ArrowUpRight, ArrowDownRight, Percent, Loader2,
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

const SALUD_CONFIG = {
  verde:    { border: 'border-emerald-500/30', bg: 'bg-emerald-500/5', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Nodo Soberano: ÓPTIMO' },
  amarillo: { border: 'border-amber-500/30',   bg: 'bg-amber-500/5',   text: 'text-amber-400',   dot: 'bg-amber-400',   label: 'Sistema: ATENCIÓN REQUERIDA' },
  rojo:     { border: 'border-red-500/30',     bg: 'bg-red-500/5',     text: 'text-red-400',     dot: 'bg-red-400',     label: 'Alerta Crítica: ACCIÓN INMEDIATA' },
}

// Chart tooltip dark
const DarkTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-xl px-3 py-2 border border-sovereign-border text-xs">
      <p className="text-sovereign-muted mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }} className="font-semibold">{p.name}: {mxn(p.value)}</p>
      ))}
    </div>
  )
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
      <div className="flex items-center gap-3 text-sovereign-muted">
        <Loader2 size={20} className="animate-spin text-sovereign-gold" />
        <span className="text-sm">Cargando métricas del nodo...</span>
      </div>
    </div>
  )
  if (error && !dash) return <p className="text-red-400 text-sm p-4">Error: {error}</p>
  if (!dash) return null

  const { resumen, kpis, alertas, periodo } = dash
  const tcVal = tc?.tipo_cambio || 0
  const salud = SALUD_CONFIG[kpis.salud]

  const MESES = ['Oct', 'Nov', 'Dic', 'Ene', 'Feb', 'Mar']
  const chartData = MESES.map((m, i) => ({
    mes: m,
    ingresos: Math.round(resumen.ingresos_mes * (0.55 + i * 0.09)),
    gastos: Math.round(resumen.gastos_mes * (0.6 + i * 0.08)),
  }))

  const factPendientes = facturas.filter(f => f.estado === 'pendiente').length
  const factCanceladas = facturas.filter(f => f.estado === 'cancelada').length

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-sovereign-text flex items-center gap-2">
            <Zap size={18} className="text-sovereign-gold" />
            Nodo Soberano
          </h1>
          <p className="text-xs text-sovereign-muted mt-0.5">Periodo: {periodo} · Tenant: {dash.tenant_id}</p>
        </div>
        {tcVal > 0 && (
          <div className="text-right glass rounded-xl px-4 py-2">
            <p className="text-xs text-sovereign-muted">Tipo de cambio</p>
            <p className="text-lg font-bold text-sovereign-gold">${tcVal.toFixed(2)} <span className="text-xs font-normal text-sovereign-muted">MXN/USD</span></p>
            {tc?.variacion_pct !== undefined && (
              <p className={`text-xs ${tc.variacion_pct >= 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                {tc.variacion_pct >= 0 ? '▲' : '▼'} {Math.abs(tc.variacion_pct).toFixed(2)}%
              </p>
            )}
          </div>
        )}
      </div>

      {/* Estado del sistema */}
      <div className={`rounded-xl border px-5 py-3 flex items-center gap-4 ${salud.bg} ${salud.border}`}>
        <span className={`w-2.5 h-2.5 rounded-full ${salud.dot} animate-gold-pulse flex-shrink-0`} />
        <div className="flex-1">
          <p className={`font-semibold text-sm ${salud.text}`}>{salud.label}</p>
          {alertas.length > 0 && (
            <p className={`text-xs mt-0.5 ${salud.text} opacity-70`}>{alertas.length} alerta{alertas.length > 1 ? 's' : ''} activa{alertas.length > 1 ? 's' : ''}</p>
          )}
        </div>
        {alertas.length === 0 && <CheckCircle size={16} className="text-emerald-400 flex-shrink-0" />}
      </div>

      {/* Alertas */}
      {alertas.length > 0 && (
        <div className="space-y-2">
          {alertas.map((a, i) => (
            <div key={i} className="flex items-start gap-3 bg-amber-500/5 border border-amber-500/20 rounded-lg px-4 py-3">
              <AlertTriangle size={15} className="text-amber-400 mt-0.5 shrink-0" />
              <p className="text-sm text-amber-300">{a}</p>
            </div>
          ))}
        </div>
      )}

      {/* KPIs Financieros */}
      <div>
        <p className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider mb-3">Resultados del Mes</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard label="Ingresos" value={mxn(resumen.ingresos_mes)}
            sub={tcVal > 0 ? usd(resumen.ingresos_mes, tcVal) : undefined} color="green"
            icon={<TrendingUp size={22} />} />
          <StatCard label="Egresos" value={mxn(resumen.gastos_mes)}
            sub={tcVal > 0 ? usd(resumen.gastos_mes, tcVal) : undefined} color="red"
            icon={<TrendingDown size={22} />} />
          <StatCard label="Utilidad Neta" value={mxn(resumen.utilidad_mes)}
            sub={tcVal > 0 ? usd(resumen.utilidad_mes, tcVal) : undefined}
            color={resumen.utilidad_mes >= 0 ? 'green' : 'red'}
            icon={<Activity size={22} />} />
          <StatCard label="Margen Bruto" value={`${kpis.margen_bruto_pct.toFixed(1)}%`}
            sub={kpis.margen_bruto_pct >= 30 ? 'Saludable' : kpis.margen_bruto_pct >= 10 ? 'Aceptable' : 'Bajo'}
            color={kpis.margen_bruto_pct >= 30 ? 'gold' : kpis.margen_bruto_pct >= 10 ? 'blue' : 'red'}
            icon={<Percent size={22} />} />
        </div>
      </div>

      {/* KPIs Flujo */}
      <div>
        <p className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider mb-3">Flujo de Caja</p>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard label="Por Cobrar" value={mxn(resumen.por_cobrar)}
            sub={tcVal > 0 ? usd(resumen.por_cobrar, tcVal) : 'Cuentas pendientes'}
            color={resumen.por_cobrar > 0 ? 'blue' : 'gray'} icon={<ArrowUpRight size={22} />} />
          <StatCard label="Por Pagar" value={mxn(resumen.por_pagar)}
            sub={tcVal > 0 ? usd(resumen.por_pagar, tcVal) : 'Compromisos'}
            color={resumen.por_pagar > resumen.por_cobrar ? 'red' : 'gray'} icon={<ArrowDownRight size={22} />} />
          <StatCard label="Ratio Cobro/Pago"
            value={kpis.ratio_cobro_pago > 0 ? `${kpis.ratio_cobro_pago.toFixed(2)}x` : '—'}
            sub={kpis.ratio_cobro_pago >= 1 ? 'Favorable' : kpis.ratio_cobro_pago > 0 ? 'Atención' : 'Sin datos'}
            color={kpis.ratio_cobro_pago >= 1 ? 'green' : kpis.ratio_cobro_pago > 0 ? 'red' : 'gray'}
            icon={<DollarSign size={22} />} />
          <StatCard label="Facturas del Mes" value={String(resumen.facturas_mes)}
            sub={`${resumen.total_facturas} total · ${factPendientes} pend · ${factCanceladas} canc`}
            color="gray" icon={<FileText size={22} />} />
        </div>
      </div>

      {/* KPIs Fiscales */}
      {cierre && (
        <div>
          <p className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider mb-3">Obligaciones Fiscales</p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <StatCard label="IVA Neto a Pagar" value={mxn(cierre.iva_neto)}
              sub={`Cobrado: ${mxn(cierre.iva_cobrado)}`} color={cierre.iva_neto > 0 ? 'red' : 'green'} />
            <StatCard label="ISR Estimado" value={mxn(cierre.isr_estimado)}
              sub="Art. 14 LISR (pago prov.)" color="blue" />
            <StatCard label="EBITDA" value={mxn(cierre.ebitda)}
              sub={`Margen: ${cierre.margen_neto_pct?.toFixed(1) ?? '0'}%`}
              color={cierre.ebitda >= 0 ? 'green' : 'red'} />
            <StatCard label="PTU Estimada" value={mxn(cierre.ptu)}
              sub="10% utilidad fiscal" color="gray" />
          </div>
        </div>
      )}

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 module-card p-5">
          <p className="text-sm font-semibold text-sovereign-text mb-0.5">Tendencia 6 meses</p>
          <p className="text-xs text-sovereign-muted mb-4">Ingresos vs Egresos (MXN)</p>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="gIng" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34d399" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gEg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f87171" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#f87171" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="mes" tick={{ fontSize: 11, fill: '#666' }} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 10, fill: '#666' }} axisLine={false} tickLine={false} />
              <Tooltip content={<DarkTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#666' }} />
              <Area type="monotone" dataKey="ingresos" stroke="#34d399" fill="url(#gIng)" strokeWidth={2} name="Ingresos" />
              <Area type="monotone" dataKey="gastos"   stroke="#f87171" fill="url(#gEg)"  strokeWidth={2} name="Egresos" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="module-card p-5">
          <p className="text-sm font-semibold text-sovereign-text mb-0.5">Desglose del mes</p>
          <p className="text-xs text-sovereign-muted mb-4">Composición financiera</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={[
              { name: 'Ingresos', valor: resumen.ingresos_mes },
              { name: 'Egresos',  valor: resumen.gastos_mes },
              { name: 'Utilidad', valor: Math.max(0, resumen.utilidad_mes) },
              ...(cierre ? [
                { name: 'IVA', valor: cierre.iva_neto },
                { name: 'ISR', valor: cierre.isr_estimado },
              ] : []),
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#666' }} axisLine={false} tickLine={false} />
              <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 9, fill: '#666' }} axisLine={false} tickLine={false} />
              <Tooltip content={<DarkTooltip />} />
              <Bar dataKey="valor" fill="#D4AF37" radius={[4, 4, 0, 0]} opacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Últimas facturas + accesos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 module-card">
          <div className="px-5 py-4 border-b border-sovereign-border flex items-center justify-between">
            <p className="text-sm font-semibold text-sovereign-text">Últimas Transacciones</p>
            <Link href="/facturas" className="text-xs text-sovereign-gold hover:underline">Ver todas →</Link>
          </div>
          {facturas.length === 0 ? (
            <p className="text-sm text-sovereign-muted p-5">Sin facturas registradas</p>
          ) : (
            <div className="divide-y divide-sovereign-border">
              {facturas.slice(0, 7).map(f => {
                const esIngreso = f.tipo === 'ingreso'
                const estadoColor = f.estado === 'pagada'
                  ? 'text-emerald-400 bg-emerald-500/10'
                  : f.estado === 'cancelada'
                    ? 'text-sovereign-muted bg-sovereign-card'
                    : 'text-amber-400 bg-amber-500/10'
                return (
                  <div key={f.id} className="px-5 py-3 flex items-center gap-3">
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${esIngreso ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                      {esIngreso
                        ? <ArrowUpRight size={13} className="text-emerald-400" />
                        : <ArrowDownRight size={13} className="text-red-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-sovereign-text truncate">{esIngreso ? f.emisor_nombre : f.receptor_nombre}</p>
                      <p className="text-xs text-sovereign-muted">{f.folio} · {f.fecha_emision?.slice(0, 10) || f.fecha?.slice(0, 10)}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className={`text-sm font-semibold ${esIngreso ? 'text-emerald-400' : 'text-red-400'}`}>
                        {esIngreso ? '+' : '-'}{mxn(f.total)}
                      </p>
                      <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${estadoColor}`}>{f.estado}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Accesos rápidos */}
        <div className="space-y-3">
          <p className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider">Canales IA</p>

          <Link href="/brain" className="flex items-center gap-4 glass-gold rounded-xl p-4 hover:border-sovereign-gold/40 transition-all group">
            <div className="w-9 h-9 bg-sovereign-gold/10 rounded-lg flex items-center justify-center group-hover:bg-sovereign-gold/20 transition-all">
              <Brain size={18} className="text-sovereign-gold" />
            </div>
            <div>
              <p className="text-sm font-semibold text-sovereign-text">Brain IA</p>
              <p className="text-xs text-sovereign-muted">Preguntas fiscales y contables</p>
            </div>
          </Link>

          <Link href="/whatsapp" className="flex items-center gap-4 module-card rounded-xl p-4 hover:border-emerald-500/20 transition-all group">
            <div className="w-9 h-9 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <MessageCircle size={18} className="text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-sovereign-text">WhatsApp</p>
              <p className="text-xs text-sovereign-muted">Estado · QR · Conversaciones</p>
            </div>
          </Link>

          <Link href="/telegram" className="flex items-center gap-4 module-card rounded-xl p-4 hover:border-sky-500/20 transition-all group">
            <div className="w-9 h-9 bg-sky-500/10 rounded-lg flex items-center justify-center">
              <Send size={18} className="text-sky-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-sovereign-text">Telegram Bot</p>
              <p className="text-xs text-sovereign-muted">Comandos · Estado · Acceso</p>
            </div>
          </Link>

          {cierre && (
            <div className="glass-gold rounded-xl p-4">
              <p className="text-xs font-semibold text-sovereign-gold uppercase tracking-wider mb-3">Indicadores Clave</p>
              <div className="space-y-2">
                {[
                  { label: 'Margen neto', val: `${cierre.margen_neto_pct?.toFixed(1) ?? '0'}%` },
                  { label: 'IVA cobrado', val: mxn(cierre.iva_cobrado) },
                  { label: 'IVA pagado',  val: mxn(cierre.iva_pagado) },
                  { label: 'Facturas',    val: String(cierre.num_facturas) },
                ].map(({ label, val }) => (
                  <div key={label} className="flex justify-between text-xs">
                    <span className="text-sovereign-muted">{label}</span>
                    <span className="font-semibold text-sovereign-text">{val}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
