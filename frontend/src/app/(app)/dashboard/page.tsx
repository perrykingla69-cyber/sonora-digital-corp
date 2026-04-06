'use client'

import { useEffect, useState, useCallback } from 'react'
import { api } from '@/lib/api'
import { getUser } from '@/lib/auth'
import {
  FileText, TrendingUp, DollarSign, AlertTriangle, CheckCircle,
  ExternalLink, Brain, Zap, Shield, Clock, ChevronRight,
  RefreshCw, MessageCircle, GraduationCap, Star, CheckSquare,
  ArrowRight, Info, Bot,
} from 'lucide-react'
import Link from 'next/link'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts'

// ── Helpers ────────────────────────────────────────────────────────────────────
const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

// ── Datos de tendencia mensual (se reemplaza con /dashboard/trends cuando exista) ──
const TREND_DATA = [
  { mes: 'Ene', ingresos: 42000, gastos: 28500, utilidad: 13500 },
  { mes: 'Feb', ingresos: 48500, gastos: 32400, utilidad: 16100 },
  { mes: 'Mar', ingresos: 52300, gastos: 34800, utilidad: 17500 },
  { mes: 'Abr', ingresos: 18700, gastos: 12100, utilidad: 6600  },
]

const PIE_DATA = [
  { name: 'Facturas pagadas', value: 68 },
  { name: 'Por cobrar',       value: 22 },
  { name: 'Canceladas',       value: 10 },
]

const CHART_COLORS = { ingresos: '#C8A84B', gastos: '#9CA3AF', utilidad: '#2D6A4F' }
const PIE_COLORS   = ['#2D6A4F', '#C8A84B', '#D1D5DB']

// Tooltip personalizado sovereign
function SovereignTooltip({ active, payload, label }: { active?: boolean; payload?: {name: string; value: number; color: string}[]; label?: string }) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass rounded-xl px-3 py-2 text-xs shadow-lg">
      <p className="font-semibold text-sovereign-text mb-1">{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {mxn(p.value)}
        </p>
      ))}
    </div>
  )
}

// ── Links oficiales ────────────────────────────────────────────────────────────
const OFFICIAL_LINKS = [
  { label: 'SAT — Portal Principal',       href: 'https://www.sat.gob.mx',             color: 'text-red-600'    },
  { label: 'SAT — Buzón Tributario',       href: 'https://www.buzonjuridico.sat.gob.mx', color: 'text-red-600'  },
  { label: 'DOF — Diario Oficial',         href: 'https://www.dof.gob.mx',             color: 'text-blue-600'   },
  { label: 'VUCEM — Ventanilla Única',     href: 'https://www.ventanillaunica.gob.mx', color: 'text-green-700'  },
  { label: 'IMSS — Portal Empresas',       href: 'https://www.imss.gob.mx/empresas',   color: 'text-teal-700'   },
  { label: 'INFONAVIT — Patrones',         href: 'https://patronos.infonavit.org.mx',  color: 'text-orange-600' },
]

// ── Beneficios clave ───────────────────────────────────────────────────────────
const BENEFITS = [
  { icon: Clock,       text: 'Ahorra hasta 12 horas de trabajo contable al mes',         color: 'text-amber-600'   },
  { icon: Shield,      text: 'Cumplimiento fiscal garantizado con el SAT en todo momento', color: 'text-green-700'  },
  { icon: DollarSign,  text: 'Evita multas y recargos con alertas automáticas de vencimientos', color: 'text-blue-600' },
  { icon: Brain,       text: 'HERMES responde tus dudas fiscales 24/7 sin costo adicional', color: 'text-purple-600' },
  { icon: FileText,    text: 'Facturación CFDI 4.0 en segundos, directa al SAT',          color: 'text-amber-600'   },
  { icon: TrendingUp,  text: 'Reportes financieros en tiempo real para tomar mejores decisiones', color: 'text-green-700' },
]

// ── Tareas delegables a HERMES ─────────────────────────────────────────────────
const DELEGATE_TASKS = [
  { id: 1, label: 'Generar factura de venta',        cmd: '/facturas',  priority: 'alta'   },
  { id: 2, label: 'Calcular ISR del mes',            cmd: '/cierre',    priority: 'normal' },
  { id: 3, label: 'Verificar alertas SAT',           cmd: '/alertas',   priority: 'critica'},
  { id: 4, label: 'Conciliar movimientos bancarios', cmd: '/cierre',    priority: 'alta'   },
  { id: 5, label: 'Calcular nómina quincenal',       cmd: '/nomina',    priority: 'normal' },
]

const PRIORITY_STYLE: Record<string, string> = {
  critica: 'bg-red-50 border-red-200 text-red-700',
  alta:    'bg-amber-50 border-amber-200 text-amber-700',
  normal:  'bg-green-50 border-green-200 text-green-700',
}

