'use client'

import { useEffect, useState } from 'react'
import { api, MVE, SemaforoResult } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Package, Plus, CheckCircle, AlertTriangle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

const fmt = (v: number, moneda = 'MXN') =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: moneda }).format(v)

const INCOTERMS = ['EXW','FCA','FAS','FOB','CFR','CIF','CPT','CIP','DAP','DPU','DDP']
const METODOS = [
  { v: 1, label: '1 — Valor de transacción (más común)' },
  { v: 2, label: '2 — Mercancías idénticas' },
  { v: 3, label: '3 — Mercancías similares' },
  { v: 4, label: '4 — Valor deductivo' },
  { v: 5, label: '5 — Valor reconstruido' },
  { v: 6, label: '6 — Último recurso' },
]

// ── Semáforo badge ─────────────────────────────────────────────────────────

function SemaforoBadge({ semaforo }: { semaforo?: string }) {
  if (!semaforo) return <span className="text-xs text-gray-400">Sin validar</span>
  if (semaforo === 'green')
    return <span className="flex items-center gap-1 text-xs text-green-600 font-semibold"><CheckCircle size={14}/>LISTA</span>
  if (semaforo === 'yellow')
    return <span className="flex items-center gap-1 text-xs text-yellow-600 font-semibold"><AlertTriangle size={14}/>ADVERTENCIAS</span>
  return <span className="flex items-center gap-1 text-xs text-red-600 font-semibold"><XCircle size={14}/>BLOQUEADA</span>
}

// ── Modal: Semáforo detalle ────────────────────────────────────────────────

