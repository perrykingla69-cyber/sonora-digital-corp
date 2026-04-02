'use client'

import { useEffect, useState } from 'react'
import { api, GSDTask } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { CheckSquare, Trash2, Plus } from 'lucide-react'

export default function TasksPage() {
  const [tasks, setTasks]   = useState<GSDTask[]>([])
  const [loading, setLoading] = useState(true)
  const [titulo, setTitulo]   = useState('')
  const [prioridad, setPrioridad] = useState<'alta' | 'media' | 'baja'>('media')
  const [adding, setAdding]   = useState(false)

  function load() {
    api.get<GSDTask[]>('/gsd/tasks')
      .then(setTasks)
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function completar(id: string) {
    await api.patch(`/gsd/tasks/${id}/done`)
    load()
  }

  async function eliminar(id: string) {
    if (!confirm('¿Eliminar tarea?')) return
    await api.delete(`/gsd/tasks/${id}`)
    load()
  }

  async function agregar(e: React.FormEvent) {
    e.preventDefault()
    if (!titulo.trim()) return
    setAdding(true)
    try {
      await api.post('/gsd/tasks', { titulo, prioridad })
      setTitulo('')
      load()
    } finally {
      setAdding(false)
    }
  }

  const pendientes  = tasks.filter(t => !t.completada)
  const completadas = tasks.filter(t =>  t.completada)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Tareas GSD</h1>

      {/* Nueva tarea */}
      <Card className="p-4">
        <form onSubmit={agregar} className="flex items-center gap-3">
          <input
            value={titulo}
            onChange={e => setTitulo(e.target.value)}
            placeholder="Nueva tarea..."
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-500"
          />
          <select
            value={prioridad}
            onChange={e => setPrioridad(e.target.value as typeof prioridad)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none"
          >
            <option value="alta">🔴 Alta</option>
            <option value="media">🟡 Media</option>
            <option value="baja">🟢 Baja</option>
          </select>
          <button
            type="submit"
            disabled={adding || !titulo.trim()}
            className="flex items-center gap-1.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                       text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus size={16} /> Agregar
          </button>
        </form>
      </Card>

      {loading && <p className="text-gray-400 text-sm">Cargando...</p>}

      {/* Pendientes */}
      {pendientes.length > 0 && (
        <Card>
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Pendientes ({pendientes.length})</h2>
          </div>
          <ul className="divide-y divide-gray-50">
            {pendientes.map(t => (
              <li key={t.id} className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50">
                <button
                  onClick={() => completar(t.id)}
                  className="text-gray-300 hover:text-emerald-500 transition-colors flex-shrink-0"
                  title="Marcar completa"
                >
                  <CheckSquare size={20} />
                </button>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{t.titulo}</p>
                  {t.fecha_limite && (
                    <p className="text-xs text-gray-400">Límite: {t.fecha_limite.slice(0,10)}</p>
                  )}
                </div>
                <Badge variant={t.prioridad} />
                <button
                  onClick={() => eliminar(t.id)}
                  className="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0"
                >
                  <Trash2 size={16} />
                </button>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Completadas */}
      {completadas.length > 0 && (
        <Card>
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-semibold text-gray-500 text-sm">Completadas ({completadas.length})</h2>
          </div>
          <ul className="divide-y divide-gray-50">
            {completadas.slice(0, 10).map(t => (
              <li key={t.id} className="flex items-center gap-3 px-4 py-2.5 opacity-50">
                <CheckSquare size={18} className="text-emerald-500 flex-shrink-0" />
                <p className="text-sm line-through text-gray-500 truncate">{t.titulo}</p>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {!loading && tasks.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <CheckSquare size={40} className="mx-auto mb-3 opacity-20" />
          <p>Sin tareas. Agrega la primera arriba.</p>
        </div>
      )}
    </div>
  )
}
