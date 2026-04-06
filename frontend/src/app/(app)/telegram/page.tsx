'use client'

import { useEffect, useState, type ElementType } from 'react'
import { api, StatusData } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import {
  Send, CheckCircle, XCircle, ExternalLink, Terminal,
  Bot, User, ShoppingCart, HelpCircle, MessageSquare, Zap,
} from 'lucide-react'

interface LogMsg {
  id: string
  sender: string
  message: string
  intent: 'order' | 'inquiry' | 'support' | 'fiscal' | 'other'
  response: string
  ts: string
}

const INTENT_META: Record<LogMsg['intent'], { label: string; color: string; icon: ElementType }> = {
  order:   { label: 'Pedido',   color: 'bg-emerald-100 text-emerald-700', icon: ShoppingCart },
  inquiry: { label: 'Consulta', color: 'bg-blue-100 text-blue-700',       icon: HelpCircle   },
  support: { label: 'Soporte',  color: 'bg-amber-100 text-amber-700',     icon: MessageSquare},
  fiscal:  { label: 'Fiscal',   color: 'bg-purple-100 text-purple-700',   icon: Zap          },
  other:   { label: 'Otro',     color: 'bg-gray-100 text-gray-600',       icon: Bot          },
}

// Simula historial de mensajes recientes del bot (reemplazar con /api/telegram/log cuando exista)
const MOCK_LOG: LogMsg[] = [
  {
    id: 'tg-001',
    sender: 'Luis Daniel',
    message: '/dashboard',
    intent: 'inquiry',
    response: '📊 Resumen financiero:\n• Facturas emitidas: 12\n• Por cobrar: $24,500 MXN\n• USD/MXN: $17.23',
    ts: '10:30',
  },
  {
    id: 'tg-002',
    sender: 'Cliente RYE',
    message: '¿Cuándo vence mi factura F-0047?',
    intent: 'inquiry',
    response: '📋 Factura F-0047:\nVencimiento: 15 Abr 2026\nMonto: $8,750 MXN\nEstado: Pendiente ⚠️',
    ts: '10:15',
  },
  {
    id: 'tg-003',
    sender: 'Luis Daniel',
    message: '¿Cuál es la tasa de IVA para exportaciones?',
    intent: 'fiscal',
    response: '⚖️ IVA Exportaciones:\nTasa: 0% (tasa cero, Art. 29 LIVA)\nRequiere: CFDI de exportación + pedimento aduanal\n\n(Fuente: LIVA Art. 29, 2024)',
    ts: '09:52',
  },
  {
    id: 'tg-004',
    sender: 'Empleado',
    message: '/tasks',
    intent: 'support',
    response: '✅ Tareas pendientes:\n1. Declaración IVA — vence 17 Abr 🔴\n2. Nómina quincenal — vence 20 Abr 🟡\n3. Revisión facturas extranjeras 🟢',
    ts: '09:30',
  },
]

const COMANDOS = [
  { cmd: '/start',     desc: 'Menú principal con botones' },
  { cmd: '/login',     desc: '/login email password — autenticación' },
  { cmd: '/dashboard', desc: 'Resumen financiero del mes' },
  { cmd: '/facturas',  desc: 'Últimas 8 facturas del tenant' },
  { cmd: '/cierre',    desc: 'Cierre mensual [año/mes]' },
  { cmd: '/tc',        desc: 'Tipo de cambio USD/MXN (Banxico)' },
  { cmd: '/mve',       desc: 'Manifestaciones de valor abiertas' },
  { cmd: '/tasks',     desc: 'Tareas pendientes GSD' },
  { cmd: '/ayuda',     desc: 'Lista completa de comandos' },
]

