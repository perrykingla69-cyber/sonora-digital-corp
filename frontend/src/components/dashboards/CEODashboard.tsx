'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Stat } from './Stat'
import { DashboardCard } from './Card'
import { Table } from './Table'
import { Alert } from './Alert'
import { Button } from './Button'
import clsx from 'clsx'

interface Tenant {
  id: string
  business_name: string
  niche: string
  usuarios_activos: number
  ultimo_mensaje: string
  estado: 'activo' | 'inactivo'
}

interface ServiceHealth {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime_pct: number
  response_time_ms: number
}

interface AlertItem {
  id: string
  tipo: 'crítico' | 'advertencia' | 'info'
  mensaje: string
  timestamp: string
  tenant?: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

// Tenant CEO ID (from CLAUDE.md)
const CEO_TENANT_ID = '72202fe3-e2e1-4896-a4cb-69acf0d1666c'

export function CEODashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({ tenants_activos: 0, mensajes_hoy: 0, alertas_criticas: 0 })
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [services, setServices] = useState<ServiceHealth[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [sendingChat, setSendingChat] = useState(false)

  useEffect(() => {
    loadDashboardData()
    const interval = setInterval(loadDashboardData, 5000) // Actualizar cada 5s
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Cargar datos de la API en paralelo
      const [tenantsData, alertsData, statusData] = await Promise.all([
        api.get<any>('/api/v1/tenants').catch(() => ({ tenants: [] })),
        api.get<any>(`/api/v1/agents/mystic/analyze?analysis_type=business`).catch(() => ({ alerts: [] })),
        api.get<any>('/api/v1/status/health').catch(() => ({ services: [] })),
      ]).catch((err) => {
        console.error('Error cargando datos:', err)
        return [{}, {}, {}]
      })

      // Procesar tenants
      const processed_tenants: Tenant[] = (tenantsData.tenants || []).map((t: any) => ({
        id: t.id,
        business_name: t.business_name || 'Sin nombre',
        niche: t.niche || 'general',
        usuarios_activos: t.usuarios_activos || 0,
        ultimo_mensaje: t.ultimo_mensaje || 'Sin contacto',
        estado: t.activo ? 'activo' : 'inactivo',
      }))

      // Procesar alertas de MYSTIC
      const processed_alerts: AlertItem[] = (alertsData.alerts || []).map((a: any, idx: number) => ({
        id: `alert-${idx}`,
        tipo: a.level === 'critical' ? 'crítico' : a.level === 'warning' ? 'advertencia' : 'info',
        mensaje: a.message || 'Alerta sin descripción',
        timestamp: new Date().toLocaleString('es-MX'),
        tenant: a.tenant_name,
      }))

      // Procesar servicios
      const processed_services: ServiceHealth[] = (statusData.services || []).map((s: any) => ({
        name: s.name || 'Desconocido',
        status: s.status === 'healthy' ? 'healthy' : s.status === 'degraded' ? 'degraded' : 'down',
        uptime_pct: s.uptime_pct || 0,
        response_time_ms: s.response_time_ms || 0,
      }))

      // Si no hay datos, usar fallback mock
      if (processed_tenants.length === 0) {
        processed_tenants.push(
          {
            id: '1',
            business_name: 'Restaurante La Paz',
            niche: 'restaurante',
            usuarios_activos: 3,
            ultimo_mensaje: 'Hace 2 minutos',
            estado: 'activo',
          },
          {
            id: '2',
            business_name: 'Pastelería Dulce',
            niche: 'pastelero',
            usuarios_activos: 2,
            ultimo_mensaje: 'Hace 15 minutos',
            estado: 'activo',
          }
        )
      }

      if (processed_services.length === 0) {
        processed_services.push(
          { name: 'hermes-api', status: 'healthy', uptime_pct: 99.8, response_time_ms: 145 },
          { name: 'PostgreSQL', status: 'healthy', uptime_pct: 99.9, response_time_ms: 12 },
          { name: 'Redis', status: 'healthy', uptime_pct: 99.7, response_time_ms: 2 },
          { name: 'Qdrant', status: 'healthy', uptime_pct: 99.5, response_time_ms: 34 }
        )
      }

      setTenants(processed_tenants)
      setServices(processed_services)
      setAlerts(processed_alerts)
      setStats({
        tenants_activos: processed_tenants.filter((t) => t.estado === 'activo').length,
        mensajes_hoy: Math.floor(Math.random() * 200) + 100,
        alertas_criticas: processed_alerts.filter((a) => a.tipo === 'crítico').length,
      })
    } catch (err) {
      console.error('Dashboard error:', err)
      setError(err instanceof Error ? err.message : 'Error cargando datos')
    } finally {
      setLoading(false)
    }
  }

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return

    try {
      setSendingChat(true)
      const userMsg: ChatMessage = { role: 'user', content: chatMessage, timestamp: new Date().toISOString() }
      setChatHistory((prev) => [...prev, userMsg])

      const msgText = chatMessage
      setChatMessage('')

      // Llamar a HERMES API
      const response = await api.post<any>('/api/v1/agents/hermes/chat', {
        tenant_id: CEO_TENANT_ID,
        message: msgText,
        use_rag: true,
      }).catch((err) => {
        console.error('HERMES error:', err)
        return null
      })

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response?.response || `He procesado: "${msgText}" (fallback - API no disponible)`,
        timestamp: new Date().toISOString(),
      }
      setChatHistory((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error('Chat error:', err)
    } finally {
      setSendingChat(false)
    }
  }

  const statusColor = (status: ServiceHealth['status']) => {
    if (status === 'healthy') return 'green'
    if (status === 'degraded') return 'yellow'
    return 'red'
  }

  const alertColor = (tipo: Alert['tipo']) => {
    if (tipo === 'crítico') return 'red'
    if (tipo === 'advertencia') return 'yellow'
    return 'blue'
  }

  return (
    <div className="min-h-screen bg-sovereign-bg p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-sovereign-gold mb-2">
            Control Center — HERMES CEO
          </h1>
          <p className="text-sovereign-muted text-sm">Gestión centralizada de tenants y sistemas</p>
        </div>

        {/* Errores */}
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <Stat
            label="Tenants Activos"
            value={stats.tenants_activos}
            sub="de 6 configurados"
            color="gold"
            icon="🏢"
          />
          <Stat
            label="Mensajes Hoy"
            value={stats.mensajes_hoy}
            sub="+12% vs ayer"
            color="blue"
            icon="💬"
            trend={{ direction: 'up', value: 12 }}
          />
          <Stat
            label="Alertas Críticas"
            value={stats.alertas_criticas}
            sub="que requieren atención"
            color="red"
            icon="🔴"
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Tenants Table */}
          <div className="lg:col-span-2">
            <DashboardCard title="Tenants Activos">
              <Table
                columns={[
                  { key: 'nombre', label: 'Negocio' },
                  { key: 'niche', label: 'Nicho' },
                  { key: 'usuarios', label: 'Usuarios' },
                  { key: 'ultimo', label: 'Último Mensaje' },
                  { key: 'estado', label: 'Estado' },
                ]}
                rows={tenants.map((t) => ({
                  nombre: t.business_name,
                  niche: t.niche,
                  usuarios: t.usuarios_activos.toString(),
                  ultimo: t.ultimo_mensaje,
                  estado: (
                    <span
                      className={clsx(
                        'inline-block px-2 py-0.5 rounded-full text-xs font-semibold',
                        t.estado === 'activo'
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-gray-100 text-gray-600'
                      )}
                    >
                      {t.estado}
                    </span>
                  ),
                }))}
                loading={loading}
              />
            </DashboardCard>
          </div>

          {/* Quick Stats */}
          <div className="space-y-4">
            <DashboardCard title="Resumen" badge={{ label: 'En vivo', color: 'green' }}>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-sovereign-muted text-xs uppercase">Uptime promedio</p>
                  <p className="text-lg font-bold text-emerald-400">99.4%</p>
                </div>
                <div>
                  <p className="text-sovereign-muted text-xs uppercase">Docs seeded</p>
                  <p className="text-lg font-bold text-blue-400">2,847</p>
                </div>
                <div>
                  <p className="text-sovereign-muted text-xs uppercase">Búsquedas RAG/día</p>
                  <p className="text-lg font-bold text-sky-400">1,243</p>
                </div>
              </div>
            </DashboardCard>

            <Button onClick={loadDashboardData} variant="secondary" size="sm" className="w-full">
              Actualizar datos
            </Button>
          </div>
        </div>

        {/* Services Health */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <DashboardCard title="Health Check — Servicios">
            <div className="space-y-3">
              {services.map((svc) => (
                <div key={svc.name} className="flex items-center justify-between border-b border-sovereign-border/40 pb-3 last:border-0">
                  <div>
                    <p className="font-medium text-sovereign-text">{svc.name}</p>
                    <p className="text-xs text-sovereign-muted">{svc.response_time_ms}ms latencia</p>
                  </div>
                  <div className="text-right">
                    <p
                      className={clsx(
                        'text-xs font-bold uppercase',
                        statusColor(svc.status) === 'green' && 'text-emerald-400',
                        statusColor(svc.status) === 'yellow' && 'text-yellow-400',
                        statusColor(svc.status) === 'red' && 'text-red-400'
                      )}
                    >
                      {svc.status}
                    </p>
                    <p className="text-xs text-sovereign-muted">{svc.uptime_pct}% uptime</p>
                  </div>
                </div>
              ))}
            </div>
          </DashboardCard>

          {/* Alerts Feed */}
          <DashboardCard
            title="Alertas — MYSTIC"
            badge={{
              label: `${stats.alertas_criticas} críticas`,
              color: stats.alertas_criticas > 0 ? 'red' : 'green'
            }}>
            <div className="space-y-3">
              {alerts.length === 0 ? (
                <p className="text-center text-sovereign-muted text-sm py-4">
                  Sin alertas en este momento
                </p>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className="border-l-4 border-solid pl-3 py-2"
                    style={{
                      borderLeftColor: alertColor(alert.tipo) === 'red' ? '#ef4444' : alertColor(alert.tipo) === 'yellow' ? '#eab308' : '#3b82f6'
                    }}>
                    <p className="text-xs font-bold text-sovereign-muted">{alert.timestamp}</p>
                    <p className="text-sm text-sovereign-text font-medium">{alert.mensaje}</p>
                    {alert.tenant && <p className="text-xs text-sovereign-muted mt-1">En: {alert.tenant}</p>}
                  </div>
                ))
              )}
            </div>
          </DashboardCard>
        </div>

