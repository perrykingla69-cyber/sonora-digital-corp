'use client'

import { useState, useRef, useEffect } from 'react'
import { api, BrainResponse } from '@/lib/api'
import { Card } from '@/components/ui/Card'
import { Brain, Send, RefreshCw, ThumbsUp, ThumbsDown, Zap } from 'lucide-react'
import { getUser } from '@/lib/auth'

interface Msg { role: 'user' | 'assistant'; text: string; fuente?: string; cached?: boolean; id?: string }

const SUGERENCIAS = [
  '¿Cuál es la tasa de IVA en México?',
  '¿Cuándo debo presentar mi declaración mensual?',
  '¿Cómo calculo el ISR de personas morales?',
  '¿Qué es el CFDI 4.0 y qué campos son obligatorios?',
  '¿Cuál es la tasa IGI para filtros industriales?',
  '¿Qué es la DTA y cuánto cuesta en 2026?',
]

export default function BrainPage() {
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `api:dashboard:${Date.now()}`)
  const bottomRef = useRef<HTMLDivElement>(null)
  const user = getUser()

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs])

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
        session_id: sessionId,
      })
      setMsgs(m => [...m, {
        role: 'assistant',
        text: res.respuesta,
        fuente: res.fuente,
        cached: res.cached,
        id: Date.now().toString(),
      }])
    } catch (e: unknown) {
      setMsgs(m => [...m, { role: 'assistant', text: `Error: ${e instanceof Error ? e.message : 'Sin respuesta'}` }])
    } finally {
      setLoading(false)
    }
  }

  async function feedback(pregunta: string, respuesta: string, rating: 1 | -1) {
    await api.post('/api/brain/feedback', { pregunta, respuesta, rating }).catch(() => null)
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-violet-100 rounded-xl flex items-center justify-center">
          <Brain size={22} className="text-violet-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Brain IA</h1>
          <p className="text-sm text-gray-500">Asistente fiscal · RAG 4 capas · DeepSeek R1</p>
        </div>
      </div>

      {/* Sugerencias si no hay mensajes */}
      {msgs.length === 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">Preguntas frecuentes:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {SUGERENCIAS.map(s => (
              <button
                key={s}
                onClick={() => enviar(s)}
                className="text-left text-sm px-4 py-3 rounded-xl border border-gray-200 bg-white hover:border-violet-300 hover:bg-violet-50 transition-colors text-gray-700"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat */}
      <Card className="min-h-96">
        <div className="h-[460px] overflow-y-auto p-4 space-y-4">
          {msgs.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                m.role === 'user'
                  ? 'bg-brand-600 text-white rounded-tr-sm'
                  : 'bg-gray-50 text-gray-800 border border-gray-200 rounded-tl-sm'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                {m.role === 'assistant' && m.fuente && (
                  <div className="mt-2 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-1.5">
                      <Zap size={11} className="text-gray-400" />
                      <span className="text-xs text-gray-400">{m.fuente}{m.cached ? ' · caché' : ''}</span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => feedback(msgs[i - 1]?.text || '', m.text, 1)}
                        className="p-1 rounded hover:bg-emerald-50 text-gray-400 hover:text-emerald-600 transition-colors"
                        title="Útil"
                      >
                        <ThumbsUp size={12} />
                      </button>
                      <button
                        onClick={() => feedback(msgs[i - 1]?.text || '', m.text, -1)}
                        className="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                        title="No útil"
                      >
                        <ThumbsDown size={12} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                <RefreshCw size={14} className="text-gray-400 animate-spin" />
                <span className="text-sm text-gray-400">Consultando Brain IA...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-4">
          <form onSubmit={e => { e.preventDefault(); enviar() }} className="flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Escribe tu pregunta fiscal o contable..."
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-xl px-4 py-2.5 transition-colors"
            >
              <Send size={16} />
            </button>
          </form>
          <p className="text-xs text-gray-400 mt-2">Contexto: {user?.tenant_id || 'fiscal'} · Sesión: {sessionId.slice(-8)}</p>
        </div>
      </Card>
    </div>
  )
}
