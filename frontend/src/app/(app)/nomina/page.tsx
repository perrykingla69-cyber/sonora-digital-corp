'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import {
  Users, Plus, ChevronDown, ChevronUp, Edit2, UserMinus,
  Calculator, CheckCircle, AlertTriangle, Building2,
} from 'lucide-react'

const mxn = (v: number) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(v ?? 0)

interface Empleado {
  id: string; nombre: string; curp?: string; rfc?: string; nss?: string
  numero_empleado?: string; puesto?: string; departamento?: string
  tipo_contrato: string; regimen_imss?: string; fecha_ingreso?: string
  tipo_salario?: string; salario_mensual: number; salario_diario: number
  salario_integrado: number; factor_integracion: number; prima_riesgo_trabajo: number
  tiene_infonavit: boolean; numero_credito_infonavit?: string
  descuento_infonavit: number; tipo_descuento_infonavit?: string
  banco?: string; clabe?: string; caja_ahorro_pct: number
  prestamos: number; vales_despensa: number; notas?: string; activo: boolean
}

interface Calculo {
  salario_neto: number; costo_total_empresa: number
  percepciones: { salario_bruto: number; vales_despensa: number; total: number }
  deducciones_trabajador: { imss: number; isr_neto: number; subsidio_empleo: number; infonavit_credito: number; caja_ahorro: number; prestamos: number; total: number }
  cuotas_patronales: { imss_patron: number; infonavit_patron: number; total: number }
  prestaciones_anuales: { aguinaldo: number; prima_vacacional: number; ptu_estimado: number }
}

const EMPTY = {
  nombre: '', curp: '', rfc: '', nss: '', numero_empleado: '', puesto: '', departamento: '',
  tipo_contrato: 'indefinido', regimen_imss: 'sueldos_salarios', tipo_salario: 'mensual',
  salario_mensual: 0, factor_integracion: 1.0452, prima_riesgo_trabajo: 0.5,
  tiene_infonavit: false, descuento_infonavit: 0, tipo_descuento_infonavit: 'vsm',
  banco: '', clabe: '', caja_ahorro_pct: 0, prestamos: 0, vales_despensa: 0, notas: '',
}