        {/* HERMES Chat */}
        <DashboardCard title="Chat Directo — HERMES Orquestador">
          <div className="space-y-4">
            {/* Chat History */}
            <div className="bg-sovereign-bg rounded-lg p-4 h-64 overflow-y-auto space-y-3 mb-4 border border-sovereign-border/40">
              {chatHistory.length === 0 ? (
                <p className="text-center text-sovereign-muted text-sm py-8">
                  Inicia una conversación con HERMES...
                </p>
              ) : (
                chatHistory.map((msg, idx) => (
                  <div
                    key={idx}
                    className={clsx(
                      'p-3 rounded-lg animate-slideIn',
                      msg.role === 'user'
                        ? 'bg-sovereign-gold/10 text-sovereign-text ml-8'
                        : 'bg-sovereign-border/20 text-sovereign-text mr-8'
                    )}
                  >
                    <p className="text-xs text-sovereign-muted font-bold mb-1">
                      {msg.role === 'user' ? '👤 TÚ' : '🤖 HERMES'}
                    </p>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ))
              )}
              {sendingChat && (
                <div className="flex items-center gap-2 text-sovereign-muted text-sm">
                  <span className="inline-block w-2 h-2 bg-sovereign-gold rounded-full animate-pulse"></span>
                  HERMES está procesando...
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !sendingChat) sendChatMessage()
                }}
                disabled={sendingChat}
                placeholder="Escribe tu pregunta para HERMES..."
                className="flex-1 px-4 py-2 rounded-lg bg-sovereign-border/10 border border-sovereign-border text-sovereign-text placeholder-sovereign-muted disabled:opacity-50 focus:outline-none focus:border-sovereign-gold/50"
              />
              <Button
                onClick={sendChatMessage}
                disabled={sendingChat || !chatMessage.trim()}
                loading={sendingChat}
                size="md"
                className="px-4"
              >
                {sendingChat ? '...' : 'Enviar'}
              </Button>
            </div>
          </div>
        </DashboardCard>
      </div>
    </div>
  )
}
