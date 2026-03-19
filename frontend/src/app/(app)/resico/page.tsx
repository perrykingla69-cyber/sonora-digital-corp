'use client'

import { useEffect, useState, useRef } from 'react'
import { api } from '@/lib/api'
import { Card, StatCard } from '@/components/ui/Card'
import {
  Upload, FileText, CheckCircle, Clock, AlertCircle,
  TrendingUp, TrendingDown, DollarSign, RefreshCw,
} from 'lucide-react'

const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 2 }).format(v ?? 0)

const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

type TipoPago = 'prepagado' | 'pendiente' | 'pagado' | 'cancelado'

const TIPO_PAGO_CONFIG: Record<TipoPago, { label: string; color: string; icon: React.ReactNode }> = {
  prepagado:  { label: 'Prepagado',  color: 'bg-blue-100 text-blue-700',   icon: <CheckCircle size={12} /> },
  pendiente:  { label: 'Pendiente',  color: 'bg-amber-100 text-amber-700', icon: <Clock size={12} /> },
  pagado:     { label: 'Pagado',     color: 'bg-green-100 text-green-700', icon: <CheckCircle size={12} /> },
  cancelado:  { label: 'Cancelado',  color: 'bg-red-100 text-red-700',     icon: <AlertCircle size={12} /> },
}

interface ResumenFiscal {
  periodo: string
  tenant_id: string
  ingresos: { total: number; pagado: number; pendiente: number; prepagado: number; num_cfdi: number }
  egresos: { total: number; num_cfdi: number }
  iva: {
    iva_cobrado: number; iva_acreditable: number
    iva_retenido_a_favor: number; iva_neto_a_pagar: number
    num_facturas_ingreso: number; num_facturas_egreso: number
  }
  isr_retenido: {
    total_isr_retenido: number; total_ingresos_con_retencion: number
    tasa_efectiva_pct: number; num_cfdi_con_retencion: number; num_cfdi_sin_retencion: number
  }
}

interface DetalleFactura {
  uuid?: string; folio?: string
  rfc_receptor?: string; rfc_emisor?: string
  nombre_receptor?: string; nombre_emisor?: string
  subtotal: number; iva: number; total: number
  isr_retenido?: number; iva_retenido?: number
  fecha: string; tipo_pago: string; concepto?: string; tasa_pct?: number
}

interface ReporteIva {
  resumen: ResumenFiscal['iva']
  detalle_ingresos: DetalleFactura[]
  detalle_egresos: DetalleFactura[]
}

