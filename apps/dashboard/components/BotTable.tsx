'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { type Bot, deleteBot } from '@/lib/api'
import clsx from 'clsx'

const STATUS_LABELS: Record<string, string> = {
  active: 'Activo',
  created: 'Configurando',
  creating: 'Creando',
  failed: 'Error',
  destroying: 'Eliminando',
  stopped: 'Pausado',
}

const STATUS_CLASS: Record<string, string> = {
  active: 'badge-active',
  created: 'badge-creating',
  creating: 'badge-creating',
  failed: 'badge-failed',
  destroying: 'badge-failed',
  stopped: 'badge-stopped',
}

const CHANNEL_ICONS: Record<string, string> = {
  telegram: '✈️',
  whatsapp: '💬',
  discord: '🎮',
}

interface Props {
  bots: Bot[]
  onRefresh?: () => void
}

export default function BotTable({ bots, onRefresh }: Props) {
  const [deleting, setDeleting] = useState<string | null>(null)

  async function handleDelete(botId: string) {
    if (!confirm('¿Eliminar este bot?')) return
    setDeleting(botId)
    try {
      await deleteBot(botId)
      onRefresh?.()
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error al eliminar')
    } finally {
      setDeleting(null)
    }
  }

  if (bots.length === 0) {
    return (
      <div className="text-center py-12 text-white/30">
        <div className="text-4xl mb-3">📡</div>
        <p className="text-sm">No tienes bots activos aún.</p>
        <p className="text-xs mt-1">Crea una automatización para comenzar.</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5">
            <th className="text-left py-3 px-4 text-white/40 font-medium">Bot</th>
            <th className="text-left py-3 px-4 text-white/40 font-medium">Canal</th>
            <th className="text-left py-3 px-4 text-white/40 font-medium">Estado</th>
            <th className="text-right py-3 px-4 text-white/40 font-medium">Mensajes Hoy</th>
            <th className="text-right py-3 px-4 text-white/40 font-medium">Uptime</th>
            <th className="text-left py-3 px-4 text-white/40 font-medium">Creado</th>
            <th className="py-3 px-4" />
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {bots.map(bot => (
              <motion.tr
                key={bot.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="border-b border-white/5 hover:bg-white/2 transition-colors"
              >
                <td className="py-3 px-4">
                  <div className="font-medium text-white">
                    {bot.name || `Bot ${bot.id.slice(0, 8)}`}
                  </div>
                  {bot.agent_name && (
                    <div className="text-xs text-white/40">{bot.agent_name}</div>
                  )}
                </td>
                <td className="py-3 px-4">
                  <span className="flex items-center gap-1.5">
                    <span>{CHANNEL_ICONS[bot.channel] || '🤖'}</span>
                    <span className="capitalize text-white/70">{bot.channel}</span>
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span className={clsx(
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    STATUS_CLASS[bot.status] || 'badge-stopped'
                  )}>
                    {STATUS_LABELS[bot.status] || bot.status}
                  </span>
                </td>
                <td className="py-3 px-4 text-right text-white/70">
                  {bot.messages_today ?? 0}
                </td>
                <td className="py-3 px-4 text-right text-white/70">
                  {bot.uptime_pct ? `${Number(bot.uptime_pct).toFixed(1)}%` : '—'}
                </td>
                <td className="py-3 px-4 text-white/40 text-xs">
                  {bot.created_at
                    ? new Date(bot.created_at).toLocaleDateString('es-MX', {
                        month: 'short', day: 'numeric'
                      })
                    : '—'}
                </td>
                <td className="py-3 px-4">
                  <button
                    onClick={() => handleDelete(bot.id)}
                    disabled={deleting === bot.id}
                    className="text-xs text-white/30 hover:text-red-400 transition-colors disabled:opacity-50"
                  >
                    {deleting === bot.id ? '...' : 'Eliminar'}
                  </button>
                </td>
              </motion.tr>
            ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  )
}
