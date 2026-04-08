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

interface Alert {
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

export function CEODashboard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({ tenants_activos: 6, mensajes_hoy: 142, alertas_criticas: 3 })
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [services, setServices] = useState<ServiceHealth[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [sendingChat, setSendingChat] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Simular llamadas a API (en producción traer datos reales)
      const mockTenants: Tenant[] = [
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
        },
        {
          id: '3',
          business_name: 'Contadores Asociados',
          niche: 'contador',
          usuarios_activos: 5,
          ultimo_mensaje: 'Hace 1 hora',
          estado: 'activo',
        },
        {
          id: '4',
          business_name: 'Bufete Legal',
          niche: 'abogado',
          usuarios_activos: 4,
          ultimo_mensaje: 'Hace 3 horas',
          estado: 'activo',
        },
        {
          id: '5',
          business_name: 'Plomería Rápida',
          niche: 'fontanero',
          usuarios_activos: 1,
          ultimo_mensaje: 'Ayer',
          estado: 'inactivo',
        },
        {
          id: '6',
          business_name: 'Consultoría Tech',
          niche: 'consultor',
          usuarios_activos: 6,
          ultimo_mensaje: 'Hace 30 minutos',
          estado: 'activo',
        },
      ]

      const mockServices: ServiceHealth[] = [
        { name: 'hermes-api', status: 'healthy', uptime_pct: 99.8, response_time_ms: 145 },
        { name: 'PostgreSQL', status: 'healthy', uptime_pct: 99.9, response_time_ms: 12 },
        { name: 'Redis', status: 'healthy', uptime_pct: 99.7, response_time_ms: 2 },
        { name: 'Qdrant', status: 'healthy', uptime_pct: 99.5, response_time_ms: 34 },
        { name: 'Evolution API', status: 'degraded', uptime_pct: 98.2, response_time_ms: 520 },
        { name: 'Ollama', status: 'healthy', uptime_pct: 99.1, response_time_ms: 1200 },
      ]

      const mockAlerts: Alert[] = [
        {
          id: '1',
          tipo: 'crítico',
          mensaje: 'Evolution API con latencia alta',
          timestamp: 'Hace 5 minutos',
          tenant: 'Restaurante La Paz',
        },
        {
          id: '2',
          tipo: 'crítico',
          mensaje: 'Cuota de vectores Qdrant 85% utilizada',
          timestamp: 'Hace 1 hora',
          tenant: undefined,
        },
        {
          id: '3',
          tipo: 'advertencia',
          mensaje: 'Plomería Rápida sin actividad por 24 horas',
          timestamp: 'Ayer',
          tenant: 'Plomería Rápida',
        },
      ]

      setTenants(mockTenants)
      setServices(mockServices)
      setAlerts(mockAlerts)
      setStats({
        tenants_activos: mockTenants.filter((t) => t.estado === 'activo').length,
        mensajes_hoy: Math.floor(Math.random() * 200) + 100,
        alertas_criticas: mockAlerts.filter((a) => a.tipo === 'crítico').length,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando datos')
    } finally {
      setLoading(false)
    }
  }

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return

    try {
      setSendingChat(true)
      const newMessage: ChatMessage = { role: 'user', content: chatMessage, timestamp: new Date().toISOString() }
      setChatHistory((prev) => [...prev, newMessage])
      setChatMessage('')

      // Simular respuesta IA (en producción llamar a /api/v1/agents/hermes/chat)
      setTimeout(() => {
        const response: ChatMessage = {
          role: 'assistant',
          content: `He procesado tu solicitud: "${chatMessage}". En producción, esto conectaría al orquestador HERMES via OpenRouter.`,
          timestamp: new Date().toISOString(),
        }
        setChatHistory((prev) => [...prev, response])
      }, 500)
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
          <DashboardCard title="Alertas — MYSTIC" badge={{ label: '3 críticas', color: 'red' }}>
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div key={alert.id} className="border-l-4 border-solid pl-3 py-2"
                  style={{
                    borderLeftColor: alertColor(alert.tipo) === 'red' ? '#ef4444' : alertColor(alert.tipo) === 'yellow' ? '#eab308' : '#3b82f6'
                  }}>
                  <p className="text-xs font-bold text-sovereign-muted">{alert.timestamp}</p>
                  <p className="text-sm text-sovereign-text font-medium">{alert.mensaje}</p>
                  {alert.tenant && <p className="text-xs text-sovereign-muted mt-1">En: {alert.tenant}</p>}
                </div>
              ))}
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
                      'p-3 rounded-lg',
                      msg.role === 'user'
                        ? 'bg-sovereign-gold/10 text-sovereign-text ml-8'
                        : 'bg-sovereign-border/20 text-sovereign-text mr-8'
                    )}
                  >
                    <p className="text-xs text-sovereign-muted font-bold mb-1">
                      {msg.role === 'user' ? 'TÚ' : 'HERMES'}
                    </p>
                    <p className="text-sm">{msg.content}</p>
                  </div>
                ))
              )}
            </div>

            {/* Chat Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Escribe tu pregunta..."
                className="flex-1 px-4 py-2 rounded-lg bg-sovereign-border/10 border border-sovereign-border text-sovereign-text placeholder-sovereign-muted focus:outline-none focus:border-sovereign-gold/50"
              />
              <Button
                onClick={sendChatMessage}
                loading={sendingChat}
                size="md"
                className="w-20"
              >
                Enviar
              </Button>
            </div>
          </div>
        </DashboardCard>
      </div>
    </div>
  )
}
