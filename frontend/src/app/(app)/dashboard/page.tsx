'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import { api, DashboardData, TipoCambio } from '@/lib/api'
import {
  Mic, MicOff, CheckCircle, XCircle, ArrowRight, Zap,
  Mail, FileText, AlertTriangle, Brain, MessageCircle,
  ChevronRight, Volume2, Sun, Moon, RefreshCw, Eye,
  Clock, TrendingUp, DollarSign, Bell, Play, Pause,
  CheckCheck, MoreHorizontal, Sparkles,
} from 'lucide-react'

// ── Types ──────────────────────────────────────────────────────────────────────
type ActionPriority = 'critica' | 'alta' | 'normal'
type ActionStatus   = 'pendiente' | 'aprobada' | 'rechazada' | 'delegada'
type ActionSource   = 'email' | 'factura' | 'sat' | 'whatsapp' | 'sistema' | 'banco'

interface AutoAction {
  id: string
  source: ActionSource
  title: string
  detail: string
  amount?: number
  priority: ActionPriority
  status: ActionStatus
  timestamp: string
  recommendation: string
  options: { label: string; action: string; style: 'approve' | 'reject' | 'delegate' | 'view' }[]
}

interface LiveEvent {
  id: string
  type: ActionSource
  msg: string
  time: string
  handled: boolean
}

// ── Helpers ────────────────────────────────────────────────────────────────────
const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

const relTime = (iso: string) => {
  const diff = Date.now() - new Date(iso).getTime()
  if (diff < 60000) return 'ahora mismo'
  if (diff < 3600000) return `hace ${Math.floor(diff / 60000)}m`
  if (diff < 86400000) return `hace ${Math.floor(diff / 3600000)}h`
  return `hace ${Math.floor(diff / 86400000)}d`
}

const SOURCE_META: Record<ActionSource, { icon: React.ReactNode; color: string; bg: string }> = {
  email:    { icon: <Mail size={14} />,        color: 'text-sky-400',     bg: 'bg-sky-400/10'     },
  factura:  { icon: <FileText size={14} />,    color: 'text-amber-400',   bg: 'bg-amber-400/10'   },
  sat:      { icon: <AlertTriangle size={14}/>, color: 'text-red-400',    bg: 'bg-red-400/10'     },
  whatsapp: { icon: <MessageCircle size={14}/>, color: 'text-emerald-400', bg: 'bg-emerald-400/10'},
  sistema:  { icon: <Brain size={14} />,       color: 'text-purple-400',  bg: 'bg-purple-400/10'  },
  banco:    { icon: <DollarSign size={14} />,  color: 'text-green-400',   bg: 'bg-green-400/10'   },
}

