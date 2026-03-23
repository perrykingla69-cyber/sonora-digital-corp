'use client'

import { useState, useRef, useEffect } from 'react'
import { api, BrainResponse } from '@/lib/api'
import { Zap, Send, RefreshCw, ThumbsUp, ThumbsDown, Sparkles, Loader2 } from 'lucide-react'
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
  const inputRef = useRef<HTMLInputElement>(null)
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
    <div className="flex flex-col h-[calc(100vh-7rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-full bg-sovereign-gold/10 border border-sovereign-gold/30 flex items-center justify-center">
          <Sparkles size={17} className="text-sovereign-gold" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-sovereign-text">Brain IA</h1>
          <p className="text-xs text-sovereign-muted">Asistente fiscal · RAG 4 capas · DeepSeek R1</p>
        </div>
      </div>

      {/* Suggestions */}
      {msgs.length === 0 && (
        <div className="mb-4 space-y-2">
          <p className="text-xs text-sovereign-muted uppercase tracking-wider">Preguntas frecuentes</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {SUGERENCIAS.map(s => (
              <button
                key={s}
                onClick={() => enviar(s)}
                className="text-left text-xs px-4 py-3 rounded-xl border border-sovereign-border
                           bg-sovereign-card text-sovereign-muted
                           hover:border-sovereign-gold/40 hover:text-sovereign-text
                           transition-all"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat stream */}
      <div className="flex-1 overflow-y-auto module-card rounded-xl flex flex-col">
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {msgs.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-up`}>
              {m.role === 'assistant' && (
                <div className="w-6 h-6 rounded-full bg-sovereign-gold/10 border border-sovereign-gold/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                  <Zap size={10} className="text-sovereign-gold" />
                </div>
              )}
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                m.role === 'user' ? 'msg-user text-sovereign-text' : 'msg-ai text-sovereign-text'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                {m.role === 'assistant' && m.fuente && (
                  <div className="mt-2 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-1.5">
                      <Zap size={9} className="text-sovereign-muted" />
                      <span className="text-xs text-sovereign-muted">{m.fuente}{m.cached ? ' · caché' : ''}</span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => feedback(msgs[i - 1]?.text || '', m.text, 1)}
                        className="p-1 rounded text-sovereign-muted hover:text-emerald-400 transition-colors"
                        title="Útil"
                      >
                        <ThumbsUp size={11} />
                      </button>
                      <button
                        onClick={() => feedback(msgs[i - 1]?.text || '', m.text, -1)}
                        className="p-1 rounded text-sovereign-muted hover:text-red-400 transition-colors"
                        title="No útil"
                      >
                        <ThumbsDown size={11} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start animate-fade-up">
              <div className="w-6 h-6 rounded-full bg-sovereign-gold/10 border border-sovereign-gold/20 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                <Zap size={10} className="text-sovereign-gold animate-gold-pulse" />
              </div>
              <div className="msg-ai rounded-2xl px-4 py-3 flex items-center gap-2">
                <RefreshCw size={13} className="text-sovereign-muted animate-spin" />
                <span className="text-sm text-sovereign-muted">Consultando Brain IA...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-sovereign-border p-4">
          <form onSubmit={e => { e.preventDefault(); enviar() }} className="flex gap-2">
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Escribe tu pregunta fiscal o contable..."
              className="sovereign-input flex-1"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all flex-shrink-0 ${
                loading || !input.trim()
                  ? 'bg-sovereign-card border border-sovereign-border text-sovereign-muted'
                  : 'bg-sovereign-gold text-sovereign-bg hover:opacity-90 gold-glow'
              }`}
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
            </button>
          </form>
          <p className="text-xs text-sovereign-muted mt-2">
            Contexto: {user?.tenant_id || 'fiscal'} · Sesión: {sessionId.slice(-8)}
          </p>
        </div>
      </div>
    </div>
  )
}
