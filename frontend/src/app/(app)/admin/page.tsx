'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import AuthGuard from '@/components/layout/AuthGuard'
import { Building2, Users, FileText, TrendingUp, Settings, CheckCircle, XCircle } from 'lucide-react'

const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

const PLANES = ['basico', 'business', 'pro', 'magia']
const PLAN_COLORS: Record<string, string> = {
  basico: 'bg-gray-100 text-gray-700',
  business: 'bg-blue-100 text-blue-700',
  pro: 'bg-purple-100 text-purple-700',
  magia: 'bg-amber-100 text-amber-700',
}

interface TenantAdmin {
  id: string
  nombre: string
  rfc: string
  plan: string
  activo: boolean
  usuarios: number
  facturas: number
  ingresos_total: number
  created_at: string
}

export default function AdminPage() {
  const [tenants, setTenants] = useState<TenantAdmin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updatingPlan, setUpdatingPlan] = useState<string | null>(null)

  async function cargar() {
    setLoading(true); setError('')
    try {
      const data = await api.get<TenantAdmin[]>('/admin/tenants')
      setTenants(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Sin acceso. Solo admin/CEO.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, [])

  async function cambiarPlan(tenantId: string, plan: string) {
    setUpdatingPlan(tenantId)
    try {
      await api.patch(`/admin/tenants/${tenantId}/plan`, { plan })
      setTenants(prev => prev.map(t => t.id === tenantId ? { ...t, plan } : t))
    } catch (e: unknown) {
      alert(`Error: ${e instanceof Error ? e.message : 'Error'}`)
    } finally {
      setUpdatingPlan(null)
    }
  }

  const totalIngresos = tenants.reduce((s, t) => s + t.ingresos_total, 0)
  const totalFacturas = tenants.reduce((s, t) => s + t.facturas, 0)
  const totalUsuarios = tenants.reduce((s, t) => s + t.usuarios, 0)

  return (
    <AuthGuard allowedRoles={['admin', 'ceo']}>
      <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin — Multi-Tenant</h1>
        <p className="text-sm text-gray-500 mt-0.5">Gestión de clientes, planes y métricas globales</p>
      </div>

      {/* KPIs globales */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg"><Building2 size={20} className="text-blue-500" /></div>
            <div>
              <p className="text-xs text-gray-500">Clientes activos</p>
              <p className="text-xl font-bold text-gray-900">{tenants.length}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-50 rounded-lg"><TrendingUp size={20} className="text-green-500" /></div>
            <div>
              <p className="text-xs text-gray-500">Ingresos totales</p>
              <p className="text-xl font-bold text-gray-900">{mxn(totalIngresos)}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-50 rounded-lg"><FileText size={20} className="text-purple-500" /></div>
            <div>
              <p className="text-xs text-gray-500">Facturas totales</p>
              <p className="text-xl font-bold text-gray-900">{totalFacturas}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-50 rounded-lg"><Users size={20} className="text-amber-500" /></div>
            <div>
              <p className="text-xs text-gray-500">Usuarios totales</p>
              <p className="text-xl font-bold text-gray-900">{totalUsuarios}</p>
            </div>
          </div>
        </Card>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-gray-400 text-sm">
          <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          Cargando tenants...
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Tabla de tenants */}
      {tenants.length > 0 && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Cliente</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">RFC</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Plan</th>
                  <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Usuarios</th>
                  <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Facturas</th>
                  <th className="text-right text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Ingresos</th>
                  <th className="text-center text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Estado</th>
                  <th className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 py-3">Cambiar Plan</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map(t => (
                  <tr key={t.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-900">{t.nombre}</p>
                      <p className="text-xs text-gray-400">{t.id.slice(0, 8)}...</p>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 font-mono">{t.rfc}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${PLAN_COLORS[t.plan] || 'bg-gray-100 text-gray-700'}`}>
                        {t.plan}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-right text-gray-700">{t.usuarios}</td>
                    <td className="px-4 py-3 text-sm text-right text-gray-700">{t.facturas}</td>
                    <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">{mxn(t.ingresos_total)}</td>
                    <td className="px-4 py-3 text-center">
                      {t.activo
                        ? <CheckCircle size={16} className="text-green-500 mx-auto" />
                        : <XCircle size={16} className="text-red-400 mx-auto" />}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <select
                          value={t.plan}
                          onChange={e => cambiarPlan(t.id, e.target.value)}
                          disabled={updatingPlan === t.id}
                          className="text-xs border border-gray-200 rounded px-2 py-1 focus:outline-none disabled:opacity-50"
                        >
                          {PLANES.map(p => <option key={p} value={p}>{p}</option>)}
                        </select>
                        {updatingPlan === t.id && (
                          <div className="w-3 h-3 border border-brand-500 border-t-transparent rounded-full animate-spin" />
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* AI OS Status */}
      <AIStatusCard />
      </div>
    </AuthGuard>
  )
}

function AIStatusCard() {
  const [status, setStatus] = useState<{ agents: string[]; skills: string[]; tasks_executed: number } | null>(null)

  useEffect(() => {
    api.get<{ agents: string[]; skills: string[]; tasks_executed: number }>('/ai/status').then(setStatus).catch(() => null)
  }, [])

  if (!status) return null

  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <Settings size={18} className="text-brand-500" />
        <h2 className="text-sm font-semibold text-gray-700">AI OS — Orquestador</h2>
        <span className="ml-auto text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">Activo</span>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{status.agents.length}</p>
          <p className="text-xs text-gray-500 mt-1">Agentes</p>
          <div className="flex flex-wrap gap-1 mt-2 justify-center">
            {status.agents.map(a => (
              <span key={a} className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">{a.replace('_agent', '')}</span>
            ))}
          </div>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{status.skills.length}</p>
          <p className="text-xs text-gray-500 mt-1">Skills</p>
          <div className="flex flex-wrap gap-1 mt-2 justify-center">
            {status.skills.map(s => (
              <span key={s} className="text-xs bg-purple-50 text-purple-700 px-1.5 py-0.5 rounded">{s}</span>
            ))}
          </div>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-900">{status.tasks_executed}</p>
          <p className="text-xs text-gray-500 mt-1">Tareas ejecutadas</p>
        </div>
      </div>
    </Card>
  )
}
