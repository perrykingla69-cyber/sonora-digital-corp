'use client'

import { useEffect, useState } from 'react'
import { api, CierreCompleto } from '@/lib/api'
import { Card, StatCard } from '@/components/ui/Card'
import {
  TrendingUp, TrendingDown, Activity, Percent,
  BarChart2, FileText, DollarSign, Save, CheckCircle, Clock, AlertCircle,
} from 'lucide-react'

const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

type EstadoCierre = 'sin_registro' | 'borrador' | 'cerrado'

interface CierreEstado {
  estado: EstadoCierre
  periodo: string
  id?: string
  ingresos_total?: number
  egresos_total?: number
  utilidad_bruta?: number
  iva_neto?: number
  isr_estimado?: number
  created_at?: string
}

function Row({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`flex justify-between py-2 border-b border-gray-50 last:border-0 ${highlight ? 'font-semibold' : ''}`}>
      <span className="text-gray-500 text-sm">{label}</span>
      <span className={`text-sm ${highlight ? 'text-gray-900' : 'text-gray-700'}`}>{value}</span>
    </div>
  )
}

const ESTADO_CONFIG: Record<EstadoCierre, { label: string; color: string; icon: JSX.Element }> = {
  sin_registro: { label: 'Sin registro', color: 'text-gray-400 bg-gray-50', icon: <Clock size={14} /> },
  borrador:     { label: 'Pre-cierre guardado', color: 'text-amber-700 bg-amber-50', icon: <AlertCircle size={14} /> },
  cerrado:      { label: 'Cierre oficial', color: 'text-green-700 bg-green-50', icon: <CheckCircle size={14} /> },
}

