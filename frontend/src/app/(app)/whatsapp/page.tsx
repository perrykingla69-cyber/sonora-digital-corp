'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { MessageCircle, Wifi, WifiOff, RefreshCw, Phone, ExternalLink } from 'lucide-react'

interface WaStatus { connected: boolean; phone?: string; qr_available?: boolean; uptime?: number }

const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'https://sonoradigitalcorp.com'

export default function WhatsAppPage() {
  const [status, setStatus] = useState<WaStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  async function cargar() {
    try {
      const res = await api.get<WaStatus>('/api/wa/status')
      setStatus(res)
    } catch {
      setStatus({ connected: false })
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => { cargar() }, [])

  function refresh() { setRefreshing(true); cargar() }

  const qrUrl = `${API_BASE}/whatsapp/qr?apikey=MysticWA2026%21`

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
            <MessageCircle size={22} className="text-emerald-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">WhatsApp</h1>
            <p className="text-sm text-gray-500">Estado de conexión · Hermes WA (Baileys)</p>
          </div>
        </div>
        <button
          onClick={refresh}
          disabled={refreshing}
          className="flex items-center gap-2 text-sm px-4 py-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
          Actualizar
        </button>
      </div>

      {/* Estado de conexión */}
      <Card className="p-6">
        <div className="flex items-center gap-4">
          {loading ? (
            <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center animate-pulse" />
          ) : status?.connected ? (
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center">
              <Wifi size={28} className="text-emerald-600" />
            </div>
          ) : (
            <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center">
              <WifiOff size={28} className="text-red-500" />
            </div>
          )}
          <div className="flex-1">
            <p className="text-lg font-semibold text-gray-900">
              {loading ? 'Verificando...' : status?.connected ? 'Conectado' : 'Desconectado'}
            </p>
            {status?.phone && (
              <div className="flex items-center gap-1.5 mt-1">
                <Phone size={13} className="text-gray-400" />
                <p className="text-sm text-gray-500">+52 {status.phone}</p>
              </div>
            )}
            {!loading && !status?.connected && (
              <p className="text-sm text-gray-400 mt-1">Escanea el QR para conectar</p>
            )}
          </div>
          <div className={`px-3 py-1.5 rounded-full text-xs font-semibold ${
            status?.connected ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
          }`}>
            {status?.connected ? 'ACTIVO' : 'OFFLINE'}
          </div>
        </div>
      </Card>

      {/* QR Code */}
      {!status?.connected && (
        <Card className="p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Escanear código QR</h2>
          <div className="flex flex-col items-center gap-4">
            <div className="bg-white border-2 border-gray-200 rounded-xl p-2">
              <img
                src={qrUrl}
                alt="WhatsApp QR"
                width={220}
                height={220}
                className="rounded-lg"
                onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
            </div>
            <p className="text-xs text-gray-400 text-center max-w-xs">
              Abre WhatsApp → Dispositivos vinculados → Vincular un dispositivo → Escanea este código
            </p>
            <a
              href={qrUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-brand-600 hover:underline"
            >
              <ExternalLink size={14} />
              Abrir QR en nueva pestaña
            </a>
          </div>
        </Card>
      )}

      {/* Info de configuración */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Configuración</h2>
        <div className="space-y-2 text-sm">
          {[
            ['Puerto', '3001'],
            ['Versión', 'Baileys 6.7.21'],
            ['Whitelist', '6622681111 (Nathaly) · 6623538272 (Marco)'],
            ['Brain IA', 'Activo — responde automáticamente'],
            ['Grupos', 'Ignorados (@g.us y @lid)'],
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