export default function ResicoPage() {
  const now = new Date()
  const [ano, setAno] = useState(now.getFullYear())
  const [mes, setMes] = useState(now.getMonth() + 1)
  const [tab, setTab] = useState<'resumen' | 'iva' | 'isr' | 'upload'>('resumen')

  const [resumen, setResumen] = useState<ResumenFiscal | null>(null)
  const [reporteIva, setReporteIva] = useState<ReporteIva | null>(null)
  const [reporteIsr, setReporteIsr] = useState<{ resumen: ResumenFiscal['isr_retenido']; detalle: DetalleFactura[] } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Upload state
  const [subiendo, setSubiendo] = useState(false)
  const [uploadMsg, setUploadMsg] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  async function cargar() {
    setLoading(true); setError('')
    try {
      const [r1, r2, r3] = await Promise.allSettled([
        api.get<ResumenFiscal>(`/resico/resumen/${ano}/${mes}`),
        api.get<ReporteIva>(`/resico/reporte-iva/${ano}/${mes}`),
        api.get<{ resumen: ResumenFiscal['isr_retenido']; detalle: DetalleFactura[] }>(`/resico/reporte-isr-retenido/${ano}/${mes}`),
      ])
      if (r1.status === 'fulfilled') setResumen(r1.value)
      if (r2.status === 'fulfilled') setReporteIva(r2.value)
      if (r3.status === 'fulfilled') setReporteIsr(r3.value)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function subirXml(files: FileList | null) {
    if (!files || files.length === 0) return
    setSubiendo(true); setUploadMsg('')
    const resultados: string[] = []

    for (const file of Array.from(files)) {
      if (!file.name.endsWith('.xml')) {
        resultados.push(`⚠️ ${file.name}: no es XML`)
        continue
      }
      const form = new FormData()
      form.append('archivo', file)
      try {
        const token = localStorage.getItem('mystic_token')
        const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/facturas/xml`, {
          method: 'POST',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: form,
        })
        const data = await r.json()
        if (r.ok) {
          const tipo = data.tipo === 'ingreso' ? '📥 Ingreso' : '📤 Egreso'
          const regimen = data.regimen_fiscal ? ` [${data.regimen_fiscal}]` : ''
          const isr = data.isr_retenido > 0 ? ` · ISR ret: ${mxn(data.isr_retenido)}` : ''
          resultados.push(`✅ ${tipo}${regimen}: ${mxn(data.total)}${isr}`)
        } else if (r.status === 409) {
          resultados.push(`⚠️ ${file.name}: ya registrado`)
        } else {
          resultados.push(`❌ ${file.name}: ${data.detail || data.error || 'Error'}`)
        }
      } catch {
        resultados.push(`❌ ${file.name}: error de conexión`)
      }
    }

    setUploadMsg(resultados.join('\n'))
    setSubiendo(false)
    await cargar() // refresca datos
  }

  async function cambiarTipoPago(facturaId: string, tipoPago: TipoPago) {
    await api.patch(`/facturas/${facturaId}/tipo-pago`, { tipo_pago: tipoPago })
    await cargar()
  }

  const Row = ({ label, value, highlight, sub }: { label: string; value: string; highlight?: boolean; sub?: string }) => (
    <div className={`flex justify-between py-2 border-b border-gray-50 last:border-0 ${highlight ? 'font-bold' : ''}`}>
      <div>
        <span className="text-gray-500 text-sm">{label}</span>
        {sub && <p className="text-xs text-gray-400">{sub}</p>}
      </div>
      <span className={`text-sm ${highlight ? 'text-gray-900 text-base' : 'text-gray-700'}`}>{value}</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Contabilidad RESICO</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Régimen Simplificado de Confianza · IVA · ISR Retenido 1.25% · Estados de pago
        </p>
      </div>

      {/* Selector + Tabs */}
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
          <button onClick={cargar} disabled={loading}
            className="flex items-center gap-1.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Actualizar
          </button>
        </div>

        <div className="flex gap-1 mt-3 border-b border-gray-100">
          {(['resumen', 'iva', 'isr', 'upload'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${tab === t ? 'bg-brand-600 text-white' : 'text-gray-500 hover:text-gray-700'}`}>
              {t === 'resumen' ? 'Resumen' : t === 'iva' ? 'Reporte IVA' : t === 'isr' ? 'ISR Retenido' : 'Cargar XMLs'}
            </button>
          ))}
        </div>
      </Card>

      {error && <p className="text-red-500 text-sm">Error: {error}</p>}

      {/* TAB: RESUMEN */}
      {tab === 'resumen' && resumen && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Ingresos del mes" value={mxn(resumen.ingresos.total)} color="green"
              sub={`${resumen.ingresos.num_cfdi} CFDIs`} icon={<TrendingUp size={22} />} />
            <StatCard label="Egresos del mes" value={mxn(resumen.egresos.total)} color="red"
              sub={`${resumen.egresos.num_cfdi} CFDIs`} icon={<TrendingDown size={22} />} />
            <StatCard label="IVA neto a pagar" value={mxn(resumen.iva.iva_neto_a_pagar)}
              color={resumen.iva.iva_neto_a_pagar > 0 ? 'red' : 'green'}
              sub={resumen.iva.iva_neto_a_pagar > 0 ? 'Por enterar SAT' : 'Saldo a favor'}
              icon={<DollarSign size={22} />} />
            <StatCard label="ISR retenido" value={mxn(resumen.isr_retenido.total_isr_retenido)}
              color="blue" sub={`${resumen.isr_retenido.num_cfdi_con_retencion} CFDIs con retención`}
              icon={<FileText size={22} />} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Estados de pago ingresos */}
            <Card className="p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Ingresos por estado de pago — {MESES[mes]} {ano}</h2>
              <Row label="Pagados" value={mxn(resumen.ingresos.pagado)} />
              <Row label="Pendientes de cobro" value={mxn(resumen.ingresos.pendiente)} />
              <Row label="Prepagados" value={mxn(resumen.ingresos.prepagado)} />
              <Row label="Total ingresos" value={mxn(resumen.ingresos.total)} highlight />
            </Card>

            {/* IVA y ISR */}
            <Card className="p-5">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Posición Fiscal — {MESES[mes]} {ano}</h2>
              <Row label="IVA cobrado (ingresos)" value={mxn(resumen.iva.iva_cobrado)} />
              <Row label="IVA acreditable (egresos)" value={`(${mxn(resumen.iva.iva_acreditable)})`} />
              <Row label="IVA retenido a favor" value={`(${mxn(resumen.iva.iva_retenido_a_favor)})`} />
              <Row label="IVA neto a pagar SAT" value={mxn(resumen.iva.iva_neto_a_pagar)} highlight />
              <div className="my-2 border-t border-gray-100" />
              <Row label="ISR retenido 1.25% (Art. 113-J)" value={mxn(resumen.isr_retenido.total_isr_retenido)}
                sub={`${resumen.isr_retenido.num_cfdi_con_retencion} facturas con retención`} />
              <Row label="Tasa efectiva retenida" value={`${resumen.isr_retenido.tasa_efectiva_pct}%`} />
            </Card>
          </div>
        </div>
      )}

      {/* TAB: REPORTE IVA */}
      {tab === 'iva' && reporteIva && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="IVA Cobrado" value={mxn(reporteIva.resumen.iva_cobrado)} color="green"
              sub="De facturas de ingreso" />
            <StatCard label="IVA Acreditable" value={mxn(reporteIva.resumen.iva_acreditable)} color="blue"
              sub="De facturas de egreso" />
            <StatCard label="IVA Retenido a Favor" value={mxn(reporteIva.resumen.iva_retenido_a_favor)} color="gray"
              sub="Retenido por clientes PM" />
            <StatCard label="IVA Neto a Pagar" value={mxn(reporteIva.resumen.iva_neto_a_pagar)}
              color={reporteIva.resumen.iva_neto_a_pagar > 0 ? 'red' : 'green'}
              sub={reporteIva.resumen.iva_neto_a_pagar > 0 ? 'Enterar al SAT' : 'Saldo a favor'} />
          </div>

          <TablaFacturas
            titulo="Ingresos — IVA cobrado"
            facturas={reporteIva.detalle_ingresos}
            columnas={['fecha', 'nombre_receptor', 'subtotal', 'iva', 'iva_retenido', 'total', 'tipo_pago']}
            onChangePago={cambiarTipoPago}
          />
          <TablaFacturas
            titulo="Egresos — IVA acreditable"
            facturas={reporteIva.detalle_egresos}
            columnas={['fecha', 'nombre_emisor', 'subtotal', 'iva', 'total', 'tipo_pago']}
            onChangePago={cambiarTipoPago}
          />
        </div>
      )}

      {/* TAB: ISR RETENIDO */}
      {tab === 'isr' && reporteIsr && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <p className="text-sm font-medium text-blue-800">ISR Retenido — RESICO PF (Art. 113-J LISR)</p>
            <p className="text-xs text-blue-600 mt-1">
              Cuando una Persona Moral te paga, debe retener el 1.25% de ISR sobre el subtotal.
              Este ISR retenido se acredita contra tu ISR mensual RESICO.
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="ISR retenido total" value={mxn(reporteIsr.resumen.total_isr_retenido)} color="blue" />
            <StatCard label="Base ingresos con retención" value={mxn(reporteIsr.resumen.total_ingresos_con_retencion)} color="gray" />
            <StatCard label="Tasa efectiva" value={`${reporteIsr.resumen.tasa_efectiva_pct}%`} color="gray"
              sub="Debería ser ~1.25%" />
            <StatCard label="CFDIs con retención" value={String(reporteIsr.resumen.num_cfdi_con_retencion)} color="green" />
          </div>

          {reporteIsr.detalle.length > 0 ? (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-left">
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Fecha</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Cliente (PM)</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase text-right">Subtotal</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase text-right">ISR Ret.</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase text-right">%</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase text-right">IVA</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase text-right">Total</th>
                      <th className="px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reporteIsr.detalle.map((f, i) => (
                      <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50">
                        <td className="px-4 py-2.5 text-gray-500">{f.fecha}</td>
                        <td className="px-4 py-2.5 font-medium text-gray-800">{f.nombre_receptor || f.rfc_receptor}</td>
                        <td className="px-4 py-2.5 text-right">{mxn(f.subtotal)}</td>
                        <td className="px-4 py-2.5 text-right text-blue-700 font-semibold">{mxn(f.isr_retenido || 0)}</td>
                        <td className="px-4 py-2.5 text-right text-gray-500">{f.tasa_pct?.toFixed(4)}%</td>
                        <td className="px-4 py-2.5 text-right">{mxn(f.iva)}</td>
                        <td className="px-4 py-2.5 text-right font-medium">{mxn(f.total)}</td>
                        <td className="px-4 py-2.5">
                          <TipoPagoBadge tipo={(f.tipo_pago as TipoPago) || 'pendiente'} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-blue-50 font-bold">
                      <td colSpan={2} className="px-4 py-2.5 text-blue-800">TOTAL</td>
                      <td className="px-4 py-2.5 text-right">{mxn(reporteIsr.resumen.total_ingresos_con_retencion)}</td>
                      <td className="px-4 py-2.5 text-right text-blue-700">{mxn(reporteIsr.resumen.total_isr_retenido)}</td>
                      <td colSpan={4} />
                    </tr>
                  </tfoot>
                </table>
              </div>
            </Card>
          ) : (
            <Card className="p-8 text-center">
              <FileText size={32} className="text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">No hay CFDIs con ISR retenido en este período.</p>
              <p className="text-xs text-gray-400 mt-1">El ISR retenido aparece en facturas donde el cliente PM retuvo el 1.25%.</p>
            </Card>
          )}
        </div>
      )}

      {/* TAB: CARGAR XMLs */}
      {tab === 'upload' && (
        <div className="space-y-4">
          <div
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); subirXml(e.dataTransfer.files) }}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors
              ${dragOver ? 'border-brand-400 bg-brand-50' : 'border-gray-200 hover:border-brand-300 hover:bg-gray-50'}`}
          >
            <input ref={inputRef} type="file" accept=".xml" multiple className="hidden"
              onChange={e => subirXml(e.target.files)} />
            <Upload size={36} className={`mx-auto mb-3 ${dragOver ? 'text-brand-500' : 'text-gray-300'}`} />
            <p className="text-sm font-medium text-gray-600">
              {subiendo ? 'Procesando XMLs...' : 'Arrastra tus CFDIs aquí o haz clic para seleccionar'}
            </p>
            <p className="text-xs text-gray-400 mt-1">CFDI 4.0 y 3.3 · Ingresos y Egresos · Múltiples archivos</p>
            <p className="text-xs text-blue-500 mt-2">
              Detecta automáticamente: tipo (ingreso/egreso), IVA, ISR retenido 1.25%, régimen fiscal
            </p>
          </div>

          {uploadMsg && (
            <Card className="p-4">
              <p className="text-xs font-semibold text-gray-600 mb-2">Resultado de carga:</p>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">{uploadMsg}</pre>
            </Card>
          )}

          <Card className="p-5 bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Qué detecta el parser CFDI</h3>
            <ul className="space-y-1.5 text-sm text-gray-500">
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />Tipo de CFDI: Ingreso (I) o Egreso (E)</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />IVA trasladado 16% del nodo Traslados</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />ISR retenido 1.25% (impuesto 001 en Retenciones) — RESICO Art. 113-J</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />IVA retenido (impuesto 002 en Retenciones)</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />Régimen fiscal del emisor (621=RESICO PF, 626=RESICO PM, 601=General)</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />UUID CFDI — previene duplicados automáticamente</li>
              <li className="flex items-start gap-2"><CheckCircle size={14} className="text-green-500 mt-0.5 flex-shrink-0" />CFDI 4.0 y 3.3 soportados</li>
            </ul>
          </Card>
        </div>
      )}
    </div>
  )
}

function TipoPagoBadge({ tipo }: { tipo: TipoPago }) {
  const cfg = TIPO_PAGO_CONFIG[tipo] || TIPO_PAGO_CONFIG.pendiente
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${cfg.color}`}>
      {cfg.icon}{cfg.label}
    </span>
  )
}

