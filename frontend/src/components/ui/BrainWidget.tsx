'use client'

import { useState, useRef, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { api, BrainResponse } from '@/lib/api'
import { Brain, X, Send, ChevronRight, RefreshCw } from 'lucide-react'
import { getUser } from '@/lib/auth'

interface Msg { role: 'user' | 'assistant'; text: string }

// FAQ contextual por ruta
const FAQ_MAP: Record<string, string[]> = {
  '/dashboard':  [
    '¿Cómo interpreto el margen bruto?',
    '¿Qué significa el semáforo amarillo?',
    '¿Cuándo debo preocuparme por cuentas por cobrar?',
  ],
  '/facturas': [
    '¿Cómo cargo un CFDI XML?',
    '¿Qué diferencia hay entre ingreso y egreso?',
    '¿Cómo cancelo una factura en el SAT?',
  ],
  '/nomina': [
    '¿Cómo calculo el ISR de nómina?',
    '¿Qué cuotas IMSS debo pagar como patrón?',
    '¿Qué es el complemento de nómina 1.2?',
  ],
  '/cierre': [
    '¿Qué incluye el cierre mensual?',
    '¿Cómo se calcula el ISR de pago provisional?',
    '¿Qué es el EBITDA y para qué sirve?',
  ],
  '/mve': [
    '¿Qué es la Manifestación de Valor?',
    '¿Cuándo aplica el RGCE anti-multa?',
    '¿Qué métodos de valoración acepta el SAT?',
  ],
  '/brain': [],
  '/whatsapp': [
    '¿Cómo reconecto el WhatsApp?',
    '¿Puedo agregar más números a la whitelist?',
  ],
  '/telegram': [
    '¿Cómo inicio sesión en el bot?',
    '¿Qué datos puedo consultar desde Telegram?',
  ],
}

export default function BrainWidget() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const pathname = usePathname()
  const bottomRef = useRef<HTMLDivElement>(null)
  const user = getUser()

  // Detectar ruta base para FAQ
  const routeKey = Object.keys(FAQ_MAP).find(k => pathname.includes(k)) || '/dashboard'
  const sugerencias = FAQ_MAP[routeKey] || []

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs, open])

  async function enviar(texto?: string) {
    const pregunta = (texto || input).trim()
    if (!pregunta || loading) return
    setInput('')
    setMsgs(m => [...m, { role: 'user', text: pregunta }])
    setLoading(true)
    try {
      const res = await api.post<BrainResponse>('/api/brain/ask', {
        question: pregunta,
        context: user?.tenant_id || 'fiscal',
        session_id: `widget:${user?.tenant_id || 'anon'}`,
      })
      setMsgs(m => [...m, { role: 'assistant', text: res.respuesta }])
    } catch {
      setMsgs(m => [...m, { role: 'assistant', text: 'No pude consultar el Brain IA. Intenta de nuevo.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Widget flotante */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-violet-600 hover:bg-violet-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-105 z-50"
          title="Preguntar al Brain IA"
        >
          <Brain size={24} />
          {sugerencias.length > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-xs flex items-center justify-center">
              {sugerencias.length}
            </span>
          )}
        </button>
      )}

      {/* Panel del widget */}
      {open && (
        <div className="fixed bottom-6 right-6 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50 max-h-[560px]">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-violet-600 rounded-t-2xl">
            <div className="flex items-center gap-2 text-white">
              <Brain size={18} />
              <div>
                <p className="text-sm font-semibold">Brain IA</p>
                <p className="text-xs opacity-70">Asistente Mystic</p>
              </div>
            </div>
            <button onClick={() => setOpen(false)} className="text-white/80 hover:text-white">
              <X size={18} />
            </button>
          </div>

          {/* Sugerencias */}
          {msgs.length === 0 && sugerencias.length > 0 && (
            <div className="px-3 py-3 border-b border-gray-100">
              <p className="text-xs text-gray-400 mb-2">Preguntas frecuentes en esta página:</p>
              <div className="space-y-1">
                {sugerencias.map(s => (
                  <button
                    key={s}
                    onClick={() => enviar(s)}
                    className="w-full text-left flex items-center gap-2 text-xs text-gray-600 hover:text-violet-600 hover:bg-violet-50 px-2 py-1.5 rounded-lg transition-colors"
                  >
                    <ChevronRight size={12} className="shrink-0" />
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Mensajes */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-[180px]">
            {msgs.length === 0 && sugerencias.length === 0 && (
              <p className="text-xs text-gray-400 text-center py-4">Escribe una pregunta fiscal o contable...</p>
            )}
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs ${
                  m.role === 'user' ? 'bg-violet-600 text-white' : 'bg-gray-100 text-gray-800'
                }`}>
                  <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-xl px-3 py-2 flex items-center gap-1.5">
                  <RefreshCw size={11} className="text-gray-400 animate-spin" />
                  <span className="text-xs text-gray-400">Consultando...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-3 py-3 border-t border-gray-100">
            <form onSubmit={e => { e.preventDefault(); enviar() }} className="flex gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Pregunta al Brain IA..."
                className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-violet-400"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-violet-600 hover:bg-violet-700 disabled:opacity-40 text-white rounded-xl px-3 py-2 transition-colors"
              >
                <Send size={13} />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