const PRIORITY_META: Record<ActionPriority, { label: string; color: string }> = {
  critica: { label: 'Crítica', color: 'text-red-400 bg-red-400/10 border-red-400/20' },
  alta:    { label: 'Alta',    color: 'text-amber-400 bg-amber-400/10 border-amber-400/20' },
  normal:  { label: 'Normal',  color: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
}

// Acciones de muestra mientras no hay datos reales
const SAMPLE_ACTIONS: AutoAction[] = [
  {
    id: '1',
    source: 'email',
    title: 'Solicitud de factura — Fourgea Industrial',
    detail: 'Correo recibido: "Necesitamos factura por $38,500 servicio de filtración marzo". Datos extraídos automáticamente.',
    amount: 38500,
    priority: 'alta',
    status: 'pendiente',
    timestamp: new Date(Date.now() - 8 * 60000).toISOString(),
    recommendation: 'Generar CFDI 4.0 ingreso. RFC Fourgea validado en SAT. Sin adeudos previos.',
    options: [
      { label: 'Generar Factura', action: 'generar_cfdi', style: 'approve' },
      { label: 'Ver detalle',     action: 'ver_email',    style: 'view'    },
      { label: 'Rechazar',        action: 'rechazar',     style: 'reject'  },
    ],
  },
  {
    id: '2',
    source: 'sat',
    title: 'Declaración IVA vence en 3 días',
    detail: 'IVA neto calculado: $12,340. Pago domiciliado disponible. SAT confirma periodo feb 2026.',
    amount: 12340,
    priority: 'critica',
    status: 'pendiente',
    timestamp: new Date(Date.now() - 25 * 60000).toISOString(),
    recommendation: 'Presentar declaración antes del 17. Brain IA preparó el formato. Solo requiere tu aprobación.',
    options: [
      { label: 'Aprobar y enviar', action: 'enviar_sat',   style: 'approve'  },
      { label: 'Revisar cifras',   action: 'ver_cierre',   style: 'view'     },
      { label: 'Delegar contador', action: 'delegar',      style: 'delegate' },
    ],
  },
  {
    id: '3',
    source: 'banco',
    title: 'Depósito sin identificar — $15,200',
    detail: 'BBVA detectó depósito en cuenta 3871 sin referencia. Posible pago cliente Distribuidora Torres.',
    amount: 15200,
    priority: 'alta',
    status: 'pendiente',
    timestamp: new Date(Date.now() - 2 * 3600000).toISOString(),
    recommendation: 'Historial sugiere: pago factura F-2024-089 de Torres. Aplicar cobro automáticamente.',
    options: [
      { label: 'Confirmar pago',   action: 'aplicar_cobro', style: 'approve'  },
      { label: 'Ver movimiento',   action: 'ver_banco',     style: 'view'     },
      { label: 'Reasignar',        action: 'reasignar',     style: 'delegate' },
    ],
  },
  {
    id: '4',
    source: 'whatsapp',
    title: 'Cliente pregunta estado nómina',
    detail: 'WhatsApp +526621234567: "¿Ya está lista la nómina de esta quincena?" Brain IA tiene respuesta lista.',
    priority: 'normal',
    status: 'pendiente',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    recommendation: 'Nómina procesada al 100%. Respuesta automática preparada. Aprobar para enviar.',
    options: [
      { label: 'Enviar respuesta', action: 'enviar_wa',   style: 'approve' },
      { label: 'Ver nómina',       action: 'ver_nomina',  style: 'view'    },
      { label: 'Modificar resp.',  action: 'editar',      style: 'delegate'},
    ],
  },
]

const SAMPLE_EVENTS: LiveEvent[] = [
  { id: 'e1', type: 'email',    msg: 'Fourgea Industrial — solicitud de factura recibida',  time: new Date(Date.now() - 8*60000).toISOString(),   handled: false },
  { id: 'e2', type: 'sistema',  msg: 'Brain IA procesó 4 correos y generó 3 tareas',        time: new Date(Date.now() - 12*60000).toISOString(),  handled: true  },
  { id: 'e3', type: 'sat',      msg: 'Alerta declaración IVA — 3 días para vencer',         time: new Date(Date.now() - 25*60000).toISOString(),  handled: false },
  { id: 'e4', type: 'banco',    msg: 'Depósito no identificado $15,200 — BBVA',             time: new Date(Date.now() - 2*3600000).toISOString(), handled: false },
  { id: 'e5', type: 'whatsapp', msg: 'Nuevo mensaje de cliente sobre nómina quincena',      time: new Date(Date.now() - 45*60000).toISOString(),  handled: false },
  { id: 'e6', type: 'factura',  msg: 'CFDI cancelado por SAT — F-2024-071 requiere sustit.',time: new Date(Date.now() - 3*3600000).toISOString(), handled: true  },
  { id: 'e7', type: 'sistema',  msg: 'Watchdog: todos los servicios operando correctamente',time: new Date(Date.now() - 5*60000).toISOString(),   handled: true  },
]

// ── Voice hook ─────────────────────────────────────────────────────────────────
function useVoice(onResult: (text: string) => void) {
  const [listening, setListening] = useState(false)
  const [supported] = useState(() => typeof window !== 'undefined' && 'webkitSpeechRecognition' in window)
  const recRef = useRef<any>(null)

  const toggle = useCallback(() => {
    if (!supported) return
    if (listening) {
      recRef.current?.stop()
      setListening(false)
      return
    }
    const SR = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
    const rec = new SR()
    rec.lang = 'es-MX'
    rec.continuous = false
    rec.interimResults = false
    rec.onresult = (e: any) => {
      const text = e.results[0]?.[0]?.transcript || ''
      if (text) onResult(text)
    }
    rec.onend = () => setListening(false)
    rec.start()
    recRef.current = rec
    setListening(true)
  }, [listening, supported, onResult])

  const speak = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utter = new SpeechSynthesisUtterance(text)
    utter.lang = 'es-MX'
    utter.rate = 1.05
    window.speechSynthesis.speak(utter)
  }, [])

  return { listening, supported, toggle, speak }
}

