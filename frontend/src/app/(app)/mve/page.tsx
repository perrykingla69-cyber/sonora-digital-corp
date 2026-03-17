'use client'

import { useEffect, useState } from 'react'
import { api, MVE } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Package } from 'lucide-react'

const fmt = (v: number, moneda = 'MXN') =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: moneda }).format(v)

export default function MVEPage() {
  const [mves, setMves]     = useState<MVE[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  function load() {
    api.get<MVE[]>('/mve?limit=50')
      .then(setMves)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function presentar(id: string) {
    await api.patch(`/mve/${id}/presentar`)
    load()
  }

  const pendientes  = mves.filter(m => m.estado === 'pendiente').length
  const presentadas = mves.filter(m => m.estado === 'presentada').length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Manifestación de Valor (MVE)</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          {pendientes} pendientes · {presentadas} presentadas
        </p>
      </div>

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wide">
                <th className="text-left px-4 py-3">Pedimento</th>
                <th className="text-left px-4 py-3">Mercancía</th>
                <th className="text-left px-4 py-3">Fecha</th>
                <th className="text-center px-4 py-3">Incoterm</th>
                <th className="text-right px-4 py-3">Valor factura</th>
                <th className="text-right px-4 py-3">Valor aduana</th>
                <th className="text-center px-4 py-3">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {mves.map(m => (
                <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs">{m.numero_pedimento || '—'}</td>
                  <td className="px-4 py-3 max-w-[200px] truncate">{m.descripcion_mercancia}</td>
                  <td className="px-4 py-3 text-gray-500">{m.fecha?.slice(0,10)}</td>
                  <td className="px-4 py-3 text-center font-medium">{m.incoterm}</td>
                  <td className="px-4 py-3 text-right">{fmt(m.valor_factura, m.moneda)}</td>
                  <td className="px-4 py-3 text-right font-semibold">{fmt(m.valor_aduana)}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={m.estado} />
                  </td>
                  <td className="px-4 py-3">
                    {m.estado === 'pendiente' && (
                      <button
                        onClick={() => presentar(m.id)}
                        className="text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 px-2 py-1 rounded"
                      >
                        Presentar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {!loading && mves.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center text-gray-400 py-8">
                    <Package size={32} className="mx-auto mb-2 opacity-30" />
                    Sin MVEs registradas
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
