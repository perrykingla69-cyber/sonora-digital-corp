'use client'

import { useEffect, useState, useCallback, type ElementType } from 'react'
import { api, StatusData } from '@/lib/api'
import {
  Brain, Bot, MessageSquare, Database, Zap,
  CheckCircle, XCircle, Clock, RefreshCw,
  ShoppingCart, Activity, AlertTriangle, Cpu,
} from 'lucide-react'

interface AgentDef {
  id: string
  name: string
  subtitle: string
  icon: ElementType
  color: string
  bgColor: string
  statusKey: keyof StatusData | null
  role: string
  capabilities: string[]
}

const AGENTS: AgentDef[] = [
  {
    id: 'hermes',
    name: 'HERMES',
    subtitle: 'Orquestador principal',
    icon: Brain,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50 border-amber-200',
    statusKey: 'api',
    role: 'Responde consultas fiscales, orquesta agentes, coordina RAG',
    capabilities: ['RAG 4 capas', 'Gemini Flash', 'Multi-tenant', 'Caché Redis'],
  },
  {
    id: 'mystic',
    name: 'MYSTIC',
    subtitle: 'Shadow analyst',
    icon: Activity,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
    statusKey: null,
    role: 'Scan horario del sistema, alertas al CEO, análisis silencioso',
    capabilities: ['GLM Z1 Rumination', 'Alertas 🔴/🟡/🟢', 'Scan horario', 'Telegram CEO'],
  },
  {
    id: 'clawbot',
    name: 'ClawBot',
    subtitle: 'Gateway multi-canal',
    icon: MessageSquare,
    color: 'text-sky-600',
    bgColor: 'bg-sky-50 border-sky-200',
    statusKey: null,
    role: 'Router Telegram (4 bots) + WhatsApp Evolution API. Dedup Redis TTL 30s',
    capabilities: ['4 bots Telegram', 'WhatsApp Evolution', 'Dedup 30s', 'Onboarding auto'],
  },
  {
    id: 'autoseeder',
    name: 'AutoSeeder',
    subtitle: 'Seed Qdrant por nicho',
    icon: Database,
    color: 'text-green-700',
    bgColor: 'bg-green-50 border-green-200',
    statusKey: 'db',
    role: 'Seed automático Qdrant en onboarding. Clasifica nicho, embebe con nomic-embed-text',
    capabilities: ['nomic-embed-text', 'Qdrant híbrido', '9 nichos', 'Zero-touch'],
  },
  {
    id: 'supply',
    name: 'Supply Agent',
    subtitle: 'Inventario y compras',
    icon: ShoppingCart,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
    statusKey: null,
    role: 'Auto-reorden, predicción de demanda, optimización de stock (módulo futuro)',
    capabilities: ['Auto-reorden', 'Predicción demanda', 'Alertas stock', 'Órdenes de compra'],
  },
  {
    id: 'risk',
    name: 'Risk Agent',
    subtitle: 'Detección de riesgos',
    icon: AlertTriangle,
    color: 'text-red-600',
    bgColor: 'bg-red-50 border-red-200',
    statusKey: null,
    role: 'Detecta riesgos de stockout, monitorea proveedores, alerta sobre retrasos (módulo futuro)',
    capabilities: ['Stockout detection', 'Monitor proveedores', 'Alertas retraso', 'SAT compliance'],
  },
]

interface AgentStatus { online: boolean; latency?: number; lastCheck: string }

