'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { createAgent } from '@/lib/api'
import clsx from 'clsx'

const VERTICALES = [
  { value: 'restaurante', label: '🍽️ Restaurante' },
  { value: 'pasteleria', label: '🎂 Pastelería' },
  { value: 'tienda', label: '🏪 Tienda' },
  { value: 'contador', label: '📊 Contador' },
  { value: 'abogado', label: '⚖️ Abogado' },
  { value: 'medico', label: '⚕️ Médico' },
  { value: 'constructor', label: '🏗️ Constructor' },
  { value: 'musico', label: '🎵 Músico / Artista' },
  { value: 'general', label: '🌐 General' },
]

const CHANNELS = [
  { value: 'telegram', label: '✈️ Telegram', desc: 'Bot vía Telegram' },
  { value: 'whatsapp', label: '💬 WhatsApp', desc: 'Bot vía WhatsApp' },
  { value: 'discord', label: '🎮 Discord', desc: 'Bot vía Discord' },
]

const AGENT_TYPES = [
  { value: 'chat', label: 'Chat', desc: 'Responde preguntas de clientes 24/7' },
  { value: 'task', label: 'Tareas', desc: 'Ejecuta tareas automáticas' },
  { value: 'data-processor', label: 'Análisis', desc: 'Procesa y analiza datos' },
  { value: 'webhook', label: 'Webhook', desc: 'Recibe y responde eventos externos' },
]

interface Props {
  onSuccess?: (agentId: string) => void
}

export default function AutomationForm({ onSuccess }: Props) {
  const [form, setForm] = useState({
    name: '',
    description: '',
    verticales: [] as string[],
    agent_type: 'chat',
    channel: 'telegram',
    config: { tone: 'profesional', language: 'es' },
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  function toggleVertical(v: string) {
    setForm(prev => ({
      ...prev,
      verticales: prev.verticales.includes(v)
        ? prev.verticales.filter(x => x !== v)
        : [...prev.verticales, v],
    }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!form.name.trim()) {
      setError('El nombre es requerido')
      return
    }
    if (!form.description.trim()) {
      setError('La descripción es requerida')
      return
    }

    setLoading(true)
    try {
      const res = await createAgent(form)
      setSuccess(`¡Agente creado! ID: ${res.agent_id}. Creándose en background...`)
      if (onSuccess) onSuccess(res.agent_id)

      // Reset form
      setForm({
        name: '',
        description: '',
        verticales: [],
        agent_type: 'chat',
        channel: 'telegram',
        config: { tone: 'profesional', language: 'es' },
      })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al crear agente')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      {/* Nombre */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          Nombre de la automatización *
        </label>
        <input
          type="text"
          value={form.name}
          onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
          placeholder="Ej: Asistente de ventas"
          className="input-base"
          maxLength={80}
        />
      </div>

      {/* Descripción */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-2">
          ¿Qué quieres automatizar? *
        </label>
        <textarea
          value={form.description}
          onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
          placeholder="Ej: Responder preguntas frecuentes de mis clientes sobre precios, horarios y productos disponibles"
          className="input-base min-h-[100px] resize-none"
          maxLength={500}
        />
        <p className="mt-1 text-xs text-white/30">{form.description.length}/500</p>
      </div>

      {/* Verticales */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-3">
          Industria (opcional)
        </label>
        <div className="flex flex-wrap gap-2">
          {VERTICALES.map(v => (
            <button
              key={v.value}
              type="button"
              onClick={() => toggleVertical(v.value)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-150 border',
                form.verticales.includes(v.value)
                  ? 'bg-brand-500/30 border-brand-500/50 text-brand-300'
                  : 'bg-white/5 border-white/10 text-white/60 hover:text-white hover:bg-white/10'
              )}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tipo de agente */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-3">
          Tipo de agente
        </label>
        <div className="grid grid-cols-2 gap-2">
          {AGENT_TYPES.map(t => (
            <button
              key={t.value}
              type="button"
              onClick={() => setForm(p => ({ ...p, agent_type: t.value }))}
              className={clsx(
                'p-3 rounded-xl text-left border transition-all duration-150',
                form.agent_type === t.value
                  ? 'bg-brand-500/20 border-brand-500/40'
                  : 'bg-white/3 border-white/8 hover:bg-white/5'
              )}
            >
              <div className="text-sm font-medium text-white">{t.label}</div>
              <div className="text-xs text-white/40 mt-0.5">{t.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Canal */}
      <div>
        <label className="block text-sm font-medium text-white/70 mb-3">
          Canal de comunicación
        </label>
        <div className="grid grid-cols-3 gap-2">
          {CHANNELS.map(c => (
            <button
              key={c.value}
              type="button"
              onClick={() => setForm(p => ({ ...p, channel: c.value }))}
              className={clsx(
                'p-3 rounded-xl text-center border transition-all duration-150',
                form.channel === c.value
                  ? 'bg-brand-500/20 border-brand-500/40'
                  : 'bg-white/3 border-white/8 hover:bg-white/5'
              )}
            >
              <div className="text-sm font-medium text-white">{c.label}</div>
              <div className="text-xs text-white/40 mt-0.5">{c.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Feedback */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
        >
          {error}
        </motion.div>
      )}
      {success && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm"
        >
          {success}
        </motion.div>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Creando agente...
          </>
        ) : (
          '🤖 Crear Agente'
        )}
      </button>
    </form>
  )
}