function EmpleadoForm({ initial, onSave, onCancel }: {
  initial?: Partial<Empleado>; onSave: (d: typeof EMPTY) => void; onCancel: () => void
}) {
  const [form, setForm] = useState({ ...EMPTY, ...initial })
  const s = (k: string, v: unknown) => setForm(f => ({ ...f, [k]: v }))
  const inp = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
  const lbl = "block text-xs font-medium text-gray-500 mb-1"

  return (
    <div className="bg-white rounded-xl border-2 border-brand-200 p-6 space-y-6">
      <h3 className="font-bold text-gray-900">{initial?.id ? 'Editar empleado' : 'Nuevo empleado'}</h3>

      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Datos personales</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2"><label className={lbl}>Nombre completo *</label><input className={inp} required value={form.nombre} onChange={e => s('nombre', e.target.value)} /></div>
          <div><label className={lbl}>No. Empleado</label><input className={inp} value={form.numero_empleado} onChange={e => s('numero_empleado', e.target.value)} /></div>
          <div><label className={lbl}>CURP (18 chars)</label><input className={inp} maxLength={18} value={form.curp} onChange={e => s('curp', e.target.value.toUpperCase())} /></div>
          <div><label className={lbl}>RFC</label><input className={inp} maxLength={13} value={form.rfc} onChange={e => s('rfc', e.target.value.toUpperCase())} /></div>
          <div><label className={lbl}>NSS IMSS (11 dígitos)</label><input className={inp} maxLength={11} value={form.nss} onChange={e => s('nss', e.target.value)} /></div>
        </div>
      </div>

      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Datos laborales</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div><label className={lbl}>Puesto</label><input className={inp} value={form.puesto} onChange={e => s('puesto', e.target.value)} /></div>
          <div><label className={lbl}>Departamento</label><input className={inp} value={form.departamento} onChange={e => s('departamento', e.target.value)} /></div>
          <div>
            <label className={lbl}>Tipo contrato</label>
            <select className={inp} value={form.tipo_contrato} onChange={e => s('tipo_contrato', e.target.value)}>
              <option value="indefinido">Indefinido</option>
              <option value="temporal">Temporal</option>
              <option value="obra">Obra determinada</option>
              <option value="honorarios">Honorarios</option>
            </select>
          </div>
          <div>
            <label className={lbl}>Régimen IMSS</label>
            <select className={inp} value={form.regimen_imss} onChange={e => s('regimen_imss', e.target.value)}>
              <option value="sueldos_salarios">Sueldos y Salarios</option>
              <option value="honorarios">Honorarios Asimilados</option>
              <option value="asimilados">Asimilados a Salarios</option>
            </select>
          </div>
          <div>
            <label className={lbl}>Prima riesgo trabajo %</label>
            <input type="number" step="0.001" min="0.005" className={inp} value={(form.prima_riesgo_trabajo * 100).toFixed(3)} onChange={e => s('prima_riesgo_trabajo', Number(e.target.value) / 100)} />
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Salario</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className={lbl}>Tipo salario</label>
            <select className={inp} value={form.tipo_salario} onChange={e => s('tipo_salario', e.target.value)}>
              <option value="mensual">Mensual</option>
              <option value="quincenal">Quincenal</option>
              <option value="semanal">Semanal</option>
              <option value="diario">Diario</option>
            </select>
          </div>
          <div><label className={lbl}>Salario mensual $MXN *</label><input type="number" min="0" step="any" className={inp} value={form.salario_mensual || ''} onChange={e => s('salario_mensual', Number(e.target.value))} /></div>
          <div>
            <label className={lbl}>Factor integración</label>
            <input type="number" step="0.0001" min="1.0452" className={inp} value={form.factor_integracion} onChange={e => s('factor_integracion', Number(e.target.value))} />
            <p className="text-xs text-gray-400 mt-0.5">Mín. 1.0452</p>
          </div>
          <div><label className={lbl}>Vales despensa $MXN</label><input type="number" min="0" step="any" className={inp} value={form.vales_despensa || ''} onChange={e => s('vales_despensa', Number(e.target.value))} /></div>
        </div>
      </div>

      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">INFONAVIT</p>
        <div className="flex items-center gap-2 mb-3">
          <input type="checkbox" id="inf" checked={form.tiene_infonavit} onChange={e => s('tiene_infonavit', e.target.checked)} />
          <label htmlFor="inf" className="text-sm text-gray-700">Tiene crédito INFONAVIT activo</label>
        </div>
        {form.tiene_infonavit && (
          <div className="grid grid-cols-3 gap-4">
            <div><label className={lbl}>No. Crédito</label><input className={inp} value={form.numero_credito_infonavit} onChange={e => s('numero_credito_infonavit', e.target.value)} /></div>
            <div>
              <label className={lbl}>Tipo descuento</label>
              <select className={inp} value={form.tipo_descuento_infonavit} onChange={e => s('tipo_descuento_infonavit', e.target.value)}>
                <option value="vsm">VSM</option>
                <option value="porcentaje">Porcentaje %</option>
                <option value="fijo">Monto fijo $</option>
              </select>
            </div>
            <div><label className={lbl}>Importe/Factor</label><input type="number" step="any" className={inp} value={form.descuento_infonavit || ''} onChange={e => s('descuento_infonavit', Number(e.target.value))} /></div>
          </div>
        )}
      </div>

      <div>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Otras deducciones y bancario</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div><label className={lbl}>Caja ahorro %</label><input type="number" min="0" max="100" step="any" className={inp} value={form.caja_ahorro_pct || ''} onChange={e => s('caja_ahorro_pct', Number(e.target.value))} /></div>
          <div><label className={lbl}>Préstamos $MXN</label><input type="number" min="0" step="any" className={inp} value={form.prestamos || ''} onChange={e => s('prestamos', Number(e.target.value))} /></div>
          <div><label className={lbl}>Banco</label><input className={inp} placeholder="BBVA, Banorte..." value={form.banco} onChange={e => s('banco', e.target.value)} /></div>
          <div><label className={lbl}>CLABE (18 dígitos)</label><input className={inp} maxLength={18} value={form.clabe} onChange={e => s('clabe', e.target.value)} /></div>
        </div>
      </div>

      <div><label className={lbl}>Notas</label><textarea className={inp} rows={2} value={form.notas} onChange={e => s('notas', e.target.value)} /></div>

      <div className="flex gap-3">
        <button type="button" onClick={() => onSave(form)} className="flex-1 bg-brand-600 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-brand-700">
          {initial?.id ? 'Guardar cambios' : 'Crear empleado'}
        </button>
        <button type="button" onClick={onCancel} className="px-5 bg-gray-100 text-gray-700 rounded-lg py-2.5 text-sm hover:bg-gray-200">Cancelar</button>
      </div>
    </div>
  )
}

