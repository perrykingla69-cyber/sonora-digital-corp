'use client'

import { useEffect, useRef, useState } from 'react'
import { api, Factura } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Upload, CheckCircle, XCircle, Clock, Plus } from 'lucide-react'
import Link from 'next/link'

const fmt = (v: number, moneda = 'MXN') =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: moneda }).format(v)

export default function FacturasPage() {
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  function load() {
    api.get<Factura[]>('/facturas?limit=50')
      .then(setFacturas)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function handlePagar(id: string) {
    await api.patch(`/facturas/${id}/pagar`)
    load()
  }

  async function handleCancelar(id: string) {
    if (!confirm('¿Cancelar esta factura?')) return
    await api.patch(`/facturas/${id}/cancelar`)
    load()
  }

  async function handleUploadXML(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFiles = e.target.files
    if (!selectedFiles || selectedFiles.length === 0) return
    const files = Array.from(selectedFiles).filter(file => file.name.toLowerCase().endsWith('.xml'))
    if (files.length === 0) {
      setUploadMsg('⚠️ Solo se aceptan archivos XML')
      if (fileRef.current) fileRef.current.value = ''
      return
    }
    setUploading(true)
    setUploadMsg('')
    try {
      const BASE = process.env.NEXT_PUBLIC_API_URL || ''
      const token = localStorage.getItem('hermes_token')
      const results = await Promise.allSettled(
        files.map(async (file) => {
          const text = await file.text()
          const res = await fetch(`${BASE}/facturas/xml`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/xml', Authorization: `Bearer ${token}` },
            body: text,
          })
          if (!res.ok) {
            const detail = (await res.json()).detail || 'Error'
            throw new Error(`${file.name}: ${detail}`)
          }
          return file.name
        })
      )
      const successCount = results.filter(result => result.status === 'fulfilled').length
      const failedResults = results
        .filter((result): result is PromiseRejectedResult => result.status === 'rejected')
        .map(result => result.reason instanceof Error ? result.reason.message : 'Error desconocido')

      if (failedResults.length === 0) {
        setUploadMsg(`✅ ${successCount} XML importados correctamente`)
      } else {
        const errorsPreview = failedResults.slice(0, 2).join(' | ')
        setUploadMsg(`⚠️ ${successCount} importados, ${failedResults.length} con error. ${errorsPreview}`)
      }
      load()
    } catch (err: unknown) {
      setUploadMsg(`❌ ${err instanceof Error ? err.message : 'Error'}`)
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const pendientes = facturas.filter(f => f.estado === 'pendiente')
  const pagadas    = facturas.filter(f => f.estado === 'pagada')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Facturas</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {pendientes.length} pendientes · {pagadas.length} pagadas
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input ref={fileRef} type="file" accept=".xml" multiple className="hidden" onChange={handleUploadXML} />
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 border border-gray-200 hover:bg-gray-50 text-gray-700 text-sm
                       font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Upload size={16} />
            {uploading ? 'Subiendo...' : 'Cargar XMLs'}
          </button>
          <Link
            href="/facturas/nueva"
            className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-sm
                       font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus size={16} />
            Nueva factura
          </Link>
          {uploadMsg && <p className="text-xs mt-1 text-right">{uploadMsg}</p>}
        </div>
      </div>

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wide">
                <th className="text-left px-4 py-3">Folio</th>
                <th className="text-left px-4 py-3">Emisor</th>
                <th className="text-left px-4 py-3">Fecha</th>
                <th className="text-right px-4 py-3">Total</th>
                <th className="text-center px-4 py-3">Tipo</th>
                <th className="text-center px-4 py-3">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {facturas.map(f => (
                <tr key={f.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-600">{f.folio || '—'}</td>
                  <td className="px-4 py-3 font-medium max-w-[180px] truncate">{f.emisor_nombre}</td>
                  <td className="px-4 py-3 text-gray-500">{f.fecha?.slice(0,10)}</td>
                  <td className="px-4 py-3 text-right font-semibold">{fmt(f.total, f.moneda)}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`text-xs font-medium ${f.tipo === 'ingreso' ? 'text-emerald-600' : 'text-red-500'}`}>
                      {f.tipo}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={f.estado} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    {f.estado === 'pendiente' && (
                      <div className="flex items-center gap-1 justify-end">
                        <button
                          onClick={() => handlePagar(f.id)}
                          className="text-emerald-600 hover:text-emerald-700"
                          title="Marcar como pagada"
                        >
                          <CheckCircle size={16} />
                        </button>
                        <button
                          onClick={() => handleCancelar(f.id)}
                          className="text-red-400 hover:text-red-600"
                          title="Cancelar"
                        >
                          <XCircle size={16} />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {!loading && facturas.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center text-gray-400 py-8">
                    <Clock size={32} className="mx-auto mb-2 opacity-30" />
                    No hay facturas. Carga un CFDI XML para comenzar.
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
