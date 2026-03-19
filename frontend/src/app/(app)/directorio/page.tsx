'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import {
  Building2, Plus, Search, Edit2, ChevronDown, ChevronUp,
  Phone, Mail, Globe, MapPin, CreditCard, Package, Anchor,
} from 'lucide-react'

const mxn = (v: number) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(v ?? 0)

const TIPOS = [
  { v: '', label: 'Todos' },
  { v: 'cliente', label: 'Clientes' },
  { v: 'proveedor', label: 'Proveedores' },
  { v: 'agente_aduanal', label: 'Agentes Aduanales' },
  { v: 'importador', label: 'Importadores' },
]

interface Contacto {
  id: string; tenant_id: string; tipo: string; razon_social: string
  rfc?: string; curp?: string; regimen_fiscal?: string; uso_cfdi?: string; pais?: string
  contacto_nombre?: string; email?: string; email2?: string
  telefono?: string; celular?: string; whatsapp?: string
  direccion_fiscal?: string; ciudad?: string; estado_mx?: string; cp?: string
  condicion_pago: number; limite_credito: number; moneda?: string
  banco?: string; cuenta?: string; clabe?: string
  patente_aduanal?: string; aduana_habitual?: string
  tax_id?: string; direccion_extranjero?: string
  total_facturas: number; monto_total_compras: number; monto_total_ventas: number
  ultima_operacion?: string; activo: boolean; notas?: string; created_at?: string
}

const EMPTY_FORM = {
  tipo: 'cliente', razon_social: '', rfc: '', curp: '', regimen_fiscal: '', uso_cfdi: 'G03', pais: 'México',
  contacto_nombre: '', email: '', email2: '', telefono: '', celular: '', whatsapp: '',
  direccion_fiscal: '', ciudad: '', estado_mx: '', cp: '',
  condicion_pago: 30, limite_credito: 0, moneda: 'MXN',
  banco: '', cuenta: '', clabe: '',
  patente_aduanal: '', aduana_habitual: '', tax_id: '', direccion_extranjero: '', notas: '',
}

const REGIMENES = [
  { v: '601', l: '601 - General de Ley PM' }, { v: '612', l: '612 - PF Actividades Empresariales' },
  { v: '626', l: '626 - RESICO' }, { v: '630', l: '630 - Enajenación e ingresos' },
  { v: '621', l: '621 - Incorporación Fiscal' }, { v: '605', l: '605 - Sueldos y Salarios' },
]

const USO_CFDI = [
  { v: 'G01', l: 'G01 - Adquisición de mercancias' }, { v: 'G03', l: 'G03 - Gastos en general' },
  { v: 'I01', l: 'I01 - Construcciones' }, { v: 'I04', l: 'I04 - Equipo de cómputo' },
  { v: 'D01', l: 'D01 - Honorarios médicos' }, { v: 'S01', l: 'S01 - Sin efectos fiscales' },
]

