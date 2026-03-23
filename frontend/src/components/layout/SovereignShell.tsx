'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { getUser, logout } from '@/lib/auth'
import {
  Send, FileText, Calculator, Users, Package, Brain,
  Zap, ChevronRight, LogOut, LayoutDashboard, Building2,
  Receipt, CheckSquare, MessageCircle, ShieldCheck,
  CreditCard, Loader2, ThumbsUp, ThumbsDown, X,
  Bot, Sparkles, BookUser,
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

// ── Types ────────────────────────────────────────────────────────────
interface ChatMsg {
  id: string
  role: 'user' | 'ai' | 'system'
  text: string
  fuente?: string
  cached?: boolean
  module?: string   // 'facturas' | 'cierre' | 'nomina' etc
  timestamp: Date
}

// ── Quick commands ───────────────────────────────────────────────────
const QUICK_CMDS = [
  { label: 'Brain IA',       icon: Brain,       cmd: '¿Qué puedes hacer por mí?' },
  { label: 'Nueva Factura',  icon: FileText,    cmd: '/facturas' },
  { label: 'Cierre Mes',     icon: Calculator,  cmd: '/cierre' },
  { label: 'Nómina',         icon: Users,       cmd: '/nomina' },
  { label: 'MVE / Aduanas',  icon: Package,     cmd: '/mve' },
  { label: 'Estado',         icon: Zap,         cmd: '/status' },
]

// ── Nav items for icon dock ──────────────────────────────────────────
const DOCK_ITEMS = [
  { href: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/facturas',   icon: FileText,         label: 'Facturas' },
  { href: '/nomina',     icon: Users,             label: 'Nómina' },
  { href: '/cierre',     icon: Calculator,        label: 'Cierre' },
  { href: '/mve',        icon: Package,           label: 'MVE' },
  { href: '/directorio', icon: Building2,          label: 'Directorio' },
  { href: '/resico',     icon: Receipt,            label: 'RESICO' },
  { href: '/contador',   icon: BookUser,           label: 'Clientes' },
  { href: '/tasks',      icon: CheckSquare,        label: 'Tareas' },
  { href: '/brain',      icon: Brain,              label: 'Brain IA' },
  { href: '/whatsapp',   icon: MessageCircle,      label: 'WhatsApp' },
  { href: '/admin',      icon: ShieldCheck,        label: 'Admin' },
  { href: '/billing',    icon: CreditCard,         label: 'Billing' },
]

const MODULE_ROUTES: Record<string, string> = {
  '/facturas': '/facturas',
  '/cierre':   '/cierre',
  '/nomina':   '/nomina',
  '/mve':      '/mve',
  '/status':   '/dashboard',
  '/admin':    '/admin',
  '/resico':   '/resico',
  '/tareas':   '/tasks',
  '/tasks':    '/tasks',
  '/brain':    '/brain',
}

const MODULE_NAMES: Record<string, string> = {
  '/facturas': 'Módulo de Facturas',
  '/cierre':   'Cierre Mensual',
  '/nomina':   'Nómina',
  '/mve':      'MVE · Aduanas',
  '/status':   'Dashboard Estado',
  '/resico':   'RESICO',
  '/tareas':   'Tareas',
  '/tasks':    'Tareas',
  '/brain':    'Brain IA',
}

function mkId() { return Math.random().toString(36).slice(2) }

// ── Thinking dots ────────────────────────────────────────────────────
function ThinkingDots() {
  return (
    <div className="flex items-center gap-1 px-1 py-0.5">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-sovereign-gold"
          style={{ animation: `thinking 1.4s ease-in-out ${i * 0.2}s infinite` }}
        />
      ))}
    </div>
  )
}

