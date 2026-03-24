'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table'
import { api } from '@/lib/api'
import {
  Plus, Search, Download, Upload, ChevronUp, ChevronDown,
  ChevronsUpDown, Check, X, Loader2, Building2, Phone, Mail,
} from 'lucide-react'

// ─── Types ───────────────────────────────────────────────────────────────────
interface Cliente {
  id: string
  razon_social: string
  rfc: string
  contacto_nombre: string
  email: string
  telefono: string
  celular: string
  ciudad: string
  estado_mx: string
  condicion_pago: number
  limite_credito: number
  moneda: string
  regimen_fiscal: string
  uso_cfdi: string
  notas: string
  activo: boolean
  total_facturas: number
  monto_total_ventas: number
  created_at: string
}

type EditableField = keyof Pick<
  Cliente,
  'razon_social' | 'rfc' | 'contacto_nombre' | 'email' |
  'telefono' | 'celular' | 'ciudad' | 'estado_mx' |
  'condicion_pago' | 'limite_credito' | 'moneda' |
  'regimen_fiscal' | 'uso_cfdi' | 'notas'
>

// ─── Inline Cell Editor ───────────────────────────────────────────────────────
function EditableCell({
  value: initialValue,
  rowId,
  field,
  type = 'text',
  onSave,
}: {
  value: string | number
  rowId: string
  field: EditableField
  type?: 'text' | 'number' | 'email'
  onSave: (id: string, field: EditableField, value: string | number) => Promise<void>
}) {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(initialValue)
  const [saving, setSaving] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => { setValue(initialValue) }, [initialValue])
  useEffect(() => { if (editing) inputRef.current?.focus() }, [editing])

  async function commit() {
    if (value === initialValue) { setEditing(false); return }
    setSaving(true)
    await onSave(rowId, field, value)
    setSaving(false)
    setEditing(false)
  }

  function cancel() { setValue(initialValue); setEditing(false) }

  if (editing) {
    return (
      <div className="flex items-center gap-1">
        <input
          ref={inputRef}
          type={type}
          value={value}
          onChange={e => setValue(type === 'number' ? Number(e.target.value) : e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') cancel() }}
          className="bg-[#1e1e1e] border border-[#D4AF37]/60 rounded px-2 py-0.5 text-xs text-white w-full focus:outline-none focus:ring-1 focus:ring-[#D4AF37]"
        />
        {saving
          ? <Loader2 className="w-3 h-3 text-[#D4AF37] animate-spin shrink-0" />
          : <>
              <button onClick={commit} className="text-emerald-400 hover:text-emerald-300"><Check className="w-3 h-3" /></button>
              <button onClick={cancel} className="text-red-400 hover:text-red-300"><X className="w-3 h-3" /></button>
            </>
        }
      </div>
    )
  }

  return (
    <div
      onClick={() => setEditing(true)}
      className="cursor-pointer truncate hover:bg-[#D4AF37]/10 rounded px-1 py-0.5 transition-colors text-xs"
      title={String(value || '—')}
    >
      {value !== '' && value !== null && value !== undefined ? String(value) : <span className="text-[#555]">—</span>}
    </div>
  )
}

// ─── Status Badge ─────────────────────────────────────────────────────────────
function StatusBadge({ activo }: { activo: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${
      activo ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'
    }`}>
      <span className={`w-1.5 h-1.5 rounded-full ${activo ? 'bg-emerald-400' : 'bg-red-400'}`} />
      {activo ? 'Activo' : 'Inactivo'}
    </span>
  )
}

const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v ?? 0)

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function ClientesPage() {
  const [data, setData] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [saving, setSaving] = useState<Set<string>>(new Set())
  const [showForm, setShowForm] = useState(false)
  const [newCliente, setNewCliente] = useState({ razon_social: '', rfc: '', email: '', telefono: '' })
  const [creating, setCreating] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    api.get<Cliente[]>('/contactos?tipo=cliente&limit=500')
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleSave = useCallback(async (id: string, field: EditableField, value: string | number) => {
    setSaving(prev => new Set(prev).add(id))
    try {
      await api.patch(`/contactos/${id}`, { [field]: value })
      setData(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c))
    } finally {
      setSaving(prev => { const s = new Set(prev); s.delete(id); return s })
    }
  }, [])

  async function handleCreate() {
    if (!newCliente.razon_social.trim()) return
    setCreating(true)
    try {
      const created = await api.post<Cliente>('/contactos', {
        tipo: 'cliente',
        ...newCliente,
        condicion_pago: 30,
        limite_credito: 0,
        moneda: 'MXN',
        uso_cfdi: 'G03',
        pais: 'México',
      })
      setData(prev => [created, ...prev])
      setNewCliente({ razon_social: '', rfc: '', email: '', telefono: '' })
      setShowForm(false)
    } finally {
      setCreating(false)
    }
  }

  async function handleToggleActivo(id: string, current: boolean) {
    await api.patch(`/contactos/${id}`, { activo: !current })
    setData(prev => prev.map(c => c.id === id ? { ...c, activo: !current } : c))
  }

  const col = createColumnHelper<Cliente>()

  const columns = [
    col.accessor('razon_social', {
      header: 'Razón Social',
      cell: info => (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center shrink-0">
            <Building2 className="w-3.5 h-3.5 text-[#D4AF37]" />
          </div>
          <EditableCell value={info.getValue()} rowId={info.row.original.id} field="razon_social" onSave={handleSave} />
        </div>
      ),
      size: 220,
    }),
    col.accessor('rfc', {
      header: 'RFC',
      cell: info => <EditableCell value={info.getValue() ?? ''} rowId={info.row.original.id} field="rfc" onSave={handleSave} />,
      size: 130,
    }),
    col.accessor('contacto_nombre', {
      header: 'Contacto',
      cell: info => <EditableCell value={info.getValue() ?? ''} rowId={info.row.original.id} field="contacto_nombre" onSave={handleSave} />,
      size: 160,
    }),
    col.accessor('email', {
      header: 'Email',
      cell: info => (
        <div className="flex items-center gap-1.5">
          <Mail className="w-3 h-3 text-[#D4AF37]/50 shrink-0" />
          <EditableCell value={info.getValue() ?? ''} rowId={info.row.original.id} field="email" type="email" onSave={handleSave} />
        </div>
      ),
      size: 200,
    }),
    col.accessor('telefono', {
      header: 'Teléfono',
      cell: info => (
        <div className="flex items-center gap-1.5">
          <Phone className="w-3 h-3 text-[#D4AF37]/50 shrink-0" />
          <EditableCell value={info.getValue() ?? ''} rowId={info.row.original.id} field="telefono" onSave={handleSave} />
        </div>
      ),
      size: 130,
    }),
    col.accessor('ciudad', {
      header: 'Ciudad',
      cell: info => <EditableCell value={info.getValue() ?? ''} rowId={info.row.original.id} field="ciudad" onSave={handleSave} />,
      size: 120,
    }),
    col.accessor('condicion_pago', {
      header: 'Crédito (días)',
      cell: info => <EditableCell value={info.getValue()} rowId={info.row.original.id} field="condicion_pago" type="number" onSave={handleSave} />,
      size: 110,
    }),
    col.accessor('monto_total_ventas', {
      header: 'Ventas Totales',
      cell: info => <span className="text-xs font-mono text-emerald-400">{mxn(info.getValue())}</span>,
      size: 130,
    }),
    col.accessor('total_facturas', {
      header: 'Facturas',
      cell: info => <span className="text-xs font-mono text-[#D4AF37]">{info.getValue()}</span>,
      size: 80,
    }),
    col.accessor('activo', {
      header: 'Estado',
      cell: info => (
        <button onClick={() => handleToggleActivo(info.row.original.id, info.getValue())}>
          <StatusBadge activo={info.getValue()} />
        </button>
      ),
      size: 90,
      enableSorting: true,
    }),
  ]

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  const rows = table.getRowModel().rows
  const totalVentas = data.reduce((s, c) => s + (c.monto_total_ventas || 0), 0)
  const activos = data.filter(c => c.activo).length

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Clientes</h1>
          <p className="text-xs text-[#888]">
            {activos} activos · {data.length} total · {mxn(totalVentas)} ventas acumuladas
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowForm(v => !v)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#D4AF37] text-black rounded-lg text-xs font-semibold hover:bg-[#f0c842] transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> Nuevo Cliente
          </button>
        </div>
      </div>

      {/* New cliente quick form */}
      {showForm && (
        <div className="bg-[#161616] border border-[#D4AF37]/30 rounded-xl p-4 flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="text-[10px] text-[#888] uppercase tracking-wider mb-1 block">Razón Social *</label>
            <input
              value={newCliente.razon_social}
              onChange={e => setNewCliente(p => ({ ...p, razon_social: e.target.value }))}
              placeholder="ACME SA de CV"
              className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#D4AF37]"
            />
          </div>
          <div className="w-36">
            <label className="text-[10px] text-[#888] uppercase tracking-wider mb-1 block">RFC</label>
            <input
              value={newCliente.rfc}
              onChange={e => setNewCliente(p => ({ ...p, rfc: e.target.value.toUpperCase() }))}
              placeholder="ACM010101AAA"
              maxLength={13}
              className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#D4AF37] font-mono"
            />
          </div>
          <div className="w-48">
            <label className="text-[10px] text-[#888] uppercase tracking-wider mb-1 block">Email</label>
            <input
              value={newCliente.email}
              onChange={e => setNewCliente(p => ({ ...p, email: e.target.value }))}
              type="email"
              placeholder="contacto@empresa.com"
              className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#D4AF37]"
            />
          </div>
          <div className="w-36">
            <label className="text-[10px] text-[#888] uppercase tracking-wider mb-1 block">Teléfono</label>
            <input
              value={newCliente.telefono}
              onChange={e => setNewCliente(p => ({ ...p, telefono: e.target.value }))}
              placeholder="6621234567"
              className="w-full bg-[#0A0A0A] border border-[#333] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#D4AF37]"
            />
          </div>
          <button
            onClick={handleCreate}
            disabled={creating || !newCliente.razon_social.trim()}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-semibold hover:bg-[#f0c842] disabled:opacity-50 transition-colors"
          >
            {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Crear
          </button>
          <button
            onClick={() => setShowForm(false)}
            className="px-4 py-2 border border-[#333] text-[#888] rounded-lg text-sm hover:border-[#555] transition-colors"
          >
            Cancelar
          </button>
        </div>
      )}

      {/* Search */}
      <div className="flex items-center gap-2 bg-[#161616] border border-[#2a2a2a] rounded-xl px-3 py-2">
        <Search className="w-4 h-4 text-[#555]" />
        <input
          value={globalFilter}
          onChange={e => setGlobalFilter(e.target.value)}
          placeholder="Buscar por nombre, RFC, contacto..."
          className="flex-1 bg-transparent text-sm text-white placeholder-[#555] focus:outline-none"
        />
        {globalFilter && (
          <button onClick={() => setGlobalFilter('')} className="text-[#555] hover:text-white">
            <X className="w-4 h-4" />
          </button>
        )}
        <span className="text-[10px] text-[#555]">{rows.length} resultados</span>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-sm text-red-400">{error}</div>
      )}

      {/* Airtable Grid */}
      <div className="flex-1 overflow-hidden bg-[#0F0F0F] border border-[#2a2a2a] rounded-xl">
        {loading ? (
          <div className="flex items-center justify-center h-full gap-2 text-[#D4AF37]">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Cargando clientes...</span>
          </div>
        ) : (
          <div className="h-full overflow-auto">
            <table className="w-full border-collapse" style={{ minWidth: '1100px' }}>
              {/* Header */}
              <thead className="sticky top-0 z-10">
                {table.getHeaderGroups().map(hg => (
                  <tr key={hg.id} className="bg-[#161616] border-b border-[#2a2a2a]">
                    {hg.headers.map(header => (
                      <th
                        key={header.id}
                        style={{ width: header.getSize() }}
                        className="px-3 py-2.5 text-left border-r border-[#2a2a2a] last:border-r-0"
                      >
                        {header.isPlaceholder ? null : (
                          <button
                            onClick={header.column.getToggleSortingHandler()}
                            className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-[#888] hover:text-white transition-colors"
                          >
                            {flexRender(header.column.columnDef.header, header.getContext())}
                            {header.column.getIsSorted() === 'asc'
                              ? <ChevronUp className="w-3 h-3 text-[#D4AF37]" />
                              : header.column.getIsSorted() === 'desc'
                                ? <ChevronDown className="w-3 h-3 text-[#D4AF37]" />
                                : <ChevronsUpDown className="w-3 h-3 opacity-30" />
                            }
                          </button>
                        )}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>

              {/* Body */}
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="text-center py-16 text-[#555] text-sm">
                      {globalFilter ? 'Sin resultados para la búsqueda' : 'No hay clientes aún'}
                    </td>
                  </tr>
                ) : rows.map((row, i) => (
                  <tr
                    key={row.id}
                    className={`border-b border-[#1e1e1e] hover:bg-[#D4AF37]/3 transition-colors ${
                      saving.has(row.original.id) ? 'opacity-75' : ''
                    } ${i % 2 === 0 ? 'bg-[#0F0F0F]' : 'bg-[#111111]'}`}
                  >
                    {row.getVisibleCells().map(cell => (
                      <td
                        key={cell.id}
                        className="px-3 py-2 border-r border-[#1e1e1e] last:border-r-0 align-middle"
                        style={{ width: cell.column.getSize() }}
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-[10px] text-[#555]">
        <span>Click en cualquier celda para editar · Enter para guardar · Esc para cancelar</span>
        <span>{rows.length} / {data.length} clientes · Ventas: {mxn(totalVentas)}</span>
      </div>
    </div>
  )
}
