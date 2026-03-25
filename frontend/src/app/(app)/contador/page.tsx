'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { api } from '@/lib/api'
import AuthGuard from '@/components/layout/AuthGuard'
import { getToken } from '@/lib/auth'
import {
  Users, Upload, CheckCircle, XCircle, AlertCircle,
  TrendingUp, TrendingDown, FileText, RefreshCw,
  ChevronRight, Building2, DollarSign, Clock, X,
} from 'lucide-react'
import Link from 'next/link'
import clsx from 'clsx'

interface Cliente {
  id: string
  nombre: string
  rfc: string
  plan: string
  facturas_mes: number
  ingresos_mes: number
  egresos_mes: number
  iva_neto_mes: number
  isr_retenido_mes: number
  pendientes_pago: number
  tiene_cierre: boolean
  estado_cierre: string | null
  semaforo: 'green' | 'yellow' | 'red'
}

interface BulkResult {
  file: string
  ok: boolean
  tenant?: string
  tipo?: string
  total?: number
  error?: string
}

const SEMAFORO_CONFIG = {
  green:  { color: 'bg-emerald-500', label: 'Al día',       ring: 'ring-emerald-200' },
  yellow: { color: 'bg-amber-400',   label: 'En proceso',   ring: 'ring-amber-200'  },
  red:    { color: 'bg-red-500',     label: 'Sin facturas', ring: 'ring-red-200'    },
}

