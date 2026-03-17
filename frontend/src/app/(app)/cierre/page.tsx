'use client'

import { useEffect, useState } from 'react'
import { api, CierreData } from '@/lib/api'
import { Card, StatCard } from '@/components/ui/Card'

const fmt = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

export default function CierrePage() {
  const now = new Date()
  const [ano, setAno]   = useState(now.getFullYear())
  const [mes, setMes]   = useState(now.getMonth() + 1)
  const [data, setData] = useState<CierreData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')
  const [guardando, setGuardando] = useState(false)
  const [guardadoMsg, setGuardadoMsg] = useState('')

  async function cargar() {
    setLoading(true)
    setError('')
    setData(null)
    try {
      const res = await api.get<CierreData>(`/cierre/${ano}/${mes}`)
      setData(res)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function guardar() {
    setGuardando(true)
    setGuardadoMsg('')
    try {
      await api.post(`/cierre/${ano}/${mes}/guardar`, {})
      setGuardadoMsg('✅ Cierre guardado correctamente')
    } catch (e: unknown) {
      setGuardadoMsg(`❌ ${e instanceof Error ? e.message : 'Error'}`)
    } finally {
      setGuardando(false)
    }
  }

  const MESES = ['', 'Enero','Febrero','Marzo','Abril','Mayo','Junio',
                 'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Cierre Mensual</h1>

      {/* Selector */}
      <Card className="p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <select
            value={mes}
            onChange={e => setMes(+e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none"
          >
            {MESES.slice(1).map((m, i) => (
              <option key={i+1} value={i+1}>{m}</option>
            ))}
          </select>
          <select
            value={ano}
            onChange={e => setAno(+e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none"
          >
            {[2024, 2025, 2026].map(a => <option key={a} value={a}>{a}</option>)}
          </select>
          <button
            onClick={cargar}
            className="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Calcular
          </button>
          {data && (
            <button
              onClick={guardar}
              disabled={guardando}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              {guardando ? 'Guardando...' : 'Guardar cierre'}
            </button>
          )}
          {guardadoMsg && <span className="text-sm">{guardadoMsg}</span>}
        </div>
      </Card>

      {loading && <p className="text-gray-400 text-sm">Calculando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      {data && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard label="Ingresos"        value={fmt(data.ingresos)}       color="green" />
            <StatCard label="Egresos"         value={fmt(data.egresos)}        color="red" />
            <StatCard label="Utilidad bruta"  value={fmt(data.utilidad_bruta)} color={data.utilidad_bruta >= 0 ? 'green' : 'red'} />
            <StatCard label="Utilidad neta"   value={fmt(data.utilidad_neta)}  color={data.utilidad_neta >= 0 ? 'green' : 'red'} />
            <StatCard label="ISR estimado"    value={fmt(data.isr_estimado)}   color="blue" sub="Art. 14 LISR" />
            <StatCard label="IVA a pagar"     value={fmt(data.iva_a_pagar)}    color="blue" sub="Régimen general" />
          </div>

          <Card className="p-5">
            <h2 className="font-semibold text-gray-800 mb-3">
              Resumen — {MESES[mes]} {ano}
            </h2>
            <div className="space-y-2 text-sm">
              <Row label="Total facturas"    value={String(data.total_facturas)} />
              <Row label="Total nómina"      value={fmt(data.total_nomina)} />
              <Row label="Margen bruto"
                value={data.ingresos > 0
                  ? `${((data.utilidad_bruta / data.ingresos) * 100).toFixed(1)}%`
                  : '—'}
              />
            </div>
          </Card>
        </>
      )}
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1.5 border-b border-gray-50 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  )
}