function SemaforoModal({ result, onClose }: { result: SemaforoResult; onClose: () => void }) {
  const bg = result.semaforo === 'green' ? 'border-green-400 bg-green-50'
           : result.semaforo === 'yellow' ? 'border-yellow-400 bg-yellow-50'
           : 'border-red-400 bg-red-50'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className={`p-5 border-b-4 rounded-t-xl ${bg}`}>
          <p className="font-bold text-lg">{result.resumen}</p>
        </div>

        <div className="p-5 space-y-3">
          {result.errores.length === 0 ? (
            <p className="text-green-700 text-sm">✅ Todos los requisitos RGCE cumplidos.</p>
          ) : (
            result.errores.map((e, i) => (
              <div key={i}
                className={`p-3 rounded-lg border text-sm ${e.nivel === 'red' ? 'border-red-200 bg-red-50' : 'border-yellow-200 bg-yellow-50'}`}
              >
                <div className="flex items-center gap-2 font-semibold mb-1">
                  {e.nivel === 'red' ? <XCircle size={14} className="text-red-500"/> : <AlertTriangle size={14} className="text-yellow-500"/>}
                  <span className="font-mono text-xs text-gray-500">{e.codigo}</span>
                  {e.campo && <span className="text-xs text-gray-400">→ {e.campo}</span>}
                </div>
                <p className="text-gray-700">{e.mensaje}</p>
              </div>
            ))
          )}
        </div>

        <div className="px-5 pb-5">
          <button onClick={onClose}
            className="w-full py-2 bg-gray-900 text-white rounded-lg text-sm hover:bg-gray-700">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Formulario nueva MVE ───────────────────────────────────────────────────

const EMPTY_FORM = {
  proveedor_nombre: '', proveedor_pais: '', proveedor_tax_id: '',
  numero_factura: '', fecha_factura: '', descripcion_mercancias: '',
  fraccion_arancelaria: '', cantidad: 1, unidad_medida: 'PZA',
  incoterm: 'FOB', valor_factura: '', moneda: 'USD',
  tipo_cambio: '', flete: 0, seguro: 0, otros_cargos: 0,
  tasa_igi: 0, metodo_valoracion: 1, justificacion_metodo: '',
  hay_vinculacion: false, justificacion_vinculacion: '', notas: '',
}

function NuevaMVEForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState<typeof EMPTY_FORM>({...EMPTY_FORM})
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const set = (k: string, v: unknown) => setForm(f => ({...f, [k]: v}))

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setErr('')
    try {
      await api.post('/mve', {
        ...form,
        cantidad: Number(form.cantidad),
        valor_factura: Number(form.valor_factura),
        tipo_cambio: form.tipo_cambio ? Number(form.tipo_cambio) : undefined,
        flete: Number(form.flete),
        seguro: Number(form.seguro),
        otros_cargos: Number(form.otros_cargos),
        tasa_igi: Number(form.tasa_igi),
        metodo_valoracion: Number(form.metodo_valoracion),
      })
      setForm({...EMPTY_FORM})
      onCreated()
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : String(e))
    } finally {
      setSaving(false)
    }
  }

  const inp = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
  const lbl = "block text-xs text-gray-500 mb-1 font-medium"

  return (
    <Card className="border-2 border-dashed border-brand-300">
      <form onSubmit={submit} className="space-y-5">
        <h3 className="font-semibold text-gray-900">Nueva Manifestación de Valor</h3>

        {/* Proveedor */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <label className={lbl}>Nombre del proveedor *</label>
            <input className={inp} required value={form.proveedor_nombre}
              onChange={e => set('proveedor_nombre', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>País de origen *</label>
            <input className={inp} placeholder="ej: China, USA" required value={form.proveedor_pais}
              onChange={e => set('proveedor_pais', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Tax ID / RFC del proveedor</label>
            <input className={inp} value={form.proveedor_tax_id}
              onChange={e => set('proveedor_tax_id', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>No. Factura comercial *</label>
            <input className={inp} required value={form.numero_factura}
              onChange={e => set('numero_factura', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Fecha factura *</label>
            <input type="date" className={inp} required value={form.fecha_factura}
              onChange={e => set('fecha_factura', e.target.value)} />
          </div>
        </div>

        {/* Mercancía */}
        <div>
          <label className={lbl}>Descripción de la mercancía * (mín. 10 caracteres, sé específico)</label>
          <textarea className={inp} rows={2} required minLength={10} value={form.descripcion_mercancias}
            placeholder="ej: Válvulas de bola de acero inoxidable 316L, 2 pulgadas, ANSI 150"
            onChange={e => set('descripcion_mercancias', e.target.value)} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className={lbl}>Fracción arancelaria *</label>
            <input className={inp} placeholder="8481.80.99.99" value={form.fraccion_arancelaria}
              onChange={e => set('fraccion_arancelaria', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Cantidad *</label>
            <input type="number" min="0.001" step="any" className={inp} required value={form.cantidad}
              onChange={e => set('cantidad', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Unidad de medida *</label>
            <input className={inp} placeholder="PZA, KG, LT…" required value={form.unidad_medida}
              onChange={e => set('unidad_medida', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>INCOTERM *</label>
            <select className={inp} value={form.incoterm} onChange={e => set('incoterm', e.target.value)}>
              {INCOTERMS.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
        </div>

        {/* Valores */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className={lbl}>Valor factura * (en moneda de origen)</label>
            <input type="number" min="0.01" step="any" className={inp} required value={form.valor_factura}
              onChange={e => set('valor_factura', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Moneda</label>
            <select className={inp} value={form.moneda} onChange={e => set('moneda', e.target.value)}>
              {['USD','EUR','MXN','CNY','GBP'].map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className={lbl}>Tipo de cambio (dejar vacío = DOF del día)</label>
            <input type="number" step="any" className={inp} value={form.tipo_cambio}
              placeholder="17.50"
              onChange={e => set('tipo_cambio', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Tasa IGI %</label>
            <input type="number" min="0" step="any" className={inp} value={form.tasa_igi}
              onChange={e => set('tasa_igi', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Flete (USD)</label>
            <input type="number" min="0" step="any" className={inp} value={form.flete}
              onChange={e => set('flete', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Seguro (USD)</label>
            <input type="number" min="0" step="any" className={inp} value={form.seguro}
              onChange={e => set('seguro', e.target.value)} />
          </div>
          <div>
            <label className={lbl}>Otros cargos (USD)</label>
            <input type="number" min="0" step="any" className={inp} value={form.otros_cargos}
              onChange={e => set('otros_cargos', e.target.value)} />
          </div>
        </div>

        {/* Método valoración */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={lbl}>Método de valoración (Art. 45-50 LA) *</label>
            <select className={inp} value={form.metodo_valoracion}
              onChange={e => set('metodo_valoracion', Number(e.target.value))}>
              {METODOS.map(m => <option key={m.v} value={m.v}>{m.label}</option>)}
            </select>
          </div>
          {form.metodo_valoracion > 1 && (
            <div>
              <label className={lbl}>Justificación método (obligatoria para Método 2-6)</label>
              <input className={inp} value={form.justificacion_metodo}
                placeholder="¿Por qué no aplica Método 1?"
                onChange={e => set('justificacion_metodo', e.target.value)} />
            </div>
          )}
        </div>

        {/* Vinculación */}
        <div className="flex items-start gap-3">
          <input type="checkbox" id="vinc" checked={form.hay_vinculacion}
            onChange={e => set('hay_vinculacion', e.target.checked)}
            className="mt-0.5" />
          <div className="flex-1">
            <label htmlFor="vinc" className="text-sm text-gray-700 cursor-pointer">
              Existe vinculación entre comprador y vendedor (Art. 64 LA)
            </label>
            {form.hay_vinculacion && (
              <div className="mt-2">
                <label className={lbl}>Justificación de vinculación</label>
                <textarea className={inp} rows={2} value={form.justificacion_vinculacion}
                  placeholder="Justifica que la vinculación no influyó en el precio…"
                  onChange={e => set('justificacion_vinculacion', e.target.value)} />
              </div>
            )}
          </div>
        </div>

        <div>
          <label className={lbl}>Notas internas</label>
          <input className={inp} value={form.notas}
            onChange={e => set('notas', e.target.value)} />
        </div>

        {err && <p className="text-red-500 text-sm">{err}</p>}

        <button type="submit" disabled={saving}
          className="w-full py-2.5 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 disabled:opacity-50">
          {saving ? 'Guardando…' : 'Crear MVE y validar semáforo'}
        </button>
      </form>
    </Card>
  )
}

// ── Página principal ───────────────────────────────────────────────────────

export default function MVEPage() {
  const [mves, setMves]         = useState<MVE[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [showForm, setShowForm] = useState(false)
  const [semaforoModal, setSemaforoModal] = useState<SemaforoResult | null>(null)
  const [validating, setValidating] = useState<string | null>(null)
  const [presenting, setPresenting] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  function load() {
    setLoading(true)
    api.get<MVE[]>('/mve?limit=50')
      .then(setMves)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function validar(id: string) {
    setValidating(id)
    try {
      const r = await api.post<SemaforoResult>(`/mve/${id}/validar`, {})
      setSemaforoModal(r)
      load()
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : String(e))
    } finally {
      setValidating(null)
    }
  }

  async function presentar(id: string) {
    setPresenting(id)
    try {
      await api.patch(`/mve/${id}/presentar`)
      load()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      try {
        const detail = JSON.parse(msg)
        if (detail?.error === 'MVE_BLOQUEADA_SEMAFORO_ROJO') {
          setSemaforoModal({
            semaforo: 'red',
            errores: detail.errores_criticos || [],
            puede_presentar: false,
            resumen: detail.resumen || detail.mensaje,
            total_errores: (detail.errores_criticos || []).length,
            total_advertencias: 0,
          })
          return
        }
      } catch {}
      alert(msg)
    } finally {
      setPresenting(null)
    }
  }

  const borradores  = mves.filter(m => m.estado === 'borrador' || m.estado === 'lista').length
  const presentadas = mves.filter(m => m.estado === 'presentada').length

  return (
    <div className="space-y-6">
      {semaforoModal && (
        <SemaforoModal result={semaforoModal} onClose={() => setSemaforoModal(null)} />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Manifestación de Valor (MVE)</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {borradores} pendientes · {presentadas} presentadas · Obligatorio 1 abril 2026
          </p>
        </div>
        <button
          onClick={() => setShowForm(v => !v)}
          className="flex items-center gap-2 bg-brand-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-brand-700"
        >
          <Plus size={16} />
          Nueva MVE
        </button>
      </div>

      {showForm && (
        <NuevaMVEForm onCreated={() => { setShowForm(false); load() }} />
      )}

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      {/* Tabla */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wide">
                <th className="text-left px-4 py-3">Proveedor</th>
                <th className="text-left px-4 py-3">Factura</th>
                <th className="text-left px-4 py-3">Mercancía</th>
                <th className="text-center px-4 py-3">Incoterm</th>
                <th className="text-right px-4 py-3">Valor factura</th>
                <th className="text-right px-4 py-3">Valor aduana</th>
                <th className="text-center px-4 py-3">Semáforo</th>
                <th className="text-center px-4 py-3">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {mves.map(m => (
                <>
                  <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900 truncate max-w-[140px]">{m.proveedor_nombre}</div>
                      <div className="text-xs text-gray-400">{m.proveedor_pais}</div>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-600">
                      <div>{m.numero_factura}</div>
                      <div className="text-gray-400">{m.fecha_factura?.slice(0,10)}</div>
                    </td>
                    <td className="px-4 py-3 max-w-[160px]">
                      <div className="truncate text-gray-700">{m.descripcion_mercancias}</div>
                      {m.fraccion_arancelaria && (
                        <div className="text-xs font-mono text-gray-400">{m.fraccion_arancelaria}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center font-semibold text-gray-700">{m.incoterm}</td>
                    <td className="px-4 py-3 text-right">{fmt(m.valor_factura, m.moneda)}</td>
                    <td className="px-4 py-3 text-right font-semibold">{fmt(m.valor_en_aduana)}</td>
                    <td className="px-4 py-3 text-center">
                      <SemaforoBadge semaforo={m.semaforo} />
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        m.estado === 'presentada' ? 'bg-blue-100 text-blue-700' :
                        m.estado === 'pagada'     ? 'bg-green-100 text-green-700' :
                        m.estado === 'lista'      ? 'bg-purple-100 text-purple-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {m.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => validar(m.id)}
                          disabled={validating === m.id}
                          className="text-xs bg-gray-100 text-gray-700 hover:bg-gray-200 px-2 py-1 rounded"
                          title="Validar semáforo"
                        >
                          {validating === m.id ? '…' : 'Validar'}
                        </button>
                        {(m.estado === 'lista' || m.estado === 'borrador') && (
                          <button
                            onClick={() => presentar(m.id)}
                            disabled={presenting === m.id}
                            className={`text-xs px-2 py-1 rounded ${
                              m.semaforo === 'red' || !m.semaforo
                                ? 'bg-red-100 text-red-400 cursor-not-allowed'
                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                            }`}
                            title={m.semaforo === 'red' ? 'Corrige los errores antes de presentar' : 'Presentar en VUCEM'}
                          >
                            {presenting === m.id ? '…' : 'Presentar'}
                          </button>
                        )}
                        <button
                          onClick={() => setExpandedId(expandedId === m.id ? null : m.id)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          {expandedId === m.id ? <ChevronUp size={14}/> : <ChevronDown size={14}/>}
                        </button>
                      </div>
                    </td>
                  </tr>
                  {expandedId === m.id && (
                    <tr key={`${m.id}-detail`} className="bg-gray-50">
                      <td colSpan={9} className="px-4 pb-4 pt-2">
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                          <div><span className="text-gray-400">Método valoración:</span> <span className="font-medium">{m.metodo_valoracion}</span></div>
                          <div><span className="text-gray-400">Tipo cambio:</span> <span className="font-medium">${m.tipo_cambio} MXN/USD</span></div>
                          <div><span className="text-gray-400">IGI ({m.tasa_igi}%):</span> <span className="font-medium">{fmt(m.igi)}</span></div>
                          <div><span className="text-gray-400">IVA importación:</span> <span className="font-medium">{fmt(m.iva_importacion)}</span></div>
                          <div><span className="text-gray-400">DTA:</span> <span className="font-medium">{fmt(m.dta)}</span></div>
                          <div><span className="text-gray-400">Flete:</span> <span className="font-medium">{fmt(m.flete, m.moneda)}</span></div>
                          <div><span className="text-gray-400">Seguro:</span> <span className="font-medium">{fmt(m.seguro, m.moneda)}</span></div>
                          <div><span className="text-gray-400">Vinculación:</span> <span className="font-medium">{m.hay_vinculacion ? 'Sí' : 'No'}</span></div>
                          {m.pedimento_numero && <div className="col-span-2"><span className="text-gray-400">Pedimento:</span> <span className="font-mono font-medium">{m.pedimento_numero}</span></div>}
                          {m.folio_vucem && <div className="col-span-2"><span className="text-gray-400">Folio VUCEM:</span> <span className="font-mono font-medium">{m.folio_vucem}</span></div>}
                          {m.notas && <div className="col-span-4"><span className="text-gray-400">Notas:</span> {m.notas}</div>}
                          {m.semaforo_errores && m.semaforo_errores.length > 0 && (
                            <div className="col-span-4 mt-2 space-y-1">
                              <p className="text-gray-500 font-medium">Últimas observaciones del semáforo:</p>
                              {m.semaforo_errores.map((e, i) => (
                                <div key={i} className={`flex items-start gap-2 p-2 rounded text-xs ${e.nivel === 'red' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'}`}>
                                  <span className="font-mono shrink-0">{e.codigo}</span>
                                  <span>{e.mensaje}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
              {!loading && mves.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center text-gray-400 py-10">
                    <Package size={36} className="mx-auto mb-3 opacity-30" />
                    <p className="font-medium">Sin MVEs registradas</p>
                    <p className="text-xs mt-1">Crea la primera con el botón &quot;Nueva MVE&quot;</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Aviso legal */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-xs text-amber-800">
        <p className="font-semibold mb-1">⚠️ Obligatorio a partir del 1 de abril de 2026</p>
        <p>La Manifestación de Valor digital en VUCEM es obligatoria para todas las importaciones/exportaciones.
           Presentar con errores genera multa del 70-100% del valor de las contribuciones (Art. 197 Ley Aduanera).
           El semáforo valida contra RGCE 2025 antes de permitir la presentación.</p>
      </div>
    </div>
  )
}