function TablaFacturas({
  titulo, facturas, columnas, onChangePago,
}: {
  titulo: string
  facturas: DetalleFactura[]
  columnas: string[]
  onChangePago: (id: string, tipo: TipoPago) => Promise<void>
}) {
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  async function handleChange(uuid: string, tp: TipoPago) {
    if (!uuid) return
    setUpdatingId(uuid)
    await onChangePago(uuid, tp)
    setUpdatingId(null)
  }

  if (facturas.length === 0)
    return <Card className="p-6 text-center text-gray-400 text-sm">{titulo} — Sin datos</Card>

  return (
    <Card>
      <div className="px-4 pt-4 pb-2 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-700">{titulo} ({facturas.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-50 text-left">
              <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase">Fecha</th>
              {columnas.includes('nombre_receptor') && <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase">Cliente</th>}
              {columnas.includes('nombre_emisor') && <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase">Proveedor</th>}
              <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase text-right">Subtotal</th>
              <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase text-right">IVA</th>
              {columnas.includes('iva_retenido') && <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase text-right">IVA Ret.</th>}
              {columnas.includes('isr_retenido') && <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase text-right">ISR Ret.</th>}
              <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase text-right">Total</th>
              {columnas.includes('tipo_pago') && <th className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase">Estado pago</th>}
            </tr>
          </thead>
          <tbody>
            {facturas.map((f, i) => (
              <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50">
                <td className="px-4 py-2.5 text-gray-400">{f.fecha}</td>
                {columnas.includes('nombre_receptor') && <td className="px-4 py-2.5 font-medium text-gray-800">{f.nombre_receptor || f.rfc_receptor || '—'}</td>}
                {columnas.includes('nombre_emisor') && <td className="px-4 py-2.5 font-medium text-gray-800">{f.nombre_emisor || f.rfc_emisor || '—'}</td>}
                <td className="px-4 py-2.5 text-right">{mxn(f.subtotal)}</td>
                <td className="px-4 py-2.5 text-right">{mxn(f.iva)}</td>
                {columnas.includes('iva_retenido') && <td className="px-4 py-2.5 text-right text-amber-600">{f.iva_retenido ? mxn(f.iva_retenido) : '—'}</td>}
                {columnas.includes('isr_retenido') && <td className="px-4 py-2.5 text-right text-blue-600 font-medium">{f.isr_retenido ? mxn(f.isr_retenido) : '—'}</td>}
                <td className="px-4 py-2.5 text-right font-semibold">{mxn(f.total)}</td>
                {columnas.includes('tipo_pago') && (
                  <td className="px-4 py-2.5">
                    <select
                      value={f.tipo_pago || 'pendiente'}
                      onChange={e => handleChange(f.uuid || '', e.target.value as TipoPago)}
                      disabled={updatingId === f.uuid}
                      className="text-xs border border-gray-200 rounded px-2 py-1 focus:outline-none disabled:opacity-50"
                    >
                      <option value="prepagado">Prepagado</option>
                      <option value="pendiente">Pendiente</option>
                      <option value="pagado">Pagado</option>
                      <option value="cancelado">Cancelado</option>
                    </select>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
