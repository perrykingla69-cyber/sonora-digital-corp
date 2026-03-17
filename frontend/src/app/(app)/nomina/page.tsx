'use client'

import { useEffect, useState } from 'react'
import { api, Empleado, Nomina } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Calculator } from 'lucide-react'

const fmt = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(v)

export default function NominaPage() {
  const [empleados, setEmpleados] = useState<Empleado[]>([])
  const [nominas,   setNominas]   = useState<Nomina[]>([])
  const [loading, setLoading]     = useState(true)
  const [calcId, setCalcId]       = useState('')
  const [dias, setDias]           = useState('15')
  const [calcResult, setCalcResult] = useState<Nomina | null>(null)
  const [calcError,  setCalcError]  = useState('')

  useEffect(() => {
    Promise.all([
      api.get<Empleado[]>('/empleados'),
      api.get<Nomina[]>('/nominas/historial').catch(() => []),
    ]).then(([emps, noms]) => {
      setEmpleados(emps)
      setNominas(Array.isArray(noms) ? noms : [])
    }).finally(() => setLoading(false))
  }, [])

  async function calcularNomina() {
    if (!calcId) return
    setCalcError('')
    setCalcResult(null)
    try {
      const today = new Date()
      const inicio = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0,10)
      const fin    = today.toISOString().slice(0,10)
      const result = await api.post<Nomina>('/nominas/calcular', {
        empleado_id: calcId,
        periodo_inicio: inicio,
        periodo_fin: fin,
        dias_trabajados: parseInt(dias),
      })
      setCalcResult(result)
    } catch (e: unknown) {
      setCalcError(e instanceof Error ? e.message : 'Error')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Nómina</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculadora */}
        <Card className="p-5 lg:col-span-1">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Calculator size={16} /> Calcular nómina
          </h2>
          <div className="space-y-3">
            <select
              value={calcId}
              onChange={e => setCalcId(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
            >
              <option value="">Seleccionar empleado</option>
              {empleados.filter(e => e.activo).map(e => (
                <option key={e.id} value={e.id}>{e.nombre}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <input
                type="number"
                value={dias}
                onChange={e => setDias(e.target.value)}
                min="1" max="31"
                className="w-20 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none"
                placeholder="Días"
              />
              <span className="self-center text-sm text-gray-500">días trabajados</span>
            </div>
            <button
              onClick={calcularNomina}
              className="w-full bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium py-2 rounded-lg transition-colors"
            >
              Calcular
            </button>

            {calcError && <p className="text-red-500 text-xs">{calcError}</p>}

            {calcResult && (
              <div className="mt-3 bg-gray-50 rounded-lg p-3 space-y-1.5 text-sm">
                <p className="font-medium text-gray-800">{calcResult.empleado_nombre}</p>
                <div className="flex justify-between text-gray-600">
                  <span>Bruto</span><span className="font-medium">{fmt(calcResult.salario_bruto)}</span>
                </div>
                <div className="flex justify-between text-gray-500 text-xs">
                  <span>ISR</span><span>-{fmt(calcResult.isr)}</span>
                </div>
                <div className="flex justify-between text-gray-500 text-xs">
                  <span>IMSS</span><span>-{fmt(calcResult.imss)}</span>
                </div>
                <div className="flex justify-between text-emerald-700 font-semibold border-t border-gray-200 pt-1.5 mt-1.5">
                  <span>Neto</span><span>{fmt(calcResult.salario_neto)}</span>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Empleados */}
        <Card className="lg:col-span-2">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Empleados ({empleados.length})</h2>
          </div>
          {loading ? (
            <p className="text-gray-400 text-sm p-4">Cargando...</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="text-left px-4 py-3">Nombre</th>
                  <th className="text-left px-4 py-3">Depto.</th>
                  <th className="text-right px-4 py-3">Salario diario</th>
                  <th className="text-center px-4 py-3">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {empleados.map(e => (
                  <tr key={e.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{e.nombre}</td>
                    <td className="px-4 py-3 text-gray-500">{e.departamento || '—'}</td>
                    <td className="px-4 py-3 text-right">{fmt(e.salario_diario)}</td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={e.activo ? 'activo' : 'inactivo'} />
                    </td>
                  </tr>
                ))}
                {empleados.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-gray-400 py-8">Sin empleados registrados</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </Card>
      </div>
    </div>
  )
}