// ── Action Card ────────────────────────────────────────────────────────────────
function ActionCard({
  action, dark, onAction,
}: { action: AutoAction; dark: boolean; onAction: (id: string, act: string) => void }) {
  const sm = SOURCE_META[action.source]
  const pm = PRIORITY_META[action.priority]
  const done = action.status !== 'pendiente'

  return (
    <div className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
      done ? 'opacity-50 scale-98' :
      dark  ? 'bg-[#0f0f0f] border-[#2a2a2a] hover:border-[#D4AF37]/30' :
              'bg-white border-gray-100 shadow-sm hover:shadow-md'
    }`}>
      {/* Priority stripe */}
      <div className={`h-0.5 w-full ${
        action.priority === 'critica' ? 'bg-red-500' :
        action.priority === 'alta'    ? 'bg-amber-500' : 'bg-emerald-500'
      }`} />

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start gap-3 mb-3">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 ${sm.bg}`}>
            <span className={sm.color}>{sm.icon}</span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-0.5">
              <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${pm.color}`}>
                {pm.label}
              </span>
              <span className={`text-[10px] ${dark ? 'text-[#555]' : 'text-gray-400'}`}>
                {relTime(action.timestamp)}
              </span>
            </div>
            <p className={`text-sm font-semibold leading-tight ${dark ? 'text-[#E8E8E8]' : 'text-gray-900'}`}>
              {action.title}
            </p>
          </div>
          {action.amount && (
            <div className="text-right flex-shrink-0">
              <p className="text-sm font-black text-amber-500 tabular-nums">{mxn(action.amount)}</p>
            </div>
          )}
        </div>

        {/* Detail */}
        <p className={`text-xs leading-relaxed mb-3 ${dark ? 'text-[#888]' : 'text-gray-500'}`}>
          {action.detail}
        </p>

        {/* AI Recommendation */}
        <div className={`flex items-start gap-2 rounded-xl p-3 mb-4 ${
          dark ? 'bg-[#D4AF37]/5 border border-[#D4AF37]/15' : 'bg-amber-50 border border-amber-100'
        }`}>
          <Sparkles size={12} className="text-amber-500 mt-0.5 flex-shrink-0" />
          <p className={`text-xs leading-relaxed ${dark ? 'text-[#D4AF37]/80' : 'text-amber-700'}`}>
            <span className="font-semibold">Brain IA: </span>{action.recommendation}
          </p>
        </div>

        {/* Action buttons */}
        {!done ? (
          <div className="flex gap-2 flex-wrap">
            {action.options.map(opt => (
              <button
                key={opt.action}
                onClick={() => onAction(action.id, opt.action)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  opt.style === 'approve'  ? 'bg-emerald-500 hover:bg-emerald-400 text-white' :
                  opt.style === 'reject'   ? (dark ? 'bg-[#2a2a2a] hover:bg-red-500/20 text-red-400 border border-[#333]' : 'bg-gray-100 hover:bg-red-50 text-red-500 border border-gray-200') :
                  opt.style === 'delegate' ? (dark ? 'bg-[#2a2a2a] hover:bg-purple-500/20 text-purple-400 border border-[#333]' : 'bg-gray-100 hover:bg-purple-50 text-purple-500 border border-gray-200') :
                                             (dark ? 'bg-[#2a2a2a] text-[#aaa] border border-[#333] hover:border-[#555]' : 'bg-gray-100 text-gray-600 border border-gray-200')
                }`}
              >
                {opt.style === 'approve'  && <CheckCircle size={11} />}
                {opt.style === 'reject'   && <XCircle size={11} />}
                {opt.style === 'delegate' && <ArrowRight size={11} />}
                {opt.style === 'view'     && <Eye size={11} />}
                {opt.label}
              </button>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <CheckCheck size={14} className="text-emerald-500" />
            <span className="text-xs text-emerald-500 font-semibold capitalize">{action.status}</span>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [dash,    setDash]    = useState<DashboardData | null>(null)
  const [tc,      setTc]      = useState<TipoCambio | null>(null)
  const [dark,    setDark]    = useState(true)
  const [actions, setActions] = useState<AutoAction[]>(SAMPLE_ACTIONS)
  const [events,  setEvents]  = useState<LiveEvent[]>(SAMPLE_EVENTS)
  const [voice,   setVoice]   = useState('')
  const [aiReply, setAiReply] = useState('')
  const [pulse,   setPulse]   = useState(false)
  const [loading, setLoading] = useState(true)

  // Fetch real data
  useEffect(() => {
    Promise.allSettled([
      api.get<DashboardData>('/dashboard'),
      api.get<TipoCambio>('/tipo-cambio/hoy'),
    ]).then(([d, t]) => {
      if (d.status === 'fulfilled') setDash(d.value)
      if (t.status === 'fulfilled') setTc(t.value)
    }).finally(() => setLoading(false))
  }, [])

  // Poll for new events & actions every 30s
  useEffect(() => {
    const id = setInterval(() => {
      api.get<TipoCambio>('/tipo-cambio/hoy').then(setTc).catch(() => {})
      // Fetch pending tasks from Brain IA
      api.get<AutoAction[]>('/api/brain/tasks?status=pendiente').then(tasks => {
        if (tasks?.length) setActions(prev => {
          const ids = new Set(prev.map(a => a.id))
          const novel = tasks.filter((t: AutoAction) => !ids.has(t.id))
          if (novel.length) { setPulse(true); setTimeout(() => setPulse(false), 2000) }
          return [...novel, ...prev]
        })
      }).catch(() => {})
    }, 30_000)
    return () => clearInterval(id)
  }, [])

  // Voice handler
  const handleVoice = useCallback(async (text: string) => {
    setVoice(text)
    setAiReply('Procesando...')
    try {
      const res = await api.post<{ answer: string }>('/api/brain/ask', {
        question: text, channel: 'dashboard', tenant_id: dash?.tenant_id || 'default',
      })
      const reply = res.answer || 'Sin respuesta del Brain IA.'
      setAiReply(reply)
      speak(reply)
    } catch {
      setAiReply('No pude conectar con Brain IA.')
    }
  }, [dash])

  const { listening, supported, toggle: toggleMic, speak } = useVoice(handleVoice)

  const handleAction = useCallback(async (id: string, act: string) => {
    const status: ActionStatus = act === 'rechazar' ? 'rechazada' : act === 'delegar' ? 'delegada' : 'aprobada'
    setActions(prev => prev.map(a => a.id === id ? { ...a, status } : a))
    // Notify Brain IA
    try { await api.post('/api/brain/task/action', { task_id: id, action: act }) } catch {}
    // Add to live feed
    const target = actions.find(a => a.id === id)
    if (target) {
      setEvents(prev => [{
        id: `ev_${Date.now()}`,
        type: target.source,
        msg: `${target.title} — ${status}`,
        time: new Date().toISOString(),
        handled: true,
      }, ...prev.slice(0, 19)])
    }
  }, [actions])

  const pending  = actions.filter(a => a.status === 'pendiente')
  const resolved = actions.filter(a => a.status !== 'pendiente')
  const tcVal    = tc?.usd_mxn || tc?.tipo_cambio || 0
  const resumen  = dash?.resumen

  const bg    = dark ? 'bg-[#070707] text-[#E8E8E8]' : 'bg-gray-50 text-gray-900'
  const card  = dark ? 'bg-[#0f0f0f] border-[#1e1e1e]' : 'bg-white border-gray-100 shadow-sm'
  const muted = dark ? 'text-[#555]' : 'text-gray-400'

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>
      <div className="max-w-6xl mx-auto px-4 py-4 space-y-4">

        {/* ── Top bar ── */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${card}`}>
              <span className={`w-2 h-2 rounded-full animate-pulse ${pulse ? 'bg-amber-400' : 'bg-emerald-400'}`} />
              <span className="text-xs font-semibold">
                {pulse ? 'Nueva acción detectada' : 'Sistema activo'}
              </span>
            </div>
            {pending.length > 0 && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <Bell size={12} className="text-amber-500" />
                <span className="text-xs font-bold text-amber-500">{pending.length} pendiente{pending.length > 1 ? 's' : ''}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            {tcVal > 0 && (
              <div className={`px-3 py-1.5 rounded-xl border text-xs tabular-nums font-black text-amber-500 ${card}`}>
                ${tcVal.toFixed(2)} <span className={`font-normal ${muted}`}>USD/MXN</span>
              </div>
            )}
            <button onClick={() => setDark(d => !d)}
              className={`w-8 h-8 rounded-xl border flex items-center justify-center transition-all ${
                dark ? 'bg-[#161616] border-[#333] text-[#888] hover:text-amber-400' : 'bg-white border-gray-200 text-gray-400 hover:text-amber-500'
              }`}>
              {dark ? <Sun size={14} /> : <Moon size={14} />}
            </button>
          </div>
        </div>

        {/* ── KPI bar rápida ── */}
        {resumen && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              { l: 'Ingresos',    v: mxn(resumen.ingresos_mes), icon: <TrendingUp size={12} />,  color: 'text-emerald-400' },
              { l: 'Utilidad',    v: mxn(resumen.utilidad_mes), icon: <DollarSign size={12} />,  color: resumen.utilidad_mes >= 0 ? 'text-emerald-400' : 'text-red-400' },
              { l: 'Por Cobrar',  v: mxn(resumen.por_cobrar),   icon: <Clock size={12} />,        color: 'text-amber-400' },
              { l: 'Facturas',    v: String(resumen.facturas_mes), icon: <FileText size={12} />, color: 'text-sky-400' },
            ].map(k => (
              <div key={k.l} className={`rounded-xl border px-3 py-2.5 flex items-center gap-2.5 ${card}`}>
                <span className={k.color}>{k.icon}</span>
                <div>
                  <p className={`text-[10px] uppercase tracking-wide ${muted}`}>{k.l}</p>
                  <p className="text-sm font-black tabular-nums">{k.v}</p>
                </div>
              </div>
            ))}
          </div>
        )}
        {!resumen && !loading && (
          <div className={`rounded-xl border px-4 py-3 text-sm ${muted} ${card}`}>
            Sin datos financieros · verificar conexión API
          </div>
        )}

        {/* ── Main 2-col layout ── */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">

          {/* ── LEFT: Cola de decisiones ── */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold flex items-center gap-2">
                  <Sparkles size={14} className="text-amber-500" />
                  Cola de decisiones
                </h2>
                <p className={`text-xs mt-0.5 ${muted}`}>
                  Brain IA detectó y preparó estas acciones. Solo aprueba o rechaza.
                </p>
              </div>
              {resolved.length > 0 && (
                <span className={`text-[10px] px-2 py-1 rounded-full border ${muted} border-current`}>
                  {resolved.length} resuelta{resolved.length > 1 ? 's' : ''} hoy
                </span>
              )}
            </div>

            {pending.length === 0 ? (
              <div className={`rounded-2xl border p-10 text-center ${card}`}>
                <CheckCheck size={32} className="mx-auto mb-3 text-emerald-500" />
                <p className="text-sm font-semibold text-emerald-400">Todo al día</p>
                <p className={`text-xs mt-1 ${muted}`}>Brain IA está monitoreando. Te avisaré cuando haya algo.</p>
              </div>
            ) : (
              pending.map(action => (
                <ActionCard key={action.id} action={action} dark={dark} onAction={handleAction} />
              ))
            )}

            {/* Resolved (collapsed) */}
            {resolved.length > 0 && (
              <div className={`rounded-xl border px-4 py-3 ${card}`}>
                <div className="flex items-center gap-2">
                  <CheckCheck size={13} className="text-emerald-500" />
                  <span className="text-xs font-semibold text-emerald-500">
                    {resolved.length} acción{resolved.length > 1 ? 'es resueltas' : ' resuelta'} en esta sesión
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* ── RIGHT: Live feed + Voice ── */}
          <div className="space-y-4">

            {/* Voice command */}
            <div className={`rounded-2xl border p-4 ${card}`}>
              <div className="flex items-center gap-2 mb-3">
                <Brain size={14} className="text-amber-500" />
                <span className="text-xs font-semibold">Consulta por voz</span>
                {!supported && <span className={`text-[10px] ${muted}`}>(solo Chrome)</span>}
              </div>

              <button
                onClick={toggleMic}
                disabled={!supported}
                className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all ${
                  listening
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                    : dark
                      ? 'bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/20'
                      : 'bg-amber-50 hover:bg-amber-100 text-amber-600 border border-amber-200'
                }`}
              >
                {listening ? <MicOff size={16} /> : <Mic size={16} />}
                {listening ? 'Escuchando...' : 'Hablar con Brain IA'}
              </button>

              {voice && (
                <div className="mt-3 space-y-2">
                  <div className={`rounded-xl px-3 py-2 text-xs ${dark ? 'bg-[#1a1a1a]' : 'bg-gray-50'}`}>
                    <span className={muted}>Tú: </span>
                    <span className="font-medium">{voice}</span>
                  </div>
                  {aiReply && (
                    <div className={`rounded-xl px-3 py-2 text-xs border ${
                      dark ? 'bg-[#D4AF37]/5 border-[#D4AF37]/15 text-[#D4AF37]/90' : 'bg-amber-50 border-amber-100 text-amber-700'
                    }`}>
                      <div className="flex items-start gap-1.5">
                        <Volume2 size={11} className="mt-0.5 flex-shrink-0" />
                        <span>{aiReply}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Live feed */}
            <div className={`rounded-2xl border overflow-hidden ${card}`}>
              <div className={`px-4 py-3 border-b flex items-center justify-between ${dark ? 'border-[#1e1e1e]' : 'border-gray-100'}`}>
                <div className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs font-semibold">Actividad en vivo</span>
                </div>
                <span className={`text-[10px] ${muted}`}>{events.length} eventos hoy</span>
              </div>
              <div className={`divide-y max-h-[400px] overflow-y-auto ${dark ? 'divide-[#131313]' : 'divide-gray-50'}`}>
                {events.map(ev => {
                  const sm = SOURCE_META[ev.type]
                  return (
                    <div key={ev.id} className={`flex items-start gap-3 px-4 py-3 transition-colors ${
                      ev.handled
                        ? dark ? 'opacity-40' : 'opacity-50'
                        : dark ? 'hover:bg-[#141414]' : 'hover:bg-gray-50'
                    }`}>
                      <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${sm.bg}`}>
                        <span className={`${sm.color} scale-90`}>{sm.icon}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-xs leading-snug ${ev.handled ? '' : 'font-medium'}`}>{ev.msg}</p>
                        <p className={`text-[10px] mt-0.5 ${muted}`}>{relTime(ev.time)}</p>
                      </div>
                      {!ev.handled && (
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0 mt-1.5" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Quick actions */}
            <div className={`rounded-2xl border p-4 ${card}`}>
              <p className="text-xs font-semibold mb-3">Acciones rápidas</p>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { label: 'Nueva factura', href: '/facturas/nueva', color: 'text-amber-500' },
                  { label: 'Consultar SAT', href: '/fiscal', color: 'text-red-400' },
                  { label: 'Ver nómina',    href: '/nomina',  color: 'text-emerald-400' },
                  { label: 'Brain IA',      href: '/brain',   color: 'text-purple-400' },
                ].map(item => (
                  <a key={item.href} href={item.href}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      dark ? 'bg-[#161616] hover:bg-[#1e1e1e] border border-[#2a2a2a]' : 'bg-gray-50 hover:bg-gray-100 border border-gray-100'
                    } ${item.color}`}
                  >
                    <ChevronRight size={10} />
                    {item.label}
                  </a>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
