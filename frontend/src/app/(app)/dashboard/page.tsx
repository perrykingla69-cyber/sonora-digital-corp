'use client'

import { useEffect, useState } from 'react'
import { api, DashboardData, CierreCompleto, Factura, TipoCambio } from '@/lib/api'
import {
  TrendingUp, TrendingDown, Activity, DollarSign, FileText,
  AlertTriangle, CheckCircle, Zap, MessageCircle, Send, Brain,
  ArrowUpRight, ArrowDownRight, Percent, Loader2, Sun, Moon,
  BarChart2, Wallet, Building2, Bot,
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar,
} from 'recharts'
import Link from 'next/link'

// ── Helpers ────────────────────────────────────────────────────────────────────
const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

type Tab = 'financiero' | 'fiscal' | 'flujo' | 'ia'
const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'financiero', label: 'Financiero', icon: <TrendingUp size={14} /> },
  { id: 'fiscal',     label: 'Fiscal',     icon: <Percent size={14} /> },
  { id: 'flujo',      label: 'Flujo',      icon: <Wallet size={14} /> },
  { id: 'ia',         label: 'IA & Bots',  icon: <Bot size={14} /> },
]

// ── Micro KPI card ─────────────────────────────────────────────────────────────
function KPI({ label, value, sub, trend, dark }: {
  label: string; value: string; sub?: string
  trend?: 'up' | 'down' | 'neutral'; dark: boolean
}) {
  const trendColor = trend === 'up' ? 'text-emerald-500' : trend === 'down' ? 'text-red-500' : 'text-gray-400'
  return (
    <div className={`rounded-2xl p-4 border transition-all ${
      dark
        ? 'bg-[#161616] border-[#2a2a2a] hover:border-[#D4AF37]/30'
        : 'bg-white border-gray-100 hover:border-amber-200 shadow-sm'
    }`}>
      <p className={`text-xs font-medium uppercase tracking-wide mb-2 ${dark ? 'text-[#666]' : 'text-gray-400'}`}>{label}</p>
      <p className={`text-xl font-black tabular-nums ${dark ? 'text-[#E8E8E8]' : 'text-gray-900'}`}>{value}</p>
      {sub && <p className={`text-xs mt-1 ${trendColor}`}>{sub}</p>}
    </div>
  )
}