const MXN = (n: number) => `$${n.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

export default function ContadorPage() {
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [bulkResults, setBulkResults] = useState<BulkResult[] | null>(null)
  const [bulkSummary, setBulkSummary] = useState<{ total: number; ok: number; errores: number } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadClientes = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.get<Cliente[]>('/contador/clientes')
      setClientes(data)
    } catch { /* silencio */ }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { loadClientes() }, [loadClientes])

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return
    const xmlFiles = Array.from(files).filter(f => f.name.toLowerCase().endsWith('.xml'))
    if (xmlFiles.length === 0) return

    setUploading(true); setBulkResults(null); setBulkSummary(null)
    try {
      const token = getToken()
      const form = new FormData()
      xmlFiles.forEach(f => form.append('files', f))
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/contador/xmls/bulk`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      })
      const data = await res.json()
      setBulkResults(data.detalle || [])
      setBulkSummary({ total: data.total, ok: data.ok, errores: data.errores })
      if (data.ok > 0) loadClientes()
    } catch (e) {
      console.error(e)
    } finally {
      setUploading(false)
    }
  }

  // Totales globales
  const totalIngresos = clientes.reduce((s, c) => s + c.ingresos_mes, 0)
  const totalEgresos  = clientes.reduce((s, c) => s + c.egresos_mes, 0)
  const totalIvaNeto  = clientes.reduce((s, c) => s + c.iva_neto_mes, 0)
  const totalFacturas = clientes.reduce((s, c) => s + c.facturas_mes, 0)
  const verdes  = clientes.filter(c => c.semaforo === 'green').length
  const amarillos = clientes.filter(c => c.semaforo === 'yellow').length
  const rojos   = clientes.filter(c => c.semaforo === 'red').length

  const mes = new Date().toLocaleString('es-MX', { month: 'long', year: 'numeric' })

  if (loading) return (
    <div className="flex items-center gap-2 text-gray-400 text-sm mt-8">
      <div className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      Cargando clientes...
    </div>
  )

  return (
    <AuthGuard allowedRoles={['contador', 'admin', 'ceo']}>
      <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Contador</h1>
          <p className="text-sm text-gray-500 mt-0.5 capitalize">{mes} — {clientes.length} clientes activos</p>
        </div>
        <button onClick={loadClientes} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition-colors">
          <RefreshCw size={14} /> Actualizar
        </button>
      </div>

      {/* KPIs globales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Ingresos mes', value: MXN(totalIngresos), icon: TrendingUp, color: 'text-emerald-600' },
          { label: 'Egresos mes',  value: MXN(totalEgresos),  icon: TrendingDown, color: 'text-red-500'   },
          { label: 'IVA neto',     value: MXN(totalIvaNeto),  icon: DollarSign,   color: 'text-blue-600'  },
          { label: 'Facturas mes', value: totalFacturas,      icon: FileText,     color: 'text-purple-600'},
        ].map(k => (
          <div key={k.label} className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
              <k.icon size={14} className={k.color} /> {k.label}
            </div>
            <p className="text-xl font-bold text-gray-900">{k.value}</p>
          </div>
        ))}
      </div>

      {/* Semáforo resumen */}
      <div className="flex gap-3">
        {[
          { label: 'Al día', count: verdes,    color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
          { label: 'En proceso', count: amarillos, color: 'bg-amber-100 text-amber-700 border-amber-200'   },
          { label: 'Sin facturas', count: rojos, color: 'bg-red-100 text-red-700 border-red-200'          },
        ].map(s => (
          <div key={s.label} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-semibold ${s.color}`}>
            <span className="font-bold text-base">{s.count}</span> {s.label}
          </div>
        ))}
      </div>

      {/* Zona de carga masiva de XMLs */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files) }}
        className={clsx(
          'border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer',
          dragging ? 'border-brand-400 bg-brand-50' : 'border-gray-200 hover:border-brand-300 hover:bg-gray-50',
          uploading && 'opacity-50 pointer-events-none'
        )}
        onClick={() => fileRef.current?.click()}
      >
        <input ref={fileRef} type="file" accept=".xml" multiple className="hidden"
          onChange={e => handleFiles(e.target.files)} />
        {uploading ? (
          <div className="flex items-center justify-center gap-2 text-brand-600">
            <div className="w-5 h-5 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
            Procesando XMLs...
          </div>
        ) : (
          <>
            <Upload size={28} className="mx-auto text-gray-400 mb-2" />
            <p className="text-sm font-semibold text-gray-700">Arrastra XMLs CFDI aquí o haz clic</p>
            <p className="text-xs text-gray-400 mt-1">Asignación automática por RFC · Múltiples archivos · Detección de duplicados</p>
          </>
        )}
      </div>

      {/* Resultados de carga masiva */}
      {bulkSummary && bulkResults && (
        <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <h3 className="font-semibold text-gray-800 text-sm">Resultado de carga</h3>
              <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-medium">{bulkSummary.ok} cargados</span>
              {bulkSummary.errores > 0 && (
                <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-medium">{bulkSummary.errores} errores</span>
              )}
            </div>
            <button onClick={() => { setBulkResults(null); setBulkSummary(null) }}><X size={16} className="text-gray-400 hover:text-gray-600" /></button>
          </div>
          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {bulkResults.map((r, i) => (
              <div key={i} className={clsx('flex items-center gap-2 text-xs p-2 rounded-lg',
                r.ok ? 'bg-emerald-50' : 'bg-red-50')}>
                {r.ok
                  ? <CheckCircle size={13} className="text-emerald-500 flex-shrink-0" />
                  : <XCircle size={13} className="text-red-500 flex-shrink-0" />
                }
                <span className="font-medium text-gray-700 truncate max-w-[200px]">{r.file}</span>
                {r.ok
                  ? <span className="text-gray-500">→ <strong>{r.tenant}</strong> · {r.tipo} · {MXN(r.total || 0)}</span>
                  : <span className="text-red-600">{r.error}</span>
                }
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grid de clientes */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Clientes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {clientes.map(c => {
            const sem = SEMAFORO_CONFIG[c.semaforo]
            return (
              <div key={c.id}
                className={clsx('bg-white border border-gray-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow ring-2', sem.ring)}>
                {/* Header cliente */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className={clsx('w-2.5 h-2.5 rounded-full flex-shrink-0 mt-1', sem.color)} />
                    <div>
                      <h3 className="font-bold text-gray-900 text-sm leading-tight">{c.nombre}</h3>
                      <p className="text-xs text-gray-400 font-mono">{c.rfc}</p>
                    </div>
                  </div>
                  <span className={clsx('text-xs px-2 py-0.5 rounded-full font-semibold',
                    c.semaforo === 'green' ? 'bg-emerald-100 text-emerald-700' :
                    c.semaforo === 'yellow' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-600'
                  )}>{sem.label}</span>
                </div>

                {/* Métricas */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-400">Ingresos</p>
                    <p className="text-sm font-bold text-emerald-700">{MXN(c.ingresos_mes)}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-400">Egresos</p>
                    <p className="text-sm font-bold text-red-600">{MXN(c.egresos_mes)}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-400">IVA neto</p>
                    <p className={clsx('text-sm font-bold', c.iva_neto_mes >= 0 ? 'text-blue-700' : 'text-emerald-700')}>
                      {MXN(c.iva_neto_mes)}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-400">Facturas</p>
                    <p className="text-sm font-bold text-gray-800">{c.facturas_mes}</p>
                  </div>
                </div>

                {/* ISR + pendientes */}
                <div className="flex items-center justify-between text-xs mb-3">
                  {c.isr_retenido_mes > 0 && (
                    <span className="text-amber-600 font-medium">ISR ret. {MXN(c.isr_retenido_mes)}</span>
                  )}
                  {c.pendientes_pago > 0 && (
                    <span className="flex items-center gap-1 text-orange-600">
                      <Clock size={11} /> {c.pendientes_pago} pend. pago
                    </span>
                  )}
                  {c.tiene_cierre && (
                    <span className={clsx('flex items-center gap-1',
                      c.estado_cierre === 'cerrado' ? 'text-emerald-600' : 'text-amber-600')}>
                      {c.estado_cierre === 'cerrado' ? <CheckCircle size={11} /> : <AlertCircle size={11} />}
                      Cierre {c.estado_cierre}
                    </span>
                  )}
                </div>

                {/* Acciones rápidas */}
                <div className="flex gap-2 pt-2 border-t border-gray-100">
                  <Link
                    href={`/facturas?tenant=${c.id}`}
                    className="flex-1 text-center text-xs text-gray-500 hover:text-brand-600 py-1.5 rounded-lg hover:bg-brand-50 transition-colors"
                  >
                    <FileText size={12} className="inline mr-1" />Facturas
                  </Link>
                  <Link
                    href={`/cierre?tenant=${c.id}`}
                    className="flex-1 text-center text-xs text-gray-500 hover:text-brand-600 py-1.5 rounded-lg hover:bg-brand-50 transition-colors"
                  >
                    <Building2 size={12} className="inline mr-1" />Cierre
                  </Link>
                  <Link
                    href={`/resico?tenant=${c.id}`}
                    className="flex-1 text-center text-xs text-gray-500 hover:text-brand-600 py-1.5 rounded-lg hover:bg-brand-50 transition-colors"
                  >
                    <ChevronRight size={12} className="inline" />RESICO
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      </div>
      </div>
    </AuthGuard>
  )
}