function TipoBadge({ tipo }: { tipo: string }) {
  const cfg: Record<string, string> = {
    cliente: 'bg-emerald-100 text-emerald-700',
    proveedor: 'bg-blue-100 text-blue-700',
    agente_aduanal: 'bg-purple-100 text-purple-700',
    importador: 'bg-orange-100 text-orange-700',
    ambos: 'bg-gray-100 text-gray-700',
  }
  const labels: Record<string, string> = {
    cliente: 'Cliente', proveedor: 'Proveedor',
    agente_aduanal: 'Ag. Aduanal', importador: 'Importador', ambos: 'Ambos',
  }
  return <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg[tipo] || 'bg-gray-100 text-gray-600'}`}>{labels[tipo] || tipo}</span>
}

function ContactoForm({ initial, onSave, onCancel }: {
  initial?: Partial<Contacto>; onSave: (d: typeof EMPTY_FORM) => void; onCancel: () => void
}) {
  const [form, setForm] = useState({ ...EMPTY_FORM, ...initial })
  const s = (k: string, v: unknown) => setForm(f => ({ ...f, [k]: v }))
  const inp = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
  const lbl = "block text-xs font-medium text-gray-500 mb-1"
  const sec = "text-xs font-bold text-gray-400 uppercase tracking-wider mb-3"

  return (
    <div className="bg-white rounded-xl border-2 border-brand-200 p-6 space-y-6">
      <h3 className="font-bold text-gray-900">{initial?.id ? 'Editar contacto' : 'Nuevo contacto'}</h3>

      <div>
        <p className={sec}>Tipo y datos fiscales</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <label className={lbl}>Tipo *</label>
            <select className={inp} value={form.tipo} onChange={e => s('tipo', e.target.value)}>
              <option value="cliente">Cliente</option>
              <option value="proveedor">Proveedor</option>
              <option value="agente_aduanal">Agente Aduanal</option>
              <option value="importador">Importador</option>
              <option value="ambos">Cliente y Proveedor</option>
            </select>
          </div>
          <div className="sm:col-span-2"><label className={lbl}>Razón social *</label><input className={inp} required value={form.razon_social} onChange={e => s('razon_social', e.target.value)} /></div>
          <div><label className={lbl}>RFC</label><input className={inp} maxLength={13} value={form.rfc} onChange={e => s('rfc', e.target.value.toUpperCase())} /></div>
          <div>
            <label className={lbl}>Régimen fiscal</label>
            <select className={inp} value={form.regimen_fiscal} onChange={e => s('regimen_fiscal', e.target.value)}>
              <option value="">— Seleccionar —</option>
              {REGIMENES.map(r => <option key={r.v} value={r.v}>{r.l}</option>)}
            </select>
          </div>
          <div>
            <label className={lbl}>Uso CFDI</label>
            <select className={inp} value={form.uso_cfdi} onChange={e => s('uso_cfdi', e.target.value)}>
              {USO_CFDI.map(u => <option key={u.v} value={u.v}>{u.l}</option>)}
            </select>
          </div>
          <div><label className={lbl}>País</label><input className={inp} value={form.pais} onChange={e => s('pais', e.target.value)} /></div>
          {form.pais !== 'México' && <div><label className={lbl}>Tax ID (EIN/SSN)</label><input className={inp} value={form.tax_id} onChange={e => s('tax_id', e.target.value)} /></div>}
        </div>
      </div>

      <div>
        <p className={sec}>Contacto</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div><label className={lbl}>Nombre contacto</label><input className={inp} value={form.contacto_nombre} onChange={e => s('contacto_nombre', e.target.value)} /></div>
          <div><label className={lbl}>Email principal</label><input type="email" className={inp} value={form.email} onChange={e => s('email', e.target.value)} /></div>
          <div><label className={lbl}>Email secundario</label><input type="email" className={inp} value={form.email2} onChange={e => s('email2', e.target.value)} /></div>
          <div><label className={lbl}>Teléfono oficina</label><input className={inp} value={form.telefono} onChange={e => s('telefono', e.target.value)} /></div>
          <div><label className={lbl}>Celular</label><input className={inp} value={form.celular} onChange={e => s('celular', e.target.value)} /></div>
          <div><label className={lbl}>WhatsApp</label><input className={inp} placeholder="52XXXXXXXXXX" value={form.whatsapp} onChange={e => s('whatsapp', e.target.value)} /></div>
        </div>
      </div>

      <div>
        <p className={sec}>Dirección fiscal</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="sm:col-span-2"><label className={lbl}>Dirección</label><input className={inp} value={form.direccion_fiscal} onChange={e => s('direccion_fiscal', e.target.value)} /></div>
          <div><label className={lbl}>Ciudad</label><input className={inp} value={form.ciudad} onChange={e => s('ciudad', e.target.value)} /></div>
          <div><label className={lbl}>Estado</label><input className={inp} placeholder="Sonora, CDMX..." value={form.estado_mx} onChange={e => s('estado_mx', e.target.value)} /></div>
          <div><label className={lbl}>C.P.</label><input className={inp} maxLength={5} value={form.cp} onChange={e => s('cp', e.target.value)} /></div>
          {form.pais !== 'México' && <div className="sm:col-span-3"><label className={lbl}>Dirección extranjero</label><input className={inp} value={form.direccion_extranjero} onChange={e => s('direccion_extranjero', e.target.value)} /></div>}
        </div>
      </div>

      <div>
        <p className={sec}>Condiciones comerciales</p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div><label className={lbl}>Días de crédito</label><input type="number" min="0" className={inp} value={form.condicion_pago} onChange={e => s('condicion_pago', Number(e.target.value))} /></div>
          <div><label className={lbl}>Límite crédito $</label><input type="number" min="0" step="any" className={inp} value={form.limite_credito || ''} onChange={e => s('limite_credito', Number(e.target.value))} /></div>
          <div>
            <label className={lbl}>Moneda</label>
            <select className={inp} value={form.moneda} onChange={e => s('moneda', e.target.value)}>
              {['MXN','USD','EUR'].map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div>
        <p className={sec}>Datos bancarios</p>
        <div className="grid grid-cols-3 gap-4">
          <div><label className={lbl}>Banco</label><input className={inp} value={form.banco} onChange={e => s('banco', e.target.value)} /></div>
          <div><label className={lbl}>No. Cuenta</label><input className={inp} value={form.cuenta} onChange={e => s('cuenta', e.target.value)} /></div>
          <div><label className={lbl}>CLABE (18 dígitos)</label><input className={inp} maxLength={18} value={form.clabe} onChange={e => s('clabe', e.target.value)} /></div>
        </div>
      </div>

      {form.tipo === 'agente_aduanal' && (
        <div>
          <p className={sec}>Datos aduanales</p>
          <div className="grid grid-cols-2 gap-4">
            <div><label className={lbl}>Patente aduanal (5 dígitos)</label><input className={inp} maxLength={5} value={form.patente_aduanal} onChange={e => s('patente_aduanal', e.target.value)} /></div>
            <div><label className={lbl}>Aduana habitual</label><input className={inp} placeholder="Nogales, Tijuana, Hermosillo..." value={form.aduana_habitual} onChange={e => s('aduana_habitual', e.target.value)} /></div>
          </div>
        </div>
      )}

      <div><label className={lbl}>Notas</label><textarea className={inp} rows={2} value={form.notas} onChange={e => s('notas', e.target.value)} /></div>

      <div className="flex gap-3">
        <button onClick={() => onSave(form)} className="flex-1 bg-brand-600 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-brand-700">
          {initial?.id ? 'Guardar cambios' : 'Crear contacto'}
        </button>
        <button onClick={onCancel} className="px-5 bg-gray-100 text-gray-700 rounded-lg py-2.5 text-sm hover:bg-gray-200">Cancelar</button>
      </div>
    </div>
  )
}

function ContactoDetalle({ c, onEdit }: { c: Contacto; onEdit: () => void }) {
  return (
    <div className="px-5 pb-5 pt-2">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
        <div className="space-y-2">
          <p className="text-xs font-bold text-gray-400 uppercase">Fiscal</p>
          {c.rfc && <p><span className="text-gray-400">RFC: </span><span className="font-mono">{c.rfc}</span></p>}
          {c.regimen_fiscal && <p><span className="text-gray-400">Régimen: </span>{c.regimen_fiscal}</p>}
          {c.uso_cfdi && <p><span className="text-gray-400">Uso CFDI: </span>{c.uso_cfdi}</p>}
          {c.tax_id && <p><span className="text-gray-400">Tax ID: </span><span className="font-mono">{c.tax_id}</span></p>}
        </div>
        <div className="space-y-2">
          <p className="text-xs font-bold text-gray-400 uppercase">Contacto</p>
          {c.contacto_nombre && <p>{c.contacto_nombre}</p>}
          {c.email && <p className="flex items-center gap-1"><Mail size={12}/>{c.email}</p>}
          {c.telefono && <p className="flex items-center gap-1"><Phone size={12}/>{c.telefono}</p>}
          {c.celular && <p className="flex items-center gap-1"><Phone size={12}/>{c.celular}</p>}
          {c.whatsapp && <p className="text-emerald-600 text-xs">WA: {c.whatsapp}</p>}
        </div>
        <div className="space-y-2">
          <p className="text-xs font-bold text-gray-400 uppercase">Dirección</p>
          {c.direccion_fiscal && <p className="flex items-start gap-1"><MapPin size={12} className="mt-0.5 shrink-0"/>{c.direccion_fiscal}</p>}
          {c.ciudad && <p>{c.ciudad}, {c.estado_mx} {c.cp}</p>}
          <p className="flex items-center gap-1"><Globe size={12}/>{c.pais}</p>
        </div>
        <div className="space-y-2">
          <p className="text-xs font-bold text-gray-400 uppercase">Comercial</p>
          <p><span className="text-gray-400">Crédito: </span>{c.condicion_pago} días</p>
          {c.limite_credito > 0 && <p><span className="text-gray-400">Límite: </span>{mxn(c.limite_credito)}</p>}
          <p><span className="text-gray-400">Moneda: </span>{c.moneda}</p>
        </div>
        {(c.banco || c.clabe) && (
          <div className="space-y-2">
            <p className="text-xs font-bold text-gray-400 uppercase">Bancario</p>
            {c.banco && <p className="flex items-center gap-1"><CreditCard size={12}/>{c.banco}</p>}
            {c.clabe && <p className="font-mono text-xs">{c.clabe}</p>}
          </div>
        )}
        {c.tipo === 'agente_aduanal' && (
          <div className="space-y-2">
            <p className="text-xs font-bold text-gray-400 uppercase">Aduanal</p>
            {c.patente_aduanal && <p className="flex items-center gap-1"><Anchor size={12}/>Patente: <b>{c.patente_aduanal}</b></p>}
            {c.aduana_habitual && <p>Aduana: {c.aduana_habitual}</p>}
          </div>
        )}
        <div className="col-span-full space-y-1">
          <p className="text-xs font-bold text-gray-400 uppercase">Historial</p>
          <div className="flex gap-6 text-sm">
            <p><span className="text-gray-400">Facturas: </span><b>{c.total_facturas}</b></p>
            {c.monto_total_ventas > 0 && <p><span className="text-gray-400">Ventas: </span><b className="text-emerald-600">{mxn(c.monto_total_ventas)}</b></p>}
            {c.monto_total_compras > 0 && <p><span className="text-gray-400">Compras: </span><b className="text-blue-600">{mxn(c.monto_total_compras)}</b></p>}
          </div>
          {c.notas && <p className="text-gray-400 italic text-xs">{c.notas}</p>}
        </div>
      </div>
      <button onClick={onEdit} className="mt-4 flex items-center gap-1 text-xs text-brand-600 hover:underline">
        <Edit2 size={12}/>Editar
      </button>
    </div>
  )
}

export default function DirectorioPage() {
  const [contactos, setContactos] = useState<Contacto[]>([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')
  const [showForm, setShowForm]   = useState(false)
  const [editando, setEditando]   = useState<Contacto | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [filtroTipo, setFiltroTipo] = useState('')
  const [buscar, setBuscar]       = useState('')

  function load() {
    setLoading(true)
    const params = new URLSearchParams()
    if (filtroTipo) params.set('tipo', filtroTipo)
    if (buscar) params.set('buscar', buscar)
    api.get<Contacto[]>(`/contactos?${params}`)
      .then(setContactos)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }
  useEffect(load, [filtroTipo, buscar])

  async function guardar(data: typeof EMPTY_FORM) {
    try {
      if (editando?.id) await api.patch(`/contactos/${editando.id}`, data)
      else await api.post('/contactos', data)
      setShowForm(false); setEditando(null); load()
    } catch (e: unknown) { alert(e instanceof Error ? e.message : 'Error') }
  }

  const clientes   = contactos.filter(c => c.tipo === 'cliente').length
  const proveedores = contactos.filter(c => c.tipo === 'proveedor').length
  const agentes    = contactos.filter(c => c.tipo === 'agente_aduanal').length

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2"><Building2 size={24}/>Directorio</h1>
          <p className="text-sm text-gray-500 mt-0.5">{clientes} clientes · {proveedores} proveedores · {agentes} agentes aduanales</p>
        </div>
        <button onClick={() => { setEditando(null); setShowForm(v => !v) }} className="flex items-center gap-2 bg-brand-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-brand-700">
          <Plus size={16}/>Nuevo
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Clientes', val: clientes, color: 'text-emerald-600' },
          { label: 'Proveedores', val: proveedores, color: 'text-blue-600' },
          { label: 'Ag. Aduanales', val: agentes, color: 'text-purple-600' },
          { label: 'Total', val: contactos.length, color: 'text-gray-900' },
        ].map(k => (
          <Card key={k.label} className="p-4">
            <p className="text-xs text-gray-400 mb-1">{k.label}</p>
            <p className={`text-2xl font-bold ${k.color}`}>{k.val}</p>
          </Card>
        ))}
      </div>

      {/* Filtros */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={buscar} onChange={e => setBuscar(e.target.value)} placeholder="Buscar por nombre, RFC..." className="w-full pl-9 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div className="flex gap-1">
          {TIPOS.map(t => (
            <button key={t.v} onClick={() => setFiltroTipo(t.v)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${filtroTipo === t.v ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {(showForm || editando) && (
        <ContactoForm initial={editando || undefined} onSave={guardar} onCancel={() => { setShowForm(false); setEditando(null) }} />
      )}

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}
      {error   && <p className="text-red-500 text-sm">Error: {error}</p>}

      <Card>
        {contactos.length === 0 && !loading ? (
          <div className="text-center py-12 text-gray-400">
            <Package size={40} className="mx-auto mb-3 opacity-30" />
            <p className="font-medium">Sin contactos registrados</p>
            <p className="text-xs mt-1">Agrega clientes, proveedores y agentes aduanales</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-500 uppercase tracking-wide">
                  <th className="text-left px-4 py-3">Empresa</th>
                  <th className="text-left px-4 py-3">Tipo</th>
                  <th className="text-left px-4 py-3 hidden sm:table-cell">RFC</th>
                  <th className="text-left px-4 py-3 hidden md:table-cell">Contacto</th>
                  <th className="text-left px-4 py-3 hidden md:table-cell">Ciudad</th>
                  <th className="text-right px-4 py-3 hidden lg:table-cell">Facturas</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {contactos.map(c => (
                  <>
                    <tr key={c.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <p className="font-semibold text-gray-900 truncate max-w-[180px]">{c.razon_social}</p>
                        {c.patente_aduanal && <p className="text-xs text-purple-600">Patente: {c.patente_aduanal}</p>}
                      </td>
                      <td className="px-4 py-3"><TipoBadge tipo={c.tipo} /></td>
                      <td className="px-4 py-3 hidden sm:table-cell font-mono text-xs text-gray-600">{c.rfc || '—'}</td>
                      <td className="px-4 py-3 hidden md:table-cell text-xs text-gray-600">
                        {c.contacto_nombre && <p>{c.contacto_nombre}</p>}
                        {c.email && <p className="text-gray-400">{c.email}</p>}
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell text-xs text-gray-500">{c.ciudad || c.pais}</td>
                      <td className="px-4 py-3 hidden lg:table-cell text-right text-xs">
                        <p className="font-semibold">{c.total_facturas}</p>
                        {c.monto_total_ventas > 0 && <p className="text-emerald-600">{mxn(c.monto_total_ventas)}</p>}
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => setExpandedId(expandedId === c.id ? null : c.id)} className="p-1.5 text-gray-400 hover:text-gray-600 rounded">
                          {expandedId === c.id ? <ChevronUp size={14}/> : <ChevronDown size={14}/>}
                        </button>
                      </td>
                    </tr>
                    {expandedId === c.id && (
                      <tr key={`${c.id}-d`} className="bg-gray-50">
                        <td colSpan={7}>
                          <ContactoDetalle c={c} onEdit={() => { setEditando(c); setExpandedId(null); setShowForm(false) }} />
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