export default function TelegramPage() {
  const [status, setStatus] = useState<StatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [log] = useState<LogMsg[]>(MOCK_LOG)

  useEffect(() => {
    api.get<StatusData>('/status')
      .then(setStatus)
      .catch(() => null)
      .finally(() => setLoading(false))
  }, [])

  const botUrl = 'https://t.me/MysticAIBot'

  return (
    <div className="space-y-6 max-w-4xl">

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-sky-100 rounded-xl flex items-center justify-center">
          <Send size={22} className="text-sky-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-sovereign-text font-display">Telegram Bot</h1>
          <p className="text-sm text-sovereign-muted">HERMES Bot · Acceso a todas las funciones · 24/7</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ── Panel izquierdo: estado + comandos ── */}
        <div className="space-y-4">

          {/* Estado del bot */}
          <Card className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                loading ? 'bg-gray-100 animate-pulse' : status?.api === 'ok' ? 'bg-sky-100' : 'bg-red-100'
              }`}>
                {!loading && (status?.api === 'ok'
                  ? <CheckCircle size={24} className="text-sky-600" />
                  : <XCircle size={24} className="text-red-500" />
                )}
              </div>
              <div>
                <p className="font-semibold text-sovereign-text text-sm">
                  {loading ? 'Verificando...' : status?.api === 'ok' ? 'Bot Activo' : 'Bot Offline'}
                </p>
                <p className="text-xs text-sovereign-muted">
                  {status?.api === 'ok' ? 'API · DB · Redis OK' : 'Revisar hermes_agent'}
                </p>
              </div>
            </div>

            {status && (
              <div className="grid grid-cols-3 gap-2 mb-4">
                {[
                  { label: 'API', val: status.api },
                  { label: 'DB', val: status.db },
                  { label: 'Redis', val: status.redis },
                ].map(({ label, val }) => (
                  <div key={label} className="text-center p-2 rounded-lg bg-gray-50">
                    <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${val === 'ok' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                    <p className="text-xs text-sovereign-muted">{label}</p>
                  </div>
                ))}
              </div>
            )}

            <a
              href={botUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl transition-colors"
            >
              <ExternalLink size={14} />
              Abrir en Telegram
            </a>
          </Card>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Mensajes hoy', value: log.length, color: 'text-sky-600' },
              { label: 'Consultas', value: log.filter(m => m.intent === 'inquiry').length, color: 'text-blue-600' },
              { label: 'Fiscales', value: log.filter(m => m.intent === 'fiscal').length, color: 'text-purple-600' },
              { label: 'Soporte', value: log.filter(m => m.intent === 'support').length, color: 'text-amber-600' },
            ].map(({ label, value, color }) => (
              <div key={label} className="glass rounded-xl p-3 text-center">
                <p className={`text-xl font-bold ${color}`}>{value}</p>
                <p className="text-xs text-sovereign-muted mt-0.5">{label}</p>
              </div>
            ))}
          </div>

          {/* Comandos */}
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-3">
              <Terminal size={14} className="text-sovereign-muted" />
              <h2 className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider">Comandos</h2>
            </div>
            <div className="space-y-1">
              {COMANDOS.map(({ cmd, desc }) => (
                <div key={cmd} className="flex items-start gap-2 py-1.5 border-b border-gray-50 last:border-0">
                  <code className="text-xs bg-gray-100 text-blue-700 px-1.5 py-0.5 rounded font-mono shrink-0">{cmd}</code>
                  <p className="text-xs text-sovereign-muted leading-tight">{desc}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* ── Panel derecho: historial de mensajes con intents ── */}
        <div className="lg:col-span-2">
          <div className="module-card rounded-2xl overflow-hidden">
            {/* Header estilo Telegram */}
            <div className="bg-gradient-to-r from-sky-500 to-blue-600 px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-white/20 rounded-full flex items-center justify-center">
                  <Bot size={18} className="text-white" />
                </div>
                <div>
                  <p className="font-semibold text-white text-sm">HERMES Bot</p>
                  <p className="text-xs text-blue-100">Asistente fiscal 24/7</p>
                </div>
                <div className="ml-auto flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                  <span className="text-xs text-white">En línea</span>
                </div>
              </div>
            </div>

            {/* Mensajes */}
            <div className="h-96 overflow-y-auto p-4 space-y-5 bg-slate-50">
              {log.length === 0 ? (
                <div className="text-center text-sovereign-muted py-8">
                  <Bot size={32} className="mx-auto mb-2 opacity-40" />
                  <p className="text-sm">Sin mensajes recientes</p>
                </div>
              ) : (
                log.map(msg => {
                  const intentMeta = INTENT_META[msg.intent]
                  const IntentIcon = intentMeta.icon
                  return (
                    <div key={msg.id} className="space-y-2">
                      {/* Mensaje usuario */}
                      <div className="flex justify-end">
                        <div className="max-w-[78%] bg-sky-500 text-white rounded-2xl rounded-tr-sm px-3 py-2">
                          <div className="flex items-center gap-1.5 mb-1">
                            <User size={11} className="opacity-70" />
                            <span className="text-xs opacity-80">{msg.sender}</span>
                            <span className="text-xs opacity-50 ml-auto">{msg.ts}</span>
                          </div>
                          <p className="text-sm">{msg.message}</p>
                        </div>
                      </div>
                      {/* Respuesta bot */}
                      <div className="flex justify-start gap-2">
                        <div className="w-7 h-7 rounded-full bg-sky-100 border border-sky-200 flex items-center justify-center flex-shrink-0 mt-1">
                          <Bot size={13} className="text-sky-600" />
                        </div>
                        <div className="max-w-[78%] bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-3 py-2 shadow-sm">
                          <div className="flex items-center gap-1.5 mb-1.5">
                            <span className="text-xs font-medium text-sky-600">HERMES</span>
                            <span className={`flex items-center gap-1 text-xs px-1.5 py-0.5 rounded-full ${intentMeta.color}`}>
                              <IntentIcon size={9} />
                              {intentMeta.label}
                            </span>
                          </div>
                          <p className="text-sm text-sovereign-text whitespace-pre-line">{msg.response}</p>
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
            </div>

            {/* Footer nota */}
            <div className="px-4 py-3 border-t border-gray-100 bg-white">
              <p className="text-xs text-sovereign-muted text-center">
                Historial de sesión actual · Los mensajes reales se gestionan en Telegram
              </p>
            </div>
          </div>

          {/* Info técnica */}
          <Card className="p-4 mt-4">
            <h2 className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider mb-3">Configuración técnica</h2>
            <div className="space-y-2">
              {[
                ['Framework',     'python-telegram-bot v21'],
                ['Brain IA',      'Integrado vía /api/brain/ask · RAG Qdrant'],
                ['Autenticación', 'JWT por sesión (en memoria)'],
                ['Modo',          'Polling (webhook eliminado)'],
                ['Sesiones',      '"telegram:{user_id}"'],
                ['Dedup',         'Redis TTL 30s (fix Evolution #1858)'],
              ].map(([label, val]) => (
                <div key={label} className="flex justify-between py-1 border-b border-gray-50 last:border-0">
                  <span className="text-xs text-sovereign-muted">{label}</span>
                  <span className="text-xs font-medium text-sovereign-text">{val}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