function CalculoPanel({ eid, nombre }: { eid: string; nombre: string }) {
  const [data, setData] = useState<Calculo | null>(null)
  const [loading, setLoading] = useState(false)
  const [dias, setDias] = useState(30)

  async function calcular() {
    setLoading(true)
    try { setData(await api.get<Calculo>(`/nomina/calculos/${eid}?dias=${dias}`)) }
    catch (e: unknown) { alert(e instanceof Error ? e.message : 'Error') }
    finally { setLoading(false) }
  }

  return (
    <div className="mt-3 bg-indigo-50 rounded-xl p-4 border border-indigo-100">
      <div className="flex items-center gap-3 mb-3">
        <Calculator size={15} className="text-indigo-600" />
        <span className="text-sm font-semibold text-indigo-700">Simulador — {nombre}</span>
        <input type="number" min="1" max="31" value={dias} onChange={e => setDias(Number(e.target.value))} className="w-14 text-sm border border-indigo-200 rounded px-2 py-1 ml-2" />
        <span className="text-xs text-indigo-500">días</span>
        <button onClick={calcular} disabled={loading} className="ml-auto text-xs bg-indigo-600 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {loading ? '...' : 'Calcular'}
        </button>
      </div>
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-white rounded-lg p-3"><p className="text-gray-400 mb-1">Salario bruto</p><p className="font-bold">{mxn(data.percepciones.salario_bruto)}</p></div>
          <div className="bg-white rounded-lg p-3"><p className="text-gray-400 mb-1">IMSS obrero</p><p className="font-bold text-red-600">-{mxn(data.deducciones_trabajador.imss)}</p></div>
          <div className="bg-white rounded-lg p-3"><p className="text-gray-400 mb-1">ISR neto</p><p className="font-bold text-red-600">-{mxn(data.deducciones_trabajador.isr_neto)}</p><p className="text-gray-400">Subsidio: {mxn(data.deducciones_trabajador.subsidio_empleo)}</p></div>
          <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-200"><p className="text-emerald-600 mb-1">Neto a pagar</p><p className="font-bold text-emerald-700 text-sm">{mxn(data.salario_neto)}</p></div>
          <div className="bg-white rounded-lg p-3"><p className="text-gray-400 mb-1">IMSS patrón</p><p className="font-bold text-orange-600">{mxn(data.cuotas_patronales.imss_patron)}</p></div>
          <div className="bg-white rounded-lg p-3"><p className="text-gray-400 mb-1">INFONAVIT patrón</p><p className="font-bold text-orange-600">{mxn(data.cuotas_patronales.infonavit_patron)}</p></div>
          <div className="col-span-2 bg-orange-50 rounded-lg p-3 border border-orange-200"><p className="text-orange-600 mb-1">Costo total empresa</p><p className="font-bold text-orange-700 text-sm">{mxn(data.costo_total_empresa)}</p></div>
          <div className="col-span-4 grid grid-cols-3 gap-2">
            <div className="bg-white rounded p-2 text-center"><p className="text-gray-400">Aguinaldo anual</p><p className="font-semibold">{mxn(data.prestaciones_anuales.aguinaldo)}</p></div>
            <div className="bg-white rounded p-2 text-center"><p className="text-gray-400">Prima vacacional</p><p className="font-semibold">{mxn(data.prestaciones_anuales.prima_vacacional)}</p></div>
            <div className="bg-white rounded p-2 text-center"><p className="text-gray-400">PTU estimado</p><p className="font-semibold">{mxn(data.prestaciones_anuales.ptu_estimado)}</p></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function NominaPage() {
  const [empleados, setEmpleados] = useState<Empleado[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editando, setEditando] = useState<Empleado | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)

  function load() {
    setLoading(true)
    api.get<Empleado[]>('/empleados').then(setEmpleados).catch(e => setError(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  async function guardar(data: typeof EMPTY) {
    try {
      if (editando?.id) await api.patch(`/empleados/${editando.id}`, data)
      else await api.post('/empleados', data)
      setShowForm(false); setEditando(null); load()
    } catch (e: unknown) { alert(e instanceof Error ? e.message : 'Error') }
  }

  async function darBaja(e: Empleado) {
    if (!confirm(`¿Dar de baja a ${e.nombre}?`)) return
    try { await api.delete(`/empleados/${e.id}`); load() }
    catch (err: unknown) { alert(err instanceof Error ? err.message : 'Error') }
  }

  const totalNomina = empleados.reduce((s, e) => s + (e.salario_mensual || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><Users size={24} />Nómina</h1>
          <p className="text-sm text-gray-500 mt-0.5">{empleados.length} activos · IMSS · INFONAVIT · ISR · PTU</p>
        </div>
        <button onClick={() => { setEditando(null); setShowForm(v => !v) }} className="flex items-center gap-2 bg-brand-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-brand-700">
          <Plus size={16} /> Nuevo empleado
        </button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card className="p-4"><p className="text-xs text-gray-400 mb-1">Empleados activos</p><p className="text-2xl font-bold">{empleados.length}</p></Card>
        <Card className="p-4"><p className="text-xs text-gray-400 mb-1">Nómina mensual bruta</p><p className="text-xl font-bold text-brand-600">{mxn(totalNomina)}</p></Card>
        <Card className="p-4"><p className="text-xs text-gray-400 mb-1">Costo empresa est. (+35%)</p><p className="text-xl font-bold text-orange-600">{mxn(totalNomina * 1.35)}</p></Card>
      </div>

      {(showForm || editando) && (
        <EmpleadoForm initial={editando || undefined} onSave={guardar} onCancel={() => { setShowForm(false); setEditando(null) }} />
      )}

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      <Card>
        {empleados.length === 0 && !loading ? (
          <div className="text-center py-12 text-gray-400">
            <Users size={40} className="mx-auto mb-3 opacity-30" />
            <p className="font-medium">Sin empleados registrados</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {empleados.map(e => (
              <div key={e.id}>
                <div className="px-5 py-4 flex items-center gap-4 hover:bg-gray-50">
                  <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
                    <span className="text-brand-700 font-bold text-sm">{e.nombre.slice(0, 2).toUpperCase()}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900">{e.nombre}</p>
                    <p className="text-xs text-gray-400">{e.puesto || '—'} · {e.departamento || 'Sin depto'} · {e.tipo_contrato}</p>
                  </div>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-semibold">{mxn(e.salario_mensual)}/mes</p>
                    <p className="text-xs text-gray-400">Integrado: {mxn(e.salario_integrado)}/día</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {e.nss ? <CheckCircle size={13} className="text-emerald-500" aria-label="NSS OK" /> : <AlertTriangle size={13} className="text-amber-400" aria-label="Falta NSS" />}
                    {e.clabe ? <CheckCircle size={13} className="text-emerald-500" aria-label="CLABE OK" /> : <AlertTriangle size={13} className="text-amber-400" aria-label="Falta CLABE" />}
                    {e.curp ? <CheckCircle size={13} className="text-emerald-500" aria-label="CURP OK" /> : <AlertTriangle size={13} className="text-amber-400" aria-label="Falta CURP" />}
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => { setEditando(e); setShowForm(false) }} className="p-1.5 text-gray-400 hover:text-brand-600 rounded"><Edit2 size={14} /></button>
                    <button onClick={() => darBaja(e)} className="p-1.5 text-gray-400 hover:text-red-500 rounded"><UserMinus size={14} /></button>
                    <button onClick={() => setExpandedId(expandedId === e.id ? null : e.id)} className="p-1.5 text-gray-400 hover:text-gray-600 rounded">
                      {expandedId === e.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  </div>
                </div>
                {expandedId === e.id && (
                  <div className="px-5 pb-5">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs mb-3 text-gray-700">
                      <div><span className="text-gray-400">RFC: </span><span className="font-mono">{e.rfc || '—'}</span></div>
                      <div><span className="text-gray-400">NSS: </span><span className="font-mono">{e.nss || '—'}</span></div>
                      <div><span className="text-gray-400">CURP: </span><span className="font-mono text-xs">{e.curp || '—'}</span></div>
                      <div><span className="text-gray-400">Sal. diario: </span><b>{mxn(e.salario_diario)}</b></div>
                      <div><span className="text-gray-400">Sal. integrado: </span><b>{mxn(e.salario_integrado)}</b></div>
                      <div><span className="text-gray-400">Factor int.: </span><b>{e.factor_integracion}</b></div>
                      <div><span className="text-gray-400">Banco: </span>{e.banco || '—'}</div>
                      <div><span className="text-gray-400">CLABE: </span><span className="font-mono">{e.clabe || '—'}</span></div>
                      {e.tiene_infonavit && <div className="col-span-2"><span className="text-gray-400">INFONAVIT: </span>{e.numero_credito_infonavit} — {e.descuento_infonavit} {e.tipo_descuento_infonavit}</div>}
                      {e.notas && <div className="col-span-4 text-gray-400 italic">{e.notas}</div>}
                    </div>
                    <CalculoPanel eid={e.id} nombre={e.nombre} />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-xs text-blue-800">
        <p className="font-semibold mb-1 flex items-center gap-2"><Building2 size={14} />Referencia legal 2026</p>
        <p>UMA: $108.57 · SMG: $278.80 · IMSS patrón ~35% · INFONAVIT 5% · ISR Art. 96 LISR · Subsidio empleo Art. 1 Decreto · F. integración mín. 1.0452 (15 ag + 25% pv + vacaciones)</p>
      </div>
    </div>
  )
}