// ── Componente legal ───────────────────────────────────────────────────────────
function LegalNotice({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-2 px-3 py-2 rounded-lg bg-blue-50 border border-blue-100 text-xs text-blue-700">
      <Info size={13} className="mt-0.5 shrink-0" />
      <span>{text}</span>
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const user = getUser()
  const nombre = user?.nombre?.split(' ')[0] || 'Empresario'

  const [stats, setStats]       = useState({ facturas: 0, pendiente: 0, clientes: 0, ahorro: 48000 })
  const [tc, setTc]             = useState<number | null>(null)
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [hermesMsg, setHermesMsg]   = useState('')
  const [hermesReply, setHermesReply] = useState('')
  const [hermesLoading, setHermesLoading] = useState(false)

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    try {
      const [dash, tipoCambio] = await Promise.allSettled([
        api.get('/dashboard'),
        api.get('/tipo-cambio/hoy'),
      ])
      if (dash.status === 'fulfilled') {
        const d = (dash.value as { data: Record<string, number> }).data
        setStats({
          facturas:  d.facturas_mes     ?? 0,
          pendiente: d.monto_pendiente  ?? 0,
          clientes:  d.clientes_activos ?? 0,
          ahorro:    d.horas_ahorradas  ? d.horas_ahorradas * 800 : 48000,
        })
      }
      if (tipoCambio.status === 'fulfilled') {
        const tc2 = (tipoCambio.value as { data: Record<string, number> }).data
        setTc(tc2?.usd_mxn ?? null)
      }
    } catch {}
    setLoading(false)
    setRefreshing(false)
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const askHermes = async () => {
    if (!hermesMsg.trim() || hermesLoading) return
    setHermesLoading(true)
    setHermesReply('')
    try {
      const res = await api.post('/api/brain/ask', { question: hermesMsg, channel: 'web' }) as { data: Record<string, string> }
      setHermesReply(res.data?.answer || res.data?.respuesta || 'Procesando tu consulta...')
    } catch {
      setHermesReply('No pude conectar con HERMES en este momento. Intenta de nuevo.')
    }
    setHermesLoading(false)
  }

  const hora = new Date().getHours()
  const saludo = hora < 12 ? 'Buenos días' : hora < 19 ? 'Buenas tardes' : 'Buenas noches'

  return (
    <div className="min-h-screen p-4 md:p-6 space-y-6 max-w-7xl mx-auto">

      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-sovereign-text font-display">
            {saludo}, {nombre}
          </h1>
          <p className="text-sm text-sovereign-muted mt-0.5">
            Tu empresa está protegida y al corriente con el SAT
          </p>
        </div>
        <button
          onClick={() => loadData(true)}
          className="p-2 rounded-xl glass hover:bg-white/80 transition-colors"
          title="Actualizar"
        >
          <RefreshCw size={16} className={`text-sovereign-muted ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── KPIs ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: 'Facturas este mes',  value: loading ? '—' : String(stats.facturas),   icon: FileText,    color: 'text-amber-600',  sub: 'emitidas' },
          { label: 'Por cobrar',         value: loading ? '—' : mxn(stats.pendiente),      icon: DollarSign,  color: 'text-blue-600',   sub: 'pendiente' },
          { label: 'Clientes activos',   value: loading ? '—' : String(stats.clientes),    icon: TrendingUp,  color: 'text-green-700',  sub: 'en plataforma' },
          { label: 'USD/MXN hoy',        value: tc ? `$${tc.toFixed(2)}` : '—',            icon: Zap,         color: 'text-purple-600', sub: 'tipo de cambio' },
        ].map((kpi, i) => (
          <div key={i} className="glass rounded-2xl p-4">
            <div className="flex items-start justify-between mb-2">
              <p className="text-xs text-sovereign-muted">{kpi.label}</p>
              <kpi.icon size={16} className={kpi.color} />
            </div>
            <p className="text-xl font-bold text-sovereign-text font-display">{kpi.value}</p>
            <p className="text-xs text-sovereign-muted mt-0.5">{kpi.sub}</p>
          </div>
        ))}
      </div>

      {/* ── Gráficas: tendencia mensual + distribución ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Bar chart — Ingresos vs Gastos vs Utilidad */}
        <div className="lg:col-span-2 glass rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <p className="font-semibold text-sovereign-text text-sm">Tendencia Financiera 2026</p>
            <span className="text-xs text-sovereign-muted">Ingresos · Gastos · Utilidad</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={TREND_DATA} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(200,168,75,0.12)" vertical={false} />
              <XAxis dataKey="mes" tick={{ fontSize: 11, fill: '#6B7280' }} axisLine={false} tickLine={false} />
              <YAxis
                tick={{ fontSize: 10, fill: '#9CA3AF' }}
                axisLine={false} tickLine={false}
                tickFormatter={v => `$${(v/1000).toFixed(0)}k`}
              />
              <Tooltip content={<SovereignTooltip />} />
              <Bar dataKey="ingresos" name="Ingresos" fill={CHART_COLORS.ingresos} radius={[4,4,0,0]} />
              <Bar dataKey="gastos"   name="Gastos"   fill={CHART_COLORS.gastos}   radius={[4,4,0,0]} />
              <Bar dataKey="utilidad" name="Utilidad" fill={CHART_COLORS.utilidad} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-4 mt-3 justify-center">
            {Object.entries(CHART_COLORS).map(([key, color]) => (
              <div key={key} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
                <span className="text-xs text-sovereign-muted capitalize">{key}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pie chart — distribución facturas */}
        <div className="glass rounded-2xl p-5">
          <p className="font-semibold text-sovereign-text text-sm mb-4">Estado de Facturas</p>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={PIE_DATA}
                cx="50%" cy="50%"
                innerRadius={48} outerRadius={70}
                paddingAngle={4}
                dataKey="value"
              >
                {PIE_DATA.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(255,255,255,0.95)', border: '1px solid rgba(200,168,75,0.2)', borderRadius: '12px', fontSize: 11 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {PIE_DATA.map((d, i) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: PIE_COLORS[i] }} />
                  <span className="text-xs text-sovereign-muted">{d.name}</span>
                </div>
                <span className="text-xs font-semibold text-sovereign-text">{d.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Acceso rápido a Agentes ── */}
      <div className="glass rounded-2xl p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Bot size={15} className="text-sovereign-gold" />
            <span className="text-sm font-semibold text-sovereign-text">Agentes IA activos</span>
          </div>
          {[
            { name: 'HERMES', color: 'bg-amber-100 text-amber-700' },
            { name: 'MYSTIC', color: 'bg-purple-100 text-purple-700' },
            { name: 'ClawBot', color: 'bg-sky-100 text-sky-700' },
            { name: 'AutoSeeder', color: 'bg-green-100 text-green-700' },
          ].map(a => (
            <span key={a.name} className={`text-xs px-2.5 py-1 rounded-full font-medium ${a.color}`}>
              <span className="w-1.5 h-1.5 rounded-full bg-current inline-block mr-1 opacity-60" />
              {a.name}
            </span>
          ))}
          <Link href="/agents" className="ml-auto text-xs text-sovereign-muted hover:text-sovereign-gold flex items-center gap-1 transition-colors">
            Ver panel completo <ArrowRight size={11} />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* ── HERMES interactivo ── */}
        <div className="lg:col-span-2 glass rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <div>
              <p className="font-semibold text-sovereign-text text-sm">HERMES — Tu Contador Digital</p>
              <p className="text-xs text-sovereign-muted">Disponible 24/7 · Respuesta inmediata</p>
            </div>
            <span className="ml-auto flex items-center gap-1 text-xs text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              En línea
            </span>
          </div>

          <LegalNotice text="HERMES proporciona orientación fiscal basada en la legislación mexicana vigente (CFF, LISR, LIVA, IMSS). Para decisiones de alta complejidad, complementa con un contador certificado." />

          <div className="flex gap-2">
            <input
              value={hermesMsg}
              onChange={e => setHermesMsg(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && askHermes()}
              placeholder="Pregunta algo: ¿cuándo vence mi declaración?, ¿cómo cancelo una factura?..."
              className="flex-1 px-3 py-2.5 rounded-xl border border-sovereign-gold/20 bg-white/70 text-sm text-sovereign-text placeholder:text-sovereign-muted focus:outline-none focus:border-sovereign-gold/50"
            />
            <button
              onClick={askHermes}
              disabled={hermesLoading || !hermesMsg.trim()}
              className="px-4 py-2.5 rounded-xl bg-sovereign-gold text-white text-sm font-medium disabled:opacity-50 hover:bg-amber-500 transition-colors"
            >
              {hermesLoading ? '...' : 'Preguntar'}
            </button>
          </div>

          {hermesReply && (
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-100 text-sm text-sovereign-text whitespace-pre-wrap">
              {hermesReply}
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            {['¿Cuándo vence el IVA?', '¿Cómo timbro una factura?', 'Diferencia ISR vs RESICO'].map(q => (
              <button
                key={q}
                onClick={() => { setHermesMsg(q); }}
                className="px-3 py-1 rounded-full text-xs bg-white border border-sovereign-gold/20 text-sovereign-muted hover:text-sovereign-text hover:border-sovereign-gold/40 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* ── Acciones rápidas ── */}
        <div className="glass rounded-2xl p-5 space-y-3">
          <p className="font-semibold text-sovereign-text text-sm">Acceso rápido</p>
          {[
            { label: 'Nueva factura',         href: '/facturas', icon: FileText,       color: 'bg-amber-50 text-amber-700'  },
            { label: 'Cierre del mes',        href: '/cierre',   icon: TrendingUp,     color: 'bg-blue-50 text-blue-700'    },
            { label: 'Tareas pendientes',     href: '/tasks',    icon: CheckSquare,    color: 'bg-green-50 text-green-700'  },
            { label: 'Academia HERMES',       href: '/academy',  icon: GraduationCap,  color: 'bg-purple-50 text-purple-700'},
            { label: 'Chat con HERMES',       href: '/chat',     icon: MessageCircle,  color: 'bg-amber-50 text-amber-700'  },
          ].map((item, i) => (
            <Link
              key={i}
              href={item.href}
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/60 transition-colors group"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${item.color}`}>
                <item.icon size={15} />
              </div>
              <span className="text-sm text-sovereign-text">{item.label}</span>
              <ChevronRight size={14} className="ml-auto text-sovereign-muted group-hover:text-sovereign-text transition-colors" />
            </Link>
          ))}
        </div>
      </div>

      {/* ── Tareas delegables a HERMES ── */}
      <div className="glass rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <p className="font-semibold text-sovereign-text text-sm">Delega a HERMES</p>
          <span className="text-xs text-sovereign-muted">Tareas que HERMES puede hacer por ti</span>
        </div>
        <LegalNotice text="Cada acción ejecutada por HERMES se registra con timestamp y referencia legal aplicable (artículo de ley). Siempre tienes control y aprobación final." />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {DELEGATE_TASKS.map(task => (
            <div key={task.id} className={`flex items-center justify-between p-3 rounded-xl border ${PRIORITY_STYLE[task.priority]}`}>
              <div className="flex items-center gap-2">
                <CheckSquare size={14} />
                <span className="text-sm font-medium">{task.label}</span>
              </div>
              <Link href={task.cmd} className="text-xs underline underline-offset-2 opacity-70 hover:opacity-100">
                Ir
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* ── Beneficios ── */}
      <div className="glass rounded-2xl p-5 space-y-3">
        <div className="flex items-center gap-2">
          <Star size={16} className="text-amber-500" />
          <p className="font-semibold text-sovereign-text text-sm">Por qué HERMES transforma tu empresa</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {BENEFITS.map((b, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/50 border border-white/80">
              <b.icon size={16} className={`mt-0.5 shrink-0 ${b.color}`} />
              <p className="text-sm text-sovereign-text">{b.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Links oficiales ── */}
      <div className="glass rounded-2xl p-5 space-y-3">
        <div className="flex items-center gap-2">
          <Shield size={16} className="text-green-700" />
          <p className="font-semibold text-sovereign-text text-sm">Portales oficiales — siempre en línea</p>
          <span className="ml-auto text-xs text-sovereign-muted">Acceso directo a fuentes gubernamentales</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {OFFICIAL_LINKS.map((link, i) => (
            <a
              key={i}
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/60 border border-white/80 hover:bg-white transition-colors group"
            >
              <ExternalLink size={12} className={`shrink-0 ${link.color}`} />
              <span className={`text-xs font-medium ${link.color} group-hover:underline`}>{link.label}</span>
            </a>
          ))}
        </div>
        <LegalNotice text="HERMES integra y monitorea cambios en DOF, SAT y normativas IMSS/INFONAVIT. Te notificamos automáticamente cuando hay actualizaciones que afectan tu empresa." />
      </div>

      {/* ── Academia preview ── */}
      <div className="glass rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <GraduationCap size={16} className="text-purple-600" />
            <p className="font-semibold text-sovereign-text text-sm">Academia HERMES</p>
          </div>
          <Link href="/academy" className="text-xs text-sovereign-muted hover:text-sovereign-text flex items-center gap-1">
            Ver todo <ArrowRight size={12} />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { title: 'Facturación CFDI 4.0 sin errores',         tag: 'Fiscal',       tiempo: '8 min' },
            { title: 'Cómo reducir ISR legalmente en tu empresa', tag: 'Impuestos',    tiempo: '12 min' },
            { title: 'Nómina IMSS: errores que cuestan miles',    tag: 'Nómina',       tiempo: '10 min' },
          ].map((curso, i) => (
            <Link key={i} href="/academy" className="p-3 rounded-xl bg-white/50 border border-white/80 hover:bg-white transition-colors group">
              <span className="text-xs text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">{curso.tag}</span>
              <p className="text-sm font-medium text-sovereign-text mt-2 group-hover:text-amber-700 transition-colors">{curso.title}</p>
              <p className="text-xs text-sovereign-muted mt-1">{curso.tiempo} de lectura</p>
            </Link>
          ))}
        </div>
      </div>

    </div>
  )
}