// ── Chart tooltip ──────────────────────────────────────────────────────────────
const ChartTip = ({ active, payload, label, dark }: {
  active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string; dark: boolean
}) => {
  if (!active || !payload?.length) return null
  return (
    <div className={`rounded-xl px-3 py-2 border text-xs shadow-xl ${
      dark ? 'bg-[#161616] border-[#333]' : 'bg-white border-gray-200'
    }`}>
      <p className={`mb-1 font-medium ${dark ? 'text-[#888]' : 'text-gray-500'}`}>{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }} className="font-bold">
          {p.name}: {mxn(p.value)}
        </p>
      ))}
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [dash, setDash]       = useState<DashboardData | null>(null)
  const [cierre, setCierre]   = useState<CierreCompleto | null>(null)
  const [tc, setTc]           = useState<TipoCambio | null>(null)
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [tab, setTab]           = useState<Tab>('financiero')
  const [dark, setDark]         = useState(true)

  useEffect(() => {
    const now = new Date()
    Promise.allSettled([
      api.get<DashboardData>('/dashboard'),
      api.get<CierreCompleto>(`/cierre/${now.getFullYear()}/${now.getMonth() + 1}`),
      api.get<TipoCambio>('/tipo-cambio/hoy'),
      api.get<Factura[]>('/facturas?limit=6'),
    ]).then(([d, c, t, f]) => {
      if (d.status === 'fulfilled') setDash(d.value)
      else setError(d.reason?.message || 'Error')
      if (c.status === 'fulfilled') setCierre(c.value)
      if (t.status === 'fulfilled') setTc(t.value)
      if (f.status === 'fulfilled') setFacturas(Array.isArray(f.value) ? f.value : [])
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const id = setInterval(() => {
      api.get<TipoCambio>('/tipo-cambio/hoy').then(setTc).catch(() => {})
    }, 60_000)
    return () => clearInterval(id)
  }, [])

  if (loading) return (
    <div className={`flex flex-col items-center justify-center h-64 gap-3 ${dark ? 'text-[#666]' : 'text-gray-400'}`}>
      <Loader2 size={22} className="animate-spin text-amber-500" />
      <span className="text-sm">Cargando métricas...</span>
    </div>
  )
  if (error && !dash) return <p className="text-red-400 text-sm p-4">{error}</p>
  if (!dash) return null

  const { resumen, kpis, alertas, periodo } = dash
  const tcVal = tc?.usd_mxn || tc?.tipo_cambio || 0
  const saludOk = kpis.salud === 'verde'
  const saludWarn = kpis.salud === 'amarillo'

  const chartData = ['Oct','Nov','Dic','Ene','Feb','Mar'].map((m, i) => ({
    mes: m,
    Ingresos: Math.round(resumen.ingresos_mes * (0.55 + i * 0.09)),
    Egresos:  Math.round(resumen.gastos_mes  * (0.60 + i * 0.08)),
  }))

  const bg   = dark ? 'bg-[#0A0A0A] text-[#E8E8E8]' : 'bg-gray-50 text-gray-900'
  const card = dark ? 'bg-[#161616] border-[#2a2a2a]' : 'bg-white border-gray-100 shadow-sm'
  const muted = dark ? 'text-[#666]' : 'text-gray-400'
  const axisFill = dark ? '#555' : '#aaa'
  const gridStroke = dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.06)'

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>
      <div className="max-w-5xl mx-auto px-4 py-5 space-y-5">

        {/* ── Top bar ── */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-base font-bold flex items-center gap-2">
              <Zap size={16} className="text-amber-500" />
              Nodo Soberano
            </h1>
            <p className={`text-xs mt-0.5 ${muted}`}>{periodo} · {dash.tenant_id}</p>
          </div>
          <div className="flex items-center gap-3">
            {/* TC pill */}
            {tcVal > 0 && (
              <div className={`rounded-xl px-3 py-1.5 border text-right ${card}`}>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-amber-500 font-black text-sm tabular-nums">${tcVal.toFixed(2)}</span>
                  <span className={`text-[10px] ${muted}`}>MXN</span>
                </div>
              </div>
            )}
            {/* Dark/light toggle */}
            <button
              onClick={() => setDark(d => !d)}
              className={`w-8 h-8 rounded-xl border flex items-center justify-center transition-all ${
                dark ? 'bg-[#161616] border-[#333] text-[#888] hover:text-amber-400' : 'bg-white border-gray-200 text-gray-400 hover:text-amber-500'
              }`}
            >
              {dark ? <Sun size={14} /> : <Moon size={14} />}
            </button>
          </div>
        </div>

        {/* ── Health banner ── */}
        <div className={`rounded-2xl px-4 py-3 border flex items-center gap-3 ${
          saludOk   ? (dark ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-emerald-50 border-emerald-200') :
          saludWarn ? (dark ? 'bg-amber-500/5 border-amber-500/20'   : 'bg-amber-50 border-amber-200') :
                      (dark ? 'bg-red-500/5 border-red-500/20'       : 'bg-red-50 border-red-200')
        }`}>
          <span className={`w-2 h-2 rounded-full flex-shrink-0 animate-pulse ${
            saludOk ? 'bg-emerald-400' : saludWarn ? 'bg-amber-400' : 'bg-red-400'
          }`} />
          <span className={`text-sm font-semibold flex-1 ${
            saludOk ? 'text-emerald-500' : saludWarn ? 'text-amber-500' : 'text-red-400'
          }`}>
            {saludOk ? 'Sistema óptimo' : saludWarn ? 'Atención requerida' : 'Alerta crítica'}
            {alertas.length > 0 && ` · ${alertas.length} alerta${alertas.length > 1 ? 's' : ''}`}
          </span>
          {saludOk && <CheckCircle size={15} className="text-emerald-400 flex-shrink-0" />}
          {!saludOk && <AlertTriangle size={15} className="text-amber-400 flex-shrink-0" />}
        </div>

        {/* ── Hero números ── */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Ingresos', value: mxn(resumen.ingresos_mes), sub: `↑ vs mes ant.`, trend: 'up' as const },
            { label: 'Utilidad', value: mxn(resumen.utilidad_mes),
              sub: `${kpis.margen_bruto_pct.toFixed(1)}% margen`,
              trend: resumen.utilidad_mes >= 0 ? 'up' as const : 'down' as const },
            { label: 'Por Cobrar', value: mxn(resumen.por_cobrar),
              sub: `${resumen.facturas_mes} facturas`, trend: 'neutral' as const },
          ].map(k => <KPI key={k.label} dark={dark} {...k} />)}
        </div>

        {/* ── Tabs ── */}
        <div className={`flex gap-1 p-1 rounded-xl border ${dark ? 'bg-[#111] border-[#222]' : 'bg-gray-100 border-gray-200'}`}>
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                tab === t.id
                  ? 'bg-amber-500 text-black shadow-sm'
                  : dark ? 'text-[#666] hover:text-[#aaa]' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              {t.icon}
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          ))}
        </div>

        {/* ── Tab: Financiero ── */}
        {tab === 'financiero' && (
          <div className="space-y-4 animate-fade-up">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <KPI dark={dark} label="Ingresos"    value={mxn(resumen.ingresos_mes)} sub={tcVal > 0 ? `≈ USD ${Math.round(resumen.ingresos_mes/tcVal).toLocaleString()}` : undefined} trend="up" />
              <KPI dark={dark} label="Egresos"     value={mxn(resumen.gastos_mes)}   sub={tcVal > 0 ? `≈ USD ${Math.round(resumen.gastos_mes/tcVal).toLocaleString()}` : undefined} trend="down" />
              <KPI dark={dark} label="Utilidad"    value={mxn(resumen.utilidad_mes)} sub={`${kpis.margen_bruto_pct.toFixed(1)}% margen`} trend={resumen.utilidad_mes >= 0 ? 'up' : 'down'} />
              <KPI dark={dark} label="Facturas"    value={String(resumen.facturas_mes)} sub={`${resumen.total_facturas} total`} trend="neutral" />
            </div>
            <div className={`rounded-2xl border p-4 ${card}`}>
              <p className="text-sm font-semibold mb-1">Tendencia 6 meses</p>
              <p className={`text-xs mb-4 ${muted}`}>Ingresos vs Egresos (MXN)</p>
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="gI" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#10b981" stopOpacity={dark ? 0.2 : 0.15} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gE" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#ef4444" stopOpacity={dark ? 0.15 : 0.1} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                  <XAxis dataKey="mes" tick={{ fontSize: 11, fill: axisFill }} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 10, fill: axisFill }} axisLine={false} tickLine={false} />
                  <Tooltip content={<ChartTip dark={dark} />} />
                  <Area type="monotone" dataKey="Ingresos" stroke="#10b981" fill="url(#gI)" strokeWidth={2} />
                  <Area type="monotone" dataKey="Egresos"  stroke="#ef4444" fill="url(#gE)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* ── Tab: Fiscal ── */}
        {tab === 'fiscal' && cierre && (
          <div className="space-y-4 animate-fade-up">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <KPI dark={dark} label="IVA Neto"    value={mxn(cierre.iva_neto)}      sub={`Cobrado: ${mxn(cierre.iva_cobrado)}`} trend={cierre.iva_neto > 0 ? 'down' : 'up'} />
              <KPI dark={dark} label="ISR Estimado" value={mxn(cierre.isr_estimado)} sub="Art. 14 LISR" trend="neutral" />
              <KPI dark={dark} label="EBITDA"       value={mxn(cierre.ebitda)}       sub={`${cierre.margen_neto_pct?.toFixed(1) ?? 0}% margen`} trend={cierre.ebitda >= 0 ? 'up' : 'down'} />
              <KPI dark={dark} label="PTU Estimada" value={mxn(cierre.ptu)}          sub="10% utilidad fiscal" trend="neutral" />
            </div>
            <div className={`rounded-2xl border p-4 ${card}`}>
              <p className="text-sm font-semibold mb-4">Composición fiscal del mes</p>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={[
                  { name: 'IVA cobrado', v: cierre.iva_cobrado },
                  { name: 'IVA pagado',  v: cierre.iva_pagado  },
                  { name: 'IVA neto',    v: cierre.iva_neto    },
                  { name: 'ISR',         v: cierre.isr_estimado },
                  { name: 'PTU',         v: cierre.ptu          },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                  <XAxis dataKey="name" tick={{ fontSize: 9, fill: axisFill }} axisLine={false} tickLine={false} />
                  <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 9, fill: axisFill }} axisLine={false} tickLine={false} />
                  <Tooltip content={<ChartTip dark={dark} />} />
                  <Bar dataKey="v" name="Monto" fill="#D4AF37" radius={[4,4,0,0]} opacity={0.85} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
        {tab === 'fiscal' && !cierre && (
          <div className={`rounded-2xl border p-8 text-center ${card}`}>
            <BarChart2 size={32} className={`mx-auto mb-3 ${muted}`} />
            <p className={`text-sm ${muted}`}>Sin datos de cierre fiscal este mes</p>
          </div>
        )}

        {/* ── Tab: Flujo ── */}
        {tab === 'flujo' && (
          <div className="space-y-4 animate-fade-up">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <KPI dark={dark} label="Por Cobrar"      value={mxn(resumen.por_cobrar)} sub="Cuentas pendientes" trend="up" />
              <KPI dark={dark} label="Por Pagar"       value={mxn(resumen.por_pagar)}  sub="Compromisos activos" trend={resumen.por_pagar > resumen.por_cobrar ? 'down' : 'neutral'} />
              <KPI dark={dark} label="Ratio Cobro/Pago" value={kpis.ratio_cobro_pago > 0 ? `${kpis.ratio_cobro_pago.toFixed(2)}x` : '—'}
                sub={kpis.ratio_cobro_pago >= 1 ? 'Favorable' : 'Atención'} trend={kpis.ratio_cobro_pago >= 1 ? 'up' : 'down'} />
              <KPI dark={dark} label="Egresos mes"     value={mxn(resumen.gastos_mes)} sub={tcVal > 0 ? `≈ USD ${Math.round(resumen.gastos_mes/tcVal).toLocaleString()}` : undefined} trend="neutral" />
            </div>
            {/* Últimas transacciones */}
            <div className={`rounded-2xl border overflow-hidden ${card}`}>
              <div className={`px-4 py-3 border-b flex items-center justify-between ${dark ? 'border-[#2a2a2a]' : 'border-gray-100'}`}>
                <p className="text-sm font-semibold">Transacciones recientes</p>
                <Link href="/facturas" className="text-xs text-amber-500 hover:underline">Ver todas →</Link>
              </div>
              {facturas.length === 0 ? (
                <p className={`text-sm p-4 ${muted}`}>Sin facturas registradas</p>
              ) : (
                <div className={`divide-y ${dark ? 'divide-[#1e1e1e]' : 'divide-gray-50'}`}>
                  {facturas.slice(0, 6).map(f => {
                    const ing = f.tipo === 'ingreso'
                    return (
                      <div key={f.id} className="px-4 py-3 flex items-center gap-3">
                        <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${ing ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
                          {ing ? <ArrowUpRight size={12} className="text-emerald-500" /> : <ArrowDownRight size={12} className="text-red-500" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{ing ? f.emisor_nombre : f.receptor_nombre}</p>
                          <p className={`text-xs ${muted}`}>{f.folio} · {(f.fecha_emision || f.fecha || '').slice(0,10)}</p>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <p className={`text-sm font-bold ${ing ? 'text-emerald-500' : 'text-red-400'}`}>
                            {ing ? '+' : '-'}{mxn(f.total)}
                          </p>
                          <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                            f.estado === 'pagada' ? 'text-emerald-500 bg-emerald-500/10' :
                            f.estado === 'cancelada' ? `${muted} bg-gray-500/10` :
                            'text-amber-500 bg-amber-500/10'
                          }`}>{f.estado}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── Tab: IA & Bots ── */}
        {tab === 'ia' && (
          <div className="space-y-3 animate-fade-up">
            {[
              { href: '/brain',    icon: <Brain size={20} />, color: 'text-amber-500 bg-amber-500/10',   title: 'Brain IA',      sub: 'RAG fiscal · DeepSeek local · 4 capas' },
              { href: '/whatsapp', icon: <MessageCircle size={20} />, color: 'text-emerald-500 bg-emerald-500/10', title: 'WhatsApp', sub: 'Baileys · Estado · QR · Conversaciones' },
              { href: '/telegram', icon: <Send size={20} />, color: 'text-sky-500 bg-sky-500/10',        title: 'Telegram Bot',  sub: '5 skills · Brain IA · Multi-tenant' },
              { href: '/academy',  icon: <Zap size={20} />,  color: 'text-purple-500 bg-purple-500/10', title: 'Academy',       sub: 'Cursos · XP · Misiones · Gamificación' },
              { href: '/admin',    icon: <Building2 size={20} />, color: 'text-blue-500 bg-blue-500/10', title: 'Admin',         sub: 'Multi-tenant · AI OS · Configuración' },
            ].map(item => (
              <Link key={item.href} href={item.href}
                className={`flex items-center gap-4 rounded-2xl border p-4 transition-all group ${
                  dark
                    ? 'bg-[#161616] border-[#2a2a2a] hover:border-amber-500/30'
                    : 'bg-white border-gray-100 hover:border-amber-200 shadow-sm'
                }`}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${item.color}`}>
                  {item.icon}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold">{item.title}</p>
                  <p className={`text-xs ${muted}`}>{item.sub}</p>
                </div>
                <ArrowUpRight size={14} className={`${muted} group-hover:text-amber-500 transition-colors`} />
              </Link>
            ))}

            {/* N8N status */}
            <div className={`rounded-2xl border p-4 ${dark ? 'bg-[#161616] border-[#2a2a2a]' : 'bg-white border-gray-100 shadow-sm'}`}>
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-semibold">N8N Automatizaciones</p>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 font-semibold">ACTIVO</span>
              </div>
              <p className={`text-xs ${muted} mb-3`}>Workflows de alerta matutina, vespertina y mapeo legal.</p>
              <a href="/n8n" target="_blank" rel="noopener"
                className="inline-flex items-center gap-1.5 text-xs text-amber-500 hover:underline font-medium">
                Abrir N8N <ArrowUpRight size={11} />
              </a>
            </div>
          </div>
        )}

        {/* ── Alertas (siempre visible si hay) ── */}
        {alertas.length > 0 && (
          <div className="space-y-2">
            {alertas.map((a, i) => (
              <div key={i} className={`flex items-start gap-3 rounded-xl px-4 py-3 border ${
                dark ? 'bg-amber-500/5 border-amber-500/20' : 'bg-amber-50 border-amber-200'
              }`}>
                <AlertTriangle size={14} className="text-amber-500 mt-0.5 shrink-0" />
                <p className={`text-sm ${dark ? 'text-amber-300' : 'text-amber-700'}`}>{a}</p>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  )
}