export default function CierrePage() {
  const now = new Date()
  const [ano, setAno] = useState(now.getFullYear())
  const [mes, setMes] = useState(now.getMonth() + 1)
  const [data, setData] = useState<CierreCompleto | null>(null)
  const [estadoReg, setEstadoReg] = useState<CierreEstado | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [guardando, setGuardando] = useState<'borrador' | 'cerrado' | null>(null)
  const [msg, setMsg] = useState('')

  async function cargar() {
    setLoading(true); setError(''); setData(null); setMsg('')
    try {
      const [resCalculo, resEstado] = await Promise.allSettled([
        api.get<CierreCompleto>(`/cierre/${ano}/${mes}`),
        api.get<CierreEstado>(`/cierre/${ano}/${mes}/estado`),
      ])
      if (resCalculo.status === 'fulfilled') setData(resCalculo.value)
      else setError('No se pudo calcular el cierre')
      if (resEstado.status === 'fulfilled') setEstadoReg(resEstado.value)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function guardarBorrador() {
    if (estadoReg?.estado === 'cerrado') { setMsg('❌ Ya existe un cierre oficial para este período'); return }
    setGuardando('borrador'); setMsg('')
    try {
      await api.post(`/cierre/${ano}/${mes}/borrador`, {})
      setMsg('✅ Pre-cierre guardado como borrador')
      const est = await api.get<CierreEstado>(`/cierre/${ano}/${mes}/estado`)
      setEstadoReg(est)
    } catch (e: unknown) {
      setMsg(`❌ ${e instanceof Error ? e.message : 'Error'}`)
    } finally {
      setGuardando(null)
    }
  }

  async function cerrarOficial() {
    if (estadoReg?.estado === 'cerrado') { setMsg('❌ Cierre ya fue cerrado'); return }
    const confirmar = window.confirm(`¿Confirmas el CIERRE OFICIAL de ${MESES[mes]} ${ano}?\n\nEsta acción no se puede deshacer.`)
    if (!confirmar) return
    setGuardando('cerrado'); setMsg('')
    try {
      await api.post(`/cierre/${ano}/${mes}/guardar`, {})
      setMsg('✅ Cierre oficial guardado y bloqueado')
      const est = await api.get<CierreEstado>(`/cierre/${ano}/${mes}/estado`)
      setEstadoReg(est)
    } catch (e: unknown) {
      setMsg(`❌ ${e instanceof Error ? e.message : 'Error'}`)
    } finally {
      setGuardando(null)
    }
  }

  const estadoInfo = estadoReg ? ESTADO_CONFIG[estadoReg.estado] : null
  const esCerrado = estadoReg?.estado === 'cerrado'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cierre Mensual</h1>
        <p className="text-sm text-gray-500 mt-0.5">Estado de resultados · Obligaciones fiscales · Pre-cierre y cierre oficial</p>
      </div>

      {/* Selector + Estado + Acciones */}
      <Card className="p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <select value={mes} onChange={e => setMes(+e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none">
            {MESES.slice(1).map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
          </select>
          <select value={ano} onChange={e => setAno(+e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none">
            {[2024, 2025, 2026].map(a => <option key={a} value={a}>{a}</option>)}
          </select>
          <button onClick={cargar}
            className="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
            Calcular
          </button>

          {data && !esCerrado && (
            <button onClick={guardarBorrador} disabled={guardando !== null}
              className="flex items-center gap-1.5 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              <Save size={14} />
              {guardando === 'borrador' ? 'Guardando...' : 'Guardar Pre-Cierre'}
            </button>
          )}

          {data && !esCerrado && (
            <button onClick={cerrarOficial} disabled={guardando !== null}
              className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              <CheckCircle size={14} />
              {guardando === 'cerrado' ? 'Cerrando...' : 'Cierre Oficial'}
            </button>
          )}

          {estadoInfo && (
            <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${estadoInfo.color}`}>
              {estadoInfo.icon}
              {estadoInfo.label}
            </span>
          )}
        </div>
        {msg && <p className="mt-2 text-sm">{msg}</p>}
      </Card>

      {/* Aviso si hay borrador guardado */}
      {estadoReg?.estado === 'borrador' && estadoReg.ingresos_total !== undefined && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle size={18} className="text-amber-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-amber-800">Pre-cierre guardado el {estadoReg.created_at?.slice(0, 10)}</p>
            <p className="text-xs text-amber-700 mt-0.5">
              Ingresos: {mxn(estadoReg.ingresos_total || 0)} · Egresos: {mxn(estadoReg.egresos_total || 0)} ·
              IVA neto: {mxn(estadoReg.iva_neto || 0)} · ISR: {mxn(estadoReg.isr_estimado || 0)}
            </p>
            <p className="text-xs text-amber-600 mt-1">Puedes recalcular y actualizar el borrador hasta confirmar el cierre oficial.</p>
          </div>
        </div>
      )}

      {/* Aviso cierre oficial */}
      {estadoReg?.estado === 'cerrado' && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3">
          <CheckCircle size={18} className="text-green-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-green-800">Cierre oficial — {MESES[mes]} {ano}</p>
            <p className="text-xs text-green-700 mt-0.5">Este período está cerrado y bloqueado. Los datos mostrados son de referencia.</p>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-gray-400 text-sm">
          <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          Calculando {MESES[mes]} {ano}...
        </div>
      )}
      {error && <p className="text-red-500 text-sm">Error: {error}</p>}

      {data && (
        <>
          {/* Encabezado */}
          <div className="bg-gray-900 text-white rounded-xl px-6 py-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-wider">Estado de Resultados</p>
              <p className="text-xl font-bold mt-0.5">{MESES[mes]} {ano} — {data.tenant_id}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">Facturas procesadas</p>
              <p className="text-2xl font-bold">{data.num_facturas}</p>
            </div>
          </div>

          {/* KPIs Financieros */}
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Resultados Financieros</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Ingresos" value={mxn(data.ingresos)} color="green" icon={<TrendingUp size={22} />} />
              <StatCard label="Egresos" value={mxn(data.gastos)} color="red" icon={<TrendingDown size={22} />} />
              <StatCard label="Utilidad Bruta" value={mxn(data.utilidad_bruta)}
                sub={data.ingresos > 0 ? `${((data.utilidad_bruta / data.ingresos) * 100).toFixed(1)}% margen` : undefined}
                color={data.utilidad_bruta >= 0 ? 'green' : 'red'} icon={<Activity size={22} />} />
              <StatCard label="Utilidad Neta" value={mxn(data.utilidad_neta)}
                sub={`Margen: ${data.margen_neto_pct?.toFixed(1) ?? 0}%`}
                color={data.utilidad_neta >= 0 ? 'green' : 'red'} icon={<Percent size={22} />} />
            </div>
          </div>

          {/* KPIs Fiscales */}
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Obligaciones Fiscales</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="IVA Cobrado" value={mxn(data.iva_cobrado)} sub="Trasladado a clientes" color="blue" />
              <StatCard label="IVA Acreditable" value={mxn(data.iva_pagado)} sub="Pagado a proveedores" color="gray" />
              <StatCard label="IVA Neto a Pagar" value={mxn(data.iva_neto)}
                sub={data.iva_neto > 0 ? 'Por enterar al SAT' : 'Saldo a favor'}
                color={data.iva_neto > 0 ? 'red' : 'green'} icon={<DollarSign size={22} />} />
              <StatCard label="ISR Estimado" value={mxn(data.isr_estimado)}
                sub="Art. 14 LISR · Pago provisional" color="blue" />
            </div>
          </div>

          {/* KPIs Performance */}
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Indicadores de Performance</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="EBITDA" value={mxn(data.ebitda)}
                sub={data.ingresos > 0 ? `${((data.ebitda / data.ingresos) * 100).toFixed(1)}% de ingresos` : undefined}
                color={data.ebitda >= 0 ? 'green' : 'red'} icon={<BarChart2 size={22} />} />
              <StatCard label="PTU Estimada" value={mxn(data.ptu)} sub="10% utilidad fiscal (LSS)" color="gray" />
              <StatCard label="Margen Neto" value={`${data.margen_neto_pct?.toFixed(2) ?? 0}%`}
                sub={data.margen_neto_pct >= 15 ? 'Óptimo' : data.margen_neto_pct >= 5 ? 'Aceptable' : 'Bajo'}
                color={data.margen_neto_pct >= 15 ? 'green' : data.margen_neto_pct >= 5 ? 'blue' : 'red'}
                icon={<Percent size={22} />} />
              <StatCard label="Facturas" value={String(data.num_facturas)}
                sub={`Período ${data.periodo}`} color="gray" icon={<FileText size={22} />} />
            </div>
          </div>

          {/* Desglose completo */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Estado de Resultados — {MESES[mes]} {ano}</h2>
              <Row label="(+) Ingresos totales" value={mxn(data.ingresos)} highlight />
              <Row label="(−) Egresos / Costos" value={mxn(data.gastos)} />
              <Row label="(=) Utilidad bruta" value={mxn(data.utilidad_bruta)} highlight />
              <div className="my-2 border-t border-gray-100" />
              <Row label="EBITDA" value={mxn(data.ebitda)} />
              <Row label="Margen EBITDA" value={data.ingresos > 0 ? `${((data.ebitda / data.ingresos) * 100).toFixed(1)}%` : '—'} />
              <div className="my-2 border-t border-gray-100" />
              <Row label="(−) ISR estimado" value={`(${mxn(data.isr_estimado)})`} />
              <Row label="(−) PTU estimada" value={`(${mxn(data.ptu)})`} />
              <Row label="(=) Utilidad neta" value={mxn(data.utilidad_neta)} highlight />
              <Row label="Margen neto" value={`${data.margen_neto_pct?.toFixed(2) ?? 0}%`} />
            </Card>

            <Card className="p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Posición Fiscal — {MESES[mes]} {ano}</h2>
              <Row label="IVA trasladado (cobrado)" value={mxn(data.iva_cobrado)} />
              <Row label="IVA acreditable (pagado)" value={`(${mxn(data.iva_pagado)})`} />
              <Row label="IVA neto a declarar" value={mxn(data.iva_neto)} highlight />
              <div className="my-2 border-t border-gray-100" />
              <Row label="ISR pago provisional" value={mxn(data.isr_estimado)} />
              <Row label="Base para ISR (utilidad)" value={mxn(data.utilidad_bruta)} />
              <Row label="Tasa ISR (PM)" value="30% — Art. 9 LISR" />
              <div className="my-2 border-t border-gray-100" />
              <Row label="PTU (participación trabajadores)" value={mxn(data.ptu)} />
              <Row label="Total obligaciones del mes"
                value={mxn(data.iva_neto + data.isr_estimado + data.ptu)} highlight />
            </Card>
          </div>

          {/* Calculos 147 */}
          {data.calculos_147 && Object.keys(data.calculos_147).length > 0 && (
            <Card className="p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Indicadores Adicionales (Cálculos 147)</h2>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(data.calculos_147)
                  .filter(([, v]) => typeof v === 'number' && v !== 0)
                  .slice(0, 8)
                  .map(([key, val]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-400 capitalize">{key.replace(/_/g, ' ')}</p>
                      <p className="text-sm font-semibold text-gray-800 mt-1">
                        {typeof val === 'number' && Math.abs(val) > 10
                          ? mxn(val as number)
                          : `${(val as number).toFixed(2)}%`}
                      </p>
                    </div>
                  ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