export default function AgentsPage() {
  const [sysStatus, setSysStatus] = useState<StatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({})
  const [activeAgent, setActiveAgent] = useState<string | null>(null)

  const fetchStatus = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    const start = Date.now()
    try {
      const s = await api.get<StatusData>('/status')
      const latency = Date.now() - start
      setSysStatus(s)

      const now = new Date().toLocaleTimeString()
      setAgentStatuses({
        hermes:     { online: s.api === 'ok', latency, lastCheck: now },
        autoseeder: { online: s.db === 'ok', lastCheck: now },
        mystic:     { online: s.api === 'ok', lastCheck: now },
        clawbot:    { online: s.api === 'ok', lastCheck: now },
        supply:     { online: false, lastCheck: now },
        risk:       { online: false, lastCheck: now },
      })
    } catch {
      const now = new Date().toLocaleTimeString()
      setAgentStatuses(prev => Object.fromEntries(
        AGENTS.map(a => [a.id, { online: false, lastCheck: now, ...(prev[a.id] || {}) }])
      ))
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => { fetchStatus() }, [fetchStatus])

  const onlineCount = Object.values(agentStatuses).filter(s => s.online).length
  const active = activeAgent ? AGENTS.find(a => a.id === activeAgent) : null

  return (
    <div className="space-y-6 max-w-5xl mx-auto">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-sovereign-text font-display">Agentes IA</h1>
          <p className="text-sm text-sovereign-muted mt-0.5">
            {loading ? 'Verificando estado...' : `${onlineCount} de ${AGENTS.length} agentes activos`}
          </p>
        </div>
        <button
          onClick={() => fetchStatus(true)}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 rounded-xl glass text-sm text-sovereign-muted hover:text-sovereign-text transition-colors"
        >
          <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
          Actualizar
        </button>
      </div>

      {/* Sistema status bar */}
      {sysStatus && (
        <div className="glass rounded-2xl p-4">
          <div className="flex items-center gap-6 flex-wrap">
            <span className="text-xs font-semibold text-sovereign-muted uppercase tracking-wider">Sistema</span>
            {[
              { label: 'API', val: sysStatus.api },
              { label: 'PostgreSQL', val: sysStatus.db },
              { label: 'Redis', val: sysStatus.redis },
            ].map(({ label, val }) => (
              <div key={label} className="flex items-center gap-1.5">
                <div className={`w-2 h-2 rounded-full ${val === 'ok' ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
                <span className="text-xs text-sovereign-muted">{label}</span>
                <span className={`text-xs font-semibold ${val === 'ok' ? 'text-emerald-600' : 'text-red-500'}`}>
                  {val === 'ok' ? 'OK' : 'ERROR'}
                </span>
              </div>
            ))}
            {agentStatuses.hermes?.latency && (
              <div className="ml-auto flex items-center gap-1.5">
                <Clock size={11} className="text-sovereign-muted" />
                <span className="text-xs text-sovereign-muted">Latencia API: {agentStatuses.hermes.latency}ms</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Orquestador destacado */}
      <div className="glass-gold rounded-2xl p-5">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-100 border border-amber-200 flex items-center justify-center flex-shrink-0">
            <Cpu size={22} className="text-amber-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h2 className="font-bold text-sovereign-text">Orquestador Central</h2>
              <span className={`badge-${agentStatuses.hermes?.online ? 'green' : 'red'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${agentStatuses.hermes?.online ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
                {agentStatuses.hermes?.online ? 'Activo' : 'Inactivo'}
              </span>
            </div>
            <p className="text-sm text-sovereign-muted">HERMES coordina todos los agentes, procesa RAG y atiende clientes 24/7</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-4">
          {[
            { label: 'Agentes activos', value: `${onlineCount}/${AGENTS.length}` },
            { label: 'Latencia API', value: agentStatuses.hermes?.latency ? `${agentStatuses.hermes.latency}ms` : '—' },
            { label: 'Modelo', value: 'Gemini Flash' },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white/60 rounded-xl p-3 text-center">
              <p className="text-xs text-sovereign-muted">{label}</p>
              <p className="font-bold text-sovereign-text mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Grid de agentes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {AGENTS.map(agent => {
          const status = agentStatuses[agent.id]
          const Icon = agent.icon
          const isActive = activeAgent === agent.id

          return (
            <button
              key={agent.id}
              onClick={() => setActiveAgent(isActive ? null : agent.id)}
              className={`text-left module-card rounded-2xl p-4 transition-all cursor-pointer ${
                isActive ? 'ring-2 ring-sovereign-gold' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${agent.bgColor}`}>
                  <Icon size={18} className={agent.color} />
                </div>
                <div className="flex items-center gap-1.5">
                  {loading ? (
                    <div className="w-2 h-2 rounded-full bg-gray-300 animate-pulse" />
                  ) : status?.online ? (
                    <CheckCircle size={14} className="text-emerald-500" />
                  ) : (
                    <XCircle size={14} className="text-red-400" />
                  )}
                  <span className={`text-xs font-medium ${
                    loading ? 'text-gray-400' : status?.online ? 'text-emerald-600' : 'text-red-400'
                  }`}>
                    {loading ? '...' : status?.online ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>

              <h3 className="font-bold text-sm text-sovereign-text">{agent.name}</h3>
              <p className="text-xs text-sovereign-muted mt-0.5">{agent.subtitle}</p>

              <div className="mt-3 flex flex-wrap gap-1">
                {agent.capabilities.slice(0, 2).map(cap => (
                  <span key={cap} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-sovereign-muted">
                    {cap}
                  </span>
                ))}
              </div>

              {status?.lastCheck && (
                <p className="text-xs text-sovereign-subtle mt-2">Verificado: {status.lastCheck}</p>
              )}
            </button>
          )
        })}
      </div>

      {/* Panel de detalle del agente seleccionado */}
      {active && (
        <div className="glass rounded-2xl p-5 animate-fade-up">
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${active.bgColor}`}>
              <active.icon size={18} className={active.color} />
            </div>
            <div>
              <h3 className="font-bold text-sovereign-text">{active.name}</h3>
              <p className="text-xs text-sovereign-muted">{active.subtitle}</p>
            </div>
          </div>

          <p className="text-sm text-sovereign-text mb-4">{active.role}</p>

          <div className="grid grid-cols-2 gap-2">
            {active.capabilities.map(cap => (
              <div key={cap} className="flex items-center gap-2 p-2 rounded-lg bg-white/60 border border-white/80">
                <Zap size={12} className="text-sovereign-gold flex-shrink-0" />
                <span className="text-xs text-sovereign-text">{cap}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Flujo de decisiones — visual */}
      <div className="glass rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-sovereign-text mb-4">Flujo de orquestación</h3>
        <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
          {[
            { label: 'Cliente', sub: 'Telegram / WhatsApp / Web', icon: MessageSquare, color: 'bg-sky-100 text-sky-600' },
            { label: 'ClawBot', sub: 'Gateway + dedup', icon: Bot, color: 'bg-sky-100 text-sky-600' },
            { label: 'HERMES', sub: 'Orquestador RAG', icon: Brain, color: 'bg-amber-100 text-amber-600' },
            { label: 'Agentes', sub: 'Supply / Risk / Finance', icon: Cpu, color: 'bg-purple-100 text-purple-600' },
            { label: 'MYSTIC', sub: 'Shadow · CEO alerts', icon: Activity, color: 'bg-purple-100 text-purple-600' },
          ].map((step, i, arr) => (
            <div key={step.label} className="flex items-center gap-2 flex-shrink-0">
              <div className="text-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center mx-auto ${step.color}`}>
                  <step.icon size={17} />
                </div>
                <p className="text-xs font-medium text-sovereign-text mt-1 whitespace-nowrap">{step.label}</p>
                <p className="text-xs text-sovereign-muted whitespace-nowrap">{step.sub}</p>
              </div>
              {i < arr.length - 1 && (
                <div className="h-0.5 w-8 bg-gradient-to-r from-sovereign-gold/40 to-sovereign-gold/20 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}
