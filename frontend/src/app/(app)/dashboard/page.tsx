'use client'

import { useEffect, useState } from 'react'
import { api, DashboardData } from '@/lib/api'
import { StatCard } from '@/components/ui/Card'
import { TrendingUp, TrendingDown, FileText, Users, DollarSign, Activity } from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts'

const fmt = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

// Sparkline data simulado para el chart (en producción vendría del cierre)
const MONTHS = ['Oct','Nov','Dic','Ene','Feb','Mar']

export default function DashboardPage() {
  const [data, setData]     = useState<DashboardData | null>(null)
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<DashboardData>('/dashboard')
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-gray-400 text-sm">Cargando...</p>
  if (error)   return <p className="text-red-500 text-sm">Error: {error}</p>
  if (!data)   return null

  const utilidadPositiva = data.utilidad_neta >= 0
  const chartData = MONTHS.map((m, i) => ({
    mes: m,
    ingresos: data.ingresos_mes * (0.7 + i * 0.06),
    egresos:  data.egresos_mes  * (0.8 + i * 0.04),
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">{data.mes_actual}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <StatCard
          label="Ingresos del mes"
          value={fmt(data.ingresos_mes)}
          color="green"
          icon={<TrendingUp size={24} />}
        />
        <StatCard
          label="Egresos del mes"
          value={fmt(data.egresos_mes)}
          color="red"
          icon={<TrendingDown size={24} />}
        />
        <StatCard
          label="Utilidad neta"
          value={fmt(data.utilidad_neta)}
          color={utilidadPositiva ? 'green' : 'red'}
          icon={<Activity size={24} />}
        />
        <StatCard
          label="Tipo de cambio"
          value={`$${data.tipo_cambio?.toFixed(2) ?? '—'}`}
          sub="USD/MXN"
          color="blue"
          icon={<DollarSign size={24} />}
        />
        <StatCard
          label="Facturas pendientes"
          value={String(data.facturas_pendientes)}
          color={data.facturas_pendientes > 0 ? 'red' : 'green'}
          icon={<FileText size={24} />}
        />
        <StatCard
          label="Empleados activos"
          value={String(data.total_empleados)}
          color="gray"
          icon={<Users size={24} />}
        />
      </div>

      {/* Chart */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Tendencia 6 meses</h2>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="ing" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#10b981" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="eg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v: number) => fmt(v)} />
            <Area type="monotone" dataKey="ingresos" stroke="#10b981" fill="url(#ing)" strokeWidth={2} name="Ingresos" />
            <Area type="monotone" dataKey="egresos"  stroke="#ef4444" fill="url(#eg)"  strokeWidth={2} name="Egresos" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
