'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { ArrowLeft, Save } from 'lucide-react'
import Link from 'next/link'

const today = () => new Date().toISOString().slice(0, 10)

export default function NuevaFacturaPage() {
  const router = useRouter()
  const [saving, setSaving] = useState(false)
  const [error, setError]   = useState('')

  const [form, setForm] = useState({
    tipo:           'ingreso',
    folio:          '',
    concepto:       '',
    rfc_emisor:     '',
    nombre_emisor:  '',
    rfc_receptor:   '',
    nombre_receptor:'',
    subtotal:       '',
    moneda:         'MXN',
    estado:         'pendiente',
    fecha_emision:  today(),
  })

  function set(k: string, v: string) {
    setForm(f => ({ ...f, [k]: v }))
  }

  const subtotal = parseFloat(form.subtotal) || 0
  const iva      = subtotal * 0.16
  const total    = subtotal + iva

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.concepto || subtotal <= 0) {
      setError('Concepto y subtotal son requeridos.')
      return
    }
    setSaving(true)
    setError('')
    try {
      await api.post('/facturas', {
        ...form,
        subtotal,
        iva,
        total,
        fecha_emision: form.fecha_emision ? new Date(form.fecha_emision).toISOString() : undefined,
      })
      router.push('/facturas')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  const inp = 'w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500'
  const lbl = 'block text-xs font-medium text-gray-500 mb-1'

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/facturas" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Nueva factura</h1>
          <p className="text-sm text-gray-500">Registra un ingreso o gasto manualmente</p>
        </div>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5 p-1">

          {/* Tipo + Estado */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={lbl}>Tipo</label>
              <select className={inp} value={form.tipo} onChange={e => set('tipo', e.target.value)}>
                <option value="ingreso">Ingreso</option>
                <option value="gasto">Gasto</option>
              </select>
            </div>
            <div>
              <label className={lbl}>Estado</label>
              <select className={inp} value={form.estado} onChange={e => set('estado', e.target.value)}>
                <option value="pendiente">Pendiente</option>
                <option value="pagada">Pagada</option>
              </select>
            </div>
          </div>

          {/* Concepto + Folio */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <label className={lbl}>Concepto *</label>
              <input className={inp} value={form.concepto} onChange={e => set('concepto', e.target.value)}
                placeholder="Descripción del servicio o producto" />
            </div>
            <div>
              <label className={lbl}>Folio</label>
              <input className={inp} value={form.folio} onChange={e => set('folio', e.target.value)}
                placeholder="A-001" />
            </div>
          </div>

          {/* Emisor */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={lbl}>RFC Emisor</label>
              <input className={inp} value={form.rfc_emisor} onChange={e => set('rfc_emisor', e.target.value.toUpperCase())}
                placeholder="XAXX010101000" />
            </div>
            <div>
              <label className={lbl}>Nombre Emisor</label>
              <input className={inp} value={form.nombre_emisor} onChange={e => set('nombre_emisor', e.target.value)}
                placeholder="Proveedor S.A. de C.V." />
            </div>
          </div>

          {/* Receptor */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={lbl}>RFC Receptor</label>
              <input className={inp} value={form.rfc_receptor} onChange={e => set('rfc_receptor', e.target.value.toUpperCase())}
                placeholder="XAXX010101000" />
            </div>
            <div>
              <label className={lbl}>Nombre Receptor</label>
              <input className={inp} value={form.nombre_receptor} onChange={e => set('nombre_receptor', e.target.value)}
                placeholder="Mi empresa S.A. de C.V." />
            </div>
          </div>

          {/* Montos */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={lbl}>Subtotal *</label>
              <input className={inp} type="number" min="0" step="0.01"
                value={form.subtotal} onChange={e => set('subtotal', e.target.value)}
                placeholder="0.00" />
            </div>
            <div>
              <label className={lbl}>Moneda</label>
              <select className={inp} value={form.moneda} onChange={e => set('moneda', e.target.value)}>
                <option value="MXN">MXN</option>
                <option value="USD">USD</option>
              </select>
            </div>
            <div>
              <label className={lbl}>Fecha emisión</label>
              <input className={inp} type="date" value={form.fecha_emision}
                onChange={e => set('fecha_emision', e.target.value)} />
            </div>
          </div>

          {/* Resumen de totales */}
          {subtotal > 0 && (
            <div className="rounded-lg bg-gray-50 p-4 text-sm space-y-1">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>{new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(subtotal)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>IVA 16%</span>
                <span>{new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(iva)}</span>
              </div>
              <div className="flex justify-between font-semibold text-gray-900 border-t pt-1">
                <span>Total</span>
                <span>{new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(total)}</span>
              </div>
            </div>
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}

          <div className="flex items-center justify-between pt-2">
            <Link href="/facturas" className="text-sm text-gray-500 hover:text-gray-700">
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
                         text-sm font-medium px-5 py-2.5 rounded-lg transition-colors disabled:opacity-50"
            >
              <Save size={16} />
              {saving ? 'Guardando...' : 'Guardar factura'}
            </button>
          </div>
        </form>
      </Card>

      <p className="text-xs text-gray-400 text-center">
        Para facturas electrónicas oficiales, carga el XML desde la pantalla de Facturas.
        Este formulario registra movimientos manuales de ingreso/gasto.
      </p>
    </div>
  )
}