// ── Main component ───────────────────────────────────────────────────
export default function SovereignShell({ children }: { children: React.ReactNode }) {
  const path = usePathname()
  const user = getUser()
  const rol  = user?.rol || 'contador'

  const [msgs, setMsgs]         = useState<ChatMsg[]>([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [shellOpen, setShellOpen] = useState(false)
  const [sessionId]             = useState(() => `sovereign:${Date.now()}`)
  const [dockOpen, setDockOpen] = useState(false)
  const bottomRef               = useRef<HTMLDivElement>(null)
  const inputRef                = useRef<HTMLInputElement>(null)

  // Welcome message
  useEffect(() => {
    const nombre = user?.nombre?.split(' ')[0] || 'Comandante'
    setMsgs([{
      id: mkId(),
      role: 'ai',
      text: `Bienvenido, ${nombre}.\n\nSoy MYSTIC — tu sistema soberano de inteligencia contable. Puedes escribirme cualquier pregunta fiscal, o usar comandos como /facturas, /cierre, /nomina para acceder a los módulos.\n\nEl sistema está operando con ${user?.tenant_id || 'tu empresa'}.`,
      timestamp: new Date(),
    }])
  }, []) // eslint-disable-line

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, loading])

  const sendMsg = useCallback(async (texto?: string) => {
    const q = (texto ?? input).trim()
    if (!q || loading) return
    setInput('')
    inputRef.current?.focus()

    // Check if it's a module command
    const modRoute = MODULE_ROUTES[q.toLowerCase()]
    if (modRoute) {
      setMsgs(m => [...m,
        { id: mkId(), role: 'user', text: q, timestamp: new Date() },
        {
          id: mkId(), role: 'system', text: '',
          module: modRoute,
          timestamp: new Date(),
        },
      ])
      setShellOpen(false)
      window.location.href = `/panel${modRoute}`
      return
    }

    setMsgs(m => [...m, { id: mkId(), role: 'user', text: q, timestamp: new Date() }])
    setLoading(true)

    try {
      const res = await api.post<{ respuesta: string; fuente?: string; cached?: boolean }>(
        '/api/brain/ask',
        { question: q, context: user?.tenant_id || 'fiscal', session_id: sessionId }
      )
      setMsgs(m => [...m, {
        id: mkId(),
        role: 'ai',
        text: res.respuesta,
        fuente: res.fuente,
        cached: res.cached,
        timestamp: new Date(),
      }])
    } catch {
      setMsgs(m => [...m, {
        id: mkId(), role: 'ai',
        text: 'No pude conectar con el Brain IA. Verifica el estado del sistema.',
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, sessionId, user])

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMsg() }
    if (e.key === 'Escape') setShellOpen(false)
  }

  // Close shell on overlay click
  const overlayRef = useRef<HTMLDivElement>(null)

  const isActive = (href: string) => path.includes(href)

  return (
    <div className="flex min-h-screen bg-sovereign-bg">

      {/* ── Left Icon Dock ─────────────────────────────────────── */}
      <aside className="hidden md:flex fixed inset-y-0 left-0 w-14 bg-sovereign-surface flex-col items-center py-4 z-40 border-r border-sovereign-border">
        {/* Logo orb */}
        <button
          onClick={() => setShellOpen(s => !s)}
          className={clsx(
            'w-9 h-9 rounded-full flex items-center justify-center mb-6 transition-all',
            shellOpen
              ? 'bg-sovereign-gold text-sovereign-bg gold-glow'
              : 'bg-sovereign-card border border-sovereign-border text-sovereign-gold hover:border-sovereign-gold'
          )}
          title="Abrir Shell Soberano"
        >
          <Zap size={16} />
        </button>

        {/* Nav icons */}
        <nav className="flex-1 flex flex-col gap-1 w-full px-2 overflow-y-auto">
          {DOCK_ITEMS.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              title={label}
              className={clsx(
                'w-10 h-10 mx-auto rounded-xl flex items-center justify-center transition-all group relative',
                isActive(href)
                  ? 'bg-sovereign-gold text-sovereign-bg'
                  : 'text-sovereign-muted hover:text-sovereign-gold hover:bg-sovereign-card'
              )}
            >
              <Icon size={18} />
              {/* Tooltip */}
              <span className="absolute left-12 px-2 py-1 bg-sovereign-card border border-sovereign-border text-sovereign-text text-xs rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                {label}
              </span>
            </Link>
          ))}
        </nav>

        {/* Logout */}
        <button
          onClick={logout}
          title="Salir"
          className="w-10 h-10 rounded-xl flex items-center justify-center text-sovereign-muted hover:text-red-400 hover:bg-sovereign-card transition-all"
        >
          <LogOut size={16} />
        </button>
      </aside>

      {/* ── Main Content ────────────────────────────────────────── */}
      <div className="flex-1 md:ml-14 flex flex-col min-h-screen">

        {/* Top header */}
        <header className="h-12 flex items-center justify-between px-4 md:px-6 border-b border-sovereign-border bg-sovereign-surface/60 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-3">
            {/* Mobile logo */}
            <button
              onClick={() => setShellOpen(s => !s)}
              className="md:hidden w-7 h-7 rounded-full bg-sovereign-gold flex items-center justify-center"
            >
              <Zap size={14} className="text-sovereign-bg" />
            </button>
            <span className="text-sovereign-gold font-semibold text-sm tracking-widest uppercase">Mystic</span>
            <span className="hidden md:inline text-sovereign-border">·</span>
            <span className="hidden md:inline text-sovereign-muted text-xs">{user?.tenant_id || 'Sistema Soberano'}</span>
          </div>

          <div className="flex items-center gap-3">
            {/* Status dot */}
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-gold-pulse" />
              <span className="text-xs text-sovereign-muted hidden md:inline">online</span>
            </div>
            {/* User pill */}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-sovereign-card border border-sovereign-border">
              <span className="text-xs text-sovereign-text font-medium">{user?.nombre?.split(' ')[0] || user?.email}</span>
              <span className={clsx(
                'text-xs px-1.5 py-0.5 rounded font-semibold',
                rol === 'admin' ? 'bg-purple-900/50 text-purple-300' :
                rol === 'ceo'   ? 'text-sovereign-gold' :
                                  'text-sovereign-muted'
              )}>
                {rol.toUpperCase()}
              </span>
            </div>
            {/* Open shell btn */}
            <button
              onClick={() => setShellOpen(s => !s)}
              className={clsx(
                'hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border',
                shellOpen
                  ? 'bg-sovereign-gold/10 border-sovereign-gold text-sovereign-gold'
                  : 'bg-sovereign-card border-sovereign-border text-sovereign-muted hover:border-sovereign-gold hover:text-sovereign-gold'
              )}
            >
              <Bot size={13} />
              <span>Shell</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4 md:p-6">
          {children}
        </main>
      </div>

      {/* ── Sovereign Shell Overlay ──────────────────────────────── */}
      {shellOpen && (
        <>
          {/* Backdrop */}
          <div
            ref={overlayRef}
            className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40"
            onClick={() => setShellOpen(false)}
          />

          {/* Shell panel — slides from right */}
          <div className="fixed right-0 top-0 bottom-0 w-full md:w-[480px] z-50 flex flex-col bg-sovereign-surface border-l border-sovereign-border animate-fade-up">

            {/* Shell header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-sovereign-border">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-sovereign-gold flex items-center justify-center">
                  <Sparkles size={14} className="text-sovereign-bg" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-sovereign-text">Mystic Brain IA</p>
                  <p className="text-xs text-sovereign-muted">DeepSeek R1 · RAG contable</p>
                </div>
              </div>
              <button
                onClick={() => setShellOpen(false)}
                className="w-7 h-7 rounded-lg flex items-center justify-center text-sovereign-muted hover:text-sovereign-text hover:bg-sovereign-card transition-all"
              >
                <X size={15} />
              </button>
            </div>

            {/* Messages stream */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
              {msgs.map((msg) => (
                <div
                  key={msg.id}
                  className={clsx('flex animate-fade-up', msg.role === 'user' ? 'justify-end' : 'justify-start')}
                >
                  {msg.role !== 'user' && (
                    <div className="w-6 h-6 rounded-full bg-sovereign-gold/20 border border-sovereign-gold/30 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                      <Zap size={11} className="text-sovereign-gold" />
                    </div>
                  )}

                  <div className={clsx(
                    'max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                    msg.role === 'user' ? 'msg-user text-sovereign-text' : 'msg-ai text-sovereign-text'
                  )}>
                    <p className="whitespace-pre-wrap">{msg.text}</p>

                    {/* AI feedback row */}
                    {msg.role === 'ai' && msg.fuente && (
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-xs text-sovereign-muted flex items-center gap-1">
                          <Zap size={9} className="text-sovereign-gold-dim" />
                          {msg.fuente}{msg.cached ? ' · caché' : ''}
                        </span>
                        <div className="flex gap-1">
                          <button
                            onClick={() => api.post('/api/brain/feedback', {
                              pregunta: msgs[msgs.indexOf(msg) - 1]?.text || '',
                              respuesta: msg.text, rating: 1,
                            }).catch(() => null)}
                            className="p-1 rounded text-sovereign-muted hover:text-emerald-400 transition-colors"
                          >
                            <ThumbsUp size={11} />
                          </button>
                          <button
                            onClick={() => api.post('/api/brain/feedback', {
                              pregunta: msgs[msgs.indexOf(msg) - 1]?.text || '',
                              respuesta: msg.text, rating: -1,
                            }).catch(() => null)}
                            className="p-1 rounded text-sovereign-muted hover:text-red-400 transition-colors"
                          >
                            <ThumbsDown size={11} />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Thinking indicator */}
              {loading && (
                <div className="flex justify-start animate-fade-up">
                  <div className="w-6 h-6 rounded-full bg-sovereign-gold/20 border border-sovereign-gold/30 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
                    <Zap size={11} className="text-sovereign-gold animate-gold-pulse" />
                  </div>
                  <div className="msg-ai rounded-2xl px-4 py-3">
                    <ThinkingDots />
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Quick commands */}
            <div className="px-4 py-2 flex gap-2 flex-wrap border-t border-sovereign-border/50">
              {QUICK_CMDS.map(({ label, icon: Icon, cmd }) => (
                <button
                  key={label}
                  onClick={() => sendMsg(cmd)}
                  disabled={loading}
                  className="cmd-chip"
                >
                  <Icon size={12} />
                  {label}
                </button>
              ))}
            </div>

            {/* Input bar */}
            <div className="px-4 py-4 border-t border-sovereign-border">
              <div className="flex gap-2 items-end">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKey}
                  placeholder="Pregunta, comando (/cierre, /facturas) o consulta fiscal..."
                  className="sovereign-input flex-1"
                  disabled={loading}
                  autoFocus
                />
                <button
                  onClick={() => sendMsg()}
                  disabled={loading || !input.trim()}
                  className={clsx(
                    'w-10 h-10 rounded-xl flex items-center justify-center transition-all flex-shrink-0',
                    loading || !input.trim()
                      ? 'bg-sovereign-card border border-sovereign-border text-sovereign-muted'
                      : 'bg-sovereign-gold text-sovereign-bg hover:opacity-90 gold-glow'
                  )}
                >
                  {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>
              <p className="text-xs text-sovereign-muted mt-2">
                <kbd className="px-1 py-0.5 rounded bg-sovereign-card border border-sovereign-border text-xs">Enter</kbd> enviar
                · <kbd className="px-1 py-0.5 rounded bg-sovereign-card border border-sovereign-border text-xs">Esc</kbd> cerrar
                · sesión {sessionId.slice(-6)}
              </p>
            </div>
          </div>
        </>
      )}

      {/* Mobile: floating Shell button */}
      {!shellOpen && (
        <button
          onClick={() => setShellOpen(true)}
          className="md:hidden fixed bottom-6 right-6 w-14 h-14 rounded-full bg-sovereign-gold flex items-center justify-center gold-glow z-40 shadow-lg"
        >
          <Bot size={22} className="text-sovereign-bg" />
        </button>
      )}
    </div>
  )
}
