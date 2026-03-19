'use client'

import { useEffect, useState } from 'react'
import { api, StatusData } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Send, CheckCircle, XCircle, ExternalLink, Terminal } from 'lucide-react'

export default function TelegramPage() {
  const [status, setStatus] = useState<StatusData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<StatusData>('/status')
      .then(setStatus)
      .catch(() => null)
      .finally(() => setLoading(false))
  }, [])

  const botUrl = 'https://t.me/MysticAIBot'

  const COMANDOS = [
    { cmd: '/start',     desc: 'Menú principal con botones' },
    { cmd: '/login',     desc: '/login email password — autenticación' },
    { cmd: '/dashboard', desc: 'Resumen financiero del mes' },
    { cmd: '/facturas',  desc: 'Últimas 8 facturas del tenant' },
    { cmd: '/cierre',    desc: 'Cierre mensual [año/mes]' },
    { cmd: '/tc',        desc: 'Tipo de cambio USD/MXN (Banxico)' },
    { cmd: '/mve',       desc: 'Manifestaciones de valor abiertas' },
    { cmd: '/tasks',     desc: 'Tareas pendientes GSD' },
    { cmd: '/ayuda',     desc: 'Lista completa de comandos' },
  ]

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-sky-100 rounded-xl flex items-center justify-center">
          <Send size={22} className="text-sky-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Telegram Bot</h1>
          <p className="text-sm text-gray-500">Mystic Bot · Acceso a todas las funciones desde Telegram</p>
        </div>
      </div>

      {/* Estado del bot */}
      <Card className="p-6">
        <div className="flex items-center gap-4">
          <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
            loading ? 'bg-gray-100 animate-pulse' : status?.api === 'ok' ? 'bg-sky-100' : 'bg-red-100'
          }`}>
            {!loading && (status?.api === 'ok'
              ? <CheckCircle size={28} className="text-sky-600" />
              : <XCircle size={28} className="text-red-500" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-lg font-semibold text-gray-900">
              {loading ? 'Verificando...' : status?.api === 'ok' ? 'Bot Activo' : 'Bot Offline'}
            </p>
            <p className="text-sm text-gray-400">
              {status?.api === 'ok' ? 'API conectada · DB y Redis OK' : 'Verificar que mystic_bot esté corriendo'}
            </p>
          </div>
          <a
            href={botUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-sky-500 hover:bg-sky-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <ExternalLink size={14} />
            Abrir Bot
          </a>
        </div>
      </Card>

      {/* Indicadores del sistema */}
      {status && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'API', val: status.api },
            { label: 'Base de Datos', val: status.db },
            { label: 'Redis', val: status.redis },
          ].map(({ label, val }) => (
            <Card key={label} className="p-4 text-center">
              <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${val === 'ok' ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <p className="text-xs text-gray-500">{label}</p>
              <p className={`text-sm font-semibold mt-0.5 ${val === 'ok' ? 'text-emerald-600' : 'text-red-500'}`}>
                {val === 'ok' ? 'OK' : 'ERROR'}
              </p>
            </Card>
          ))}
        </div>
      )}

      {/* Comandos */}
      <Card className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <Terminal size={16} className="text-gray-500" />
          <h2 className="text-sm font-semibold text-gray-700">Comandos disponibles</h2>
        </div>
        <div className="space-y-1">
          {COMANDOS.map(({ cmd, desc }) => (
            <div key={cmd} className="flex items-start gap-3 py-2 border-b border-gray-50 last:border-0">
              <code className="text-xs bg-gray-100 text-brand-700 px-2 py-1 rounded font-mono shrink-0">{cmd}</code>
              <p className="text-sm text-gray-600">{desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Info */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Información técnica</h2>
        <div className="space-y-2 text-sm">
          {[
            ['Framework', 'python-telegram-bot v21'],
            ['Brain IA', 'Integrado vía /api/brain/ask'],
            ['Autenticación', 'JWT por sesión (en memoria)'],
            ['Modo', 'Polling'],
            ['Sesiones', '"telegram:{user_id}"'],
          ].map(([label, val]) => (
            <div key={label} className="flex justify-between py-1.5 border-b border-gray-50 last:border-0">
              <span className="text-gray-500">{label}</span>
              <span className="font-medium text-gray-700">{val}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
