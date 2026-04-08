'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Stat } from './Stat'
import { DashboardCard } from './Card'
import { Table } from './Table'
import { Alert } from './Alert'
import { Button } from './Button'
import clsx from 'clsx'

interface TenantInfo {
  id: string
  business_name: string
  niche: string
  joined_at: string
  plan: 'starter' | 'pro' | 'enterprise'
  usuarios_totales: number
}

interface Document {
  id: string
  nombre: string
  tipo: 'pdf' | 'imagen' | 'texto'
  tamaño_kb: number
  vectores: number
  fecha: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tokens?: number
}

interface APIKey {
  id: string
  nombre: string
  creado: string
  ultimo_uso: string
  activo: boolean
}

interface UsageStats {
  mensajes_hoy: number
  documentos_seeded: number
  búsquedas_rag: number
  vectores_totales: number
  plan_límite: number
}

export function ClientDashboard({ tenantId }: { tenantId: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tenantInfo, setTenantInfo] = useState<TenantInfo | null>(null)
  const [stats, setStats] = useState<UsageStats>({
    mensajes_hoy: 0,
    documentos_seeded: 0,
    búsquedas_rag: 0,
    vectores_totales: 0,
    plan_límite: 0,
  })
  const [documents, setDocuments] = useState<Document[]>([])
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [sendingChat, setSendingChat] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'settings'>('overview')

  useEffect(() => {
    loadTenantData()
  }, [tenantId])

  const loadTenantData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Simular llamadas a API (en producción traer datos reales vía /api/v1/tenants/{tenantId})
      const mockTenantInfo: TenantInfo = {
        id: tenantId,
        business_name: 'Restaurante La Paz',
        niche: 'restaurante',
        joined_at: '2025-08-15',
        plan: 'pro',
        usuarios_totales: 3,
      }

      const mockUsage: UsageStats = {
        mensajes_hoy: 47,
        documentos_seeded: 156,
        búsquedas_rag: 342,
        vectores_totales: 24_580,
        plan_límite: 100_000,
      }

      const mockDocs: Document[] = [
        { id: '1', nombre: 'Manual de Recetas 2025', tipo: 'pdf', tamaño_kb: 2_400, vectores: 1_200, fecha: '2025-03-01' },
        { id: '2', nombre: 'Estándares Sanitarios', tipo: 'pdf', tamaño_kb: 1_800, vectores: 900, fecha: '2025-02-15' },
        { id: '3', nombre: 'Protocolo de Atención', tipo: 'texto', tamaño_kb: 450, vectores: 225, fecha: '2025-02-20' },
        { id: '4', nombre: 'Menú Especial Trimestre', tipo: 'pdf', tamaño_kb: 3_100, vectores: 1_550, fecha: '2025-03-08' },
      ]

      const mockKeys: APIKey[] = [
        {
          id: 'key_1',
          nombre: 'Producción',
          creado: '2025-08-16',
          ultimo_uso: 'Hace 2 minutos',
          activo: true,
        },
        {
          id: 'key_2',
          nombre: 'Testing',
          creado: '2025-08-20',
          ultimo_uso: 'Ayer',
          activo: false,
        },
      ]

      setTenantInfo(mockTenantInfo)
      setStats(mockUsage)
      setDocuments(mockDocs)
      setApiKeys(mockKeys)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando datos del tenant')
    } finally {
      setLoading(false)
    }
  }

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return

    try {
      setSendingChat(true)
      const newMessage: ChatMessage = {
        role: 'user',
        content: chatMessage,
        timestamp: new Date().toISOString(),
      }
      setChatHistory((prev) => [...prev, newMessage])
      setChatMessage('')

      // Simular respuesta IA (en producción: POST /api/v1/agents/hermes/chat)
      setTimeout(() => {
        const response: ChatMessage = {
          role: 'assistant',
          content: `He procesado tu consulta: "${chatMessage}". En producción, esto conectaría a HERMES con RAG en Qdrant para tu nicho (${tenantInfo?.niche}).`,
          timestamp: new Date().toISOString(),
          tokens: Math.floor(Math.random() * 200) + 50,
        }
        setChatHistory((prev) => [...prev, response])
      }, 600)
    } finally {
      setSendingChat(false)
    }
  }

  const deleteDocument = (docId: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== docId))
  }

  const regenerateKey = (keyId: string) => {
    // Simular regeneración
    console.log('Regenerando key:', keyId)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-sovereign-bg p-4 sm:p-8">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-sovereign-muted">Cargando datos del negocio...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-sovereign-bg p-4 sm:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-sovereign-text mb-2">
            {tenantInfo?.business_name}
          </h1>
          <div className="flex items-center gap-4 text-sm text-sovereign-muted">
            <span>📍 {tenantInfo?.niche}</span>
            <span>📅 Cliente desde {tenantInfo?.joined_at}</span>
            <span className="px-2 py-1 bg-sovereign-gold/10 text-sovereign-gold rounded">
              Plan {tenantInfo?.plan}
            </span>
          </div>
        </div>

        {/* Errores */}
        {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Stat
            label="Mensajes Hoy"
            value={stats.mensajes_hoy}
            sub="en HERMES"
            color="blue"
            icon="💬"
          />
          <Stat
            label="Docs Seeded"
            value={stats.documentos_seeded}
            sub="en tu RAG"
            color="green"
            icon="📄"
          />
          <Stat
            label="Búsquedas RAG"
            value={stats.búsquedas_rag}
            sub="este mes"
            color="gold"
            icon="🔍"
          />
          <Stat
            label="Vectores"
            value={`${(stats.vectores_totales / 1000).toFixed(1)}K / ${(stats.plan_límite / 1000).toFixed(0)}K`}
            sub={`${((stats.vectores_totales / stats.plan_límite) * 100).toFixed(0)}% usado`}
            color="gray"
            icon="⚡"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Chat HERMES */}
          <div className="lg:col-span-2">
            <DashboardCard title="Chat HERMES — Asistente IA">
              <div className="space-y-4">
                <div className="bg-sovereign-bg rounded-lg p-4 h-80 overflow-y-auto space-y-3 border border-sovereign-border/40">
                  {chatHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-center">
                      <div>
                        <p className="text-2xl mb-2">💭</p>
                        <p className="text-sovereign-muted text-sm">Pregunta algo sobre tu negocio...</p>
                        <p className="text-xs text-sovereign-muted/60 mt-2">
                          Acceso a {stats.documentos_seeded} documentos seeded
                        </p>
                      </div>
                    </div>
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
                        <p className="text-sm leading-relaxed">{msg.content}</p>
                        {msg.tokens && (
                          <p className="text-xs text-sovereign-muted/60 mt-1">{msg.tokens} tokens</p>
                        )}
                      </div>
                    ))
                  )}
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                    placeholder="Escribe tu pregunta..."
                    disabled={sendingChat}
                    className="flex-1 px-4 py-2 rounded-lg bg-sovereign-border/10 border border-sovereign-border text-sovereign-text placeholder-sovereign-muted focus:outline-none focus:border-sovereign-gold/50 disabled:opacity-50"
                  />
                  <Button
                    onClick={sendChatMessage}
                    loading={sendingChat}
                    size="md"
                    className="w-24"
                  >
                    Enviar
                  </Button>
                </div>
              </div>
            </DashboardCard>
          </div>

          {/* Sidebar — Quick Actions */}
          <div className="space-y-4">
            <DashboardCard title="Acciones Rápidas">
              <div className="space-y-2">
                <Button variant="secondary" size="sm" className="w-full">
                  📤 Subir Documento
                </Button>
                <Button variant="secondary" size="sm" className="w-full">
                  🔑 Gestionar API Keys
                </Button>
                <Button variant="secondary" size="sm" className="w-full">
                  ⚙️ Configuración
                </Button>
                <Button variant="secondary" size="sm" className="w-full">
                  📊 Ver Historial
                </Button>
              </div>
            </DashboardCard>

            <DashboardCard title="Plan Actual" badge={{ label: 'Pro', color: 'blue' }}>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-sovereign-muted">Documentos/mes</span>
                  <span className="font-bold text-sovereign-text">Ilimitado</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sovereign-muted">Búsquedas RAG</span>
                  <span className="font-bold text-sovereign-text">Ilimitadas</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sovereign-muted">Vectores</span>
                  <span className="font-bold text-green-400">100K</span>
                </div>
                <hr className="border-sovereign-border/40 my-2" />
                <Button variant="ghost" size="sm" className="w-full text-xs">
                  Ver otros planes
                </Button>
              </div>
            </DashboardCard>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-4 border-b border-sovereign-border">
          <div className="flex gap-6">
            {(['overview', 'documents', 'settings'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={clsx(
                  'pb-3 px-2 font-medium text-sm transition-colors border-b-2 -mb-[1px]',
                  activeTab === tab
                    ? 'text-sovereign-gold border-sovereign-gold'
                    : 'text-sovereign-muted border-transparent hover:text-sovereign-text'
                )}
              >
                {tab === 'overview' && '📊 Overview'}
                {tab === 'documents' && '📁 Documentos'}
                {tab === 'settings' && '⚙️ Configuración'}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'documents' && (
          <DashboardCard title="Librería de Documentos">
            <Table
              columns={[
                { key: 'nombre', label: 'Nombre' },
                { key: 'tipo', label: 'Tipo' },
                { key: 'tamaño', label: 'Tamaño' },
                { key: 'vectores', label: 'Vectores' },
                { key: 'fecha', label: 'Fecha' },
                { key: 'acciones', label: 'Acciones' },
              ]}
              rows={documents.map((doc) => ({
                nombre: doc.nombre,
                tipo: (
                  <span className="inline-block px-2 py-1 bg-sovereign-border/40 rounded text-xs">
                    {doc.tipo}
                  </span>
                ),
                tamaño: `${(doc.tamaño_kb / 1024).toFixed(1)} MB`,
                vectores: doc.vectores.toLocaleString('es-MX'),
                fecha: doc.fecha,
                acciones: (
                  <div className="flex gap-2">
                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="text-red-400 hover:text-red-500 text-xs font-bold"
                    >
                      🗑️ Borrar
                    </button>
                  </div>
                ),
              }))}
              empty="No hay documentos. Sube uno para comenzar."
            />
          </DashboardCard>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <DashboardCard title="API Keys">
              <Table
                columns={[
                  { key: 'nombre', label: 'Nombre' },
                  { key: 'creado', label: 'Creado' },
                  { key: 'ultimo', label: 'Último Uso' },
                  { key: 'estado', label: 'Estado' },
                  { key: 'acciones', label: 'Acciones' },
                ]}
                rows={apiKeys.map((key) => ({
                  nombre: key.nombre,
                  creado: key.creado,
                  ultimo: key.ultimo_uso,
                  estado: (
                    <span
                      className={clsx(
                        'inline-block px-2 py-0.5 rounded-full text-xs font-bold',
                        key.activo
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-gray-100 text-gray-600'
                      )}
                    >
                      {key.activo ? 'Activa' : 'Inactiva'}
                    </span>
                  ),
                  acciones: (
                    <div className="flex gap-2">
                      <button
                        onClick={() => regenerateKey(key.id)}
                        className="text-blue-400 hover:text-blue-500 text-xs font-bold"
                      >
                        🔄 Regenerar
                      </button>
                    </div>
                  ),
                }))}
              />
            </DashboardCard>

            <DashboardCard title="Peligro — Zona Roja">
              <div className="p-4 bg-red-50/50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800 font-bold mb-3">Acciones irreversibles</p>
                <Button variant="danger" size="sm" className="w-full">
                  🗑️ Eliminar Todos los Datos del Tenant
                </Button>
              </div>
            </DashboardCard>
          </div>
        )}
      </div>
    </div>
  )
}
