'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import Link from 'next/link'
import { Countdown } from './countdown'
import {
  Brain, FileText, ShieldCheck, Zap, CheckCircle2,
  ArrowRight, Crown, Sparkles, Lock, Rocket,
} from 'lucide-react'

const API = '/api'

// ─── Logo SVG — Ojo Hermes ────────────────────────────────────────────────────
function HermesEyeLogo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
      <defs>
        <radialGradient id="eyeGold" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f0c842" />
          <stop offset="60%" stopColor="#D4AF37" />
          <stop offset="100%" stopColor="#8B7520" />
        </radialGradient>
        <radialGradient id="irisGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#1a0a00" />
          <stop offset="40%" stopColor="#3d1f00" />
          <stop offset="100%" stopColor="#D4AF37" />
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <polygon points="50,4 96,86 4,86" fill="none" stroke="url(#eyeGold)" strokeWidth="2.5" filter="url(#glow)" />
      <polygon points="50,28 76,74 24,74" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      <polygon points="50,72 74,28 26,28" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      <ellipse cx="50" cy="54" rx="16" ry="10" fill="none" stroke="url(#eyeGold)" strokeWidth="1.5" />
      <circle cx="50" cy="54" r="7" fill="url(#irisGrad)" />
      <circle cx="50" cy="54" r="3" fill="#0a0500" />
      <circle cx="52" cy="52" r="1" fill="#D4AF37" opacity="0.8" />
      <path d="M34,54 Q50,44 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
      <path d="M34,54 Q50,64 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
    </svg>
  )
}

// ─── Particle canvas ──────────────────────────────────────────────────────────
function ParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')!
    let raf: number
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight }
    resize()
    window.addEventListener('resize', resize)
    const pts = Array.from({ length: 50 }, () => ({
      x: Math.random() * canvas.width, y: Math.random() * canvas.height,
      vx: (Math.random() - .5) * .3, vy: (Math.random() - .5) * .3,
      r: Math.random() * 1.2 + .4, a: Math.random(),
    }))
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0) p.x = canvas.width; if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height; if (p.y > canvas.height) p.y = 0
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(212,175,55,${p.a * .4})`; ctx.fill()
      })
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [])
  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none" style={{ zIndex: 0 }} />
}

// ─── Instant Access Form ──────────────────────────────────────────────────────
function AccesoInstantaneo() {
  const [email, setEmail] = useState('')
  const [estado, setEstado] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle')
  const [msg, setMsg] = useState('')

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.includes('@')) { setMsg('Ingresa un email válido'); setEstado('error'); return }
    setEstado('loading')
    try {
      const res = await fetch(`${API}/auth/trial`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      })
      const data = await res.json()
      if (!res.ok) {
        if (res.status === 409) {
          setMsg('Ya tienes cuenta. Entra con tu contraseña.')
          setEstado('error')
          setTimeout(() => { window.location.href = '/login' }, 1800)
          return
        }
        throw new Error(data.detail || 'Error al crear acceso')
      }
      localStorage.setItem('hermes_token', data.access_token)
      if (data.password_temp) localStorage.setItem('hermes_pass_hint', data.password_temp)
      setEstado('ok')
      setMsg(data.nuevo ? '¡Listo! Entrando al panel...' : 'Bienvenido de vuelta. Redirigiendo...')
      setTimeout(() => { window.location.href = '/panel' }, 1200)
    } catch (err: any) {
      setMsg(err.message || 'Error de conexión')
      setEstado('error')
    }
  }, [email])

  if (estado === 'ok') {
    return (
      <div className="flex items-center gap-3 bg-green-500/20 border border-green-500/40 rounded-2xl px-6 py-4 max-w-md mx-auto">
        <CheckCircle2 className="w-6 h-6 text-green-400 shrink-0" />
        <p className="text-green-300 font-semibold">{msg}</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto space-y-3">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={e => { setEmail(e.target.value); setEstado('idle'); setMsg('') }}
          placeholder="tu@email.com"
          required
          className="flex-1 px-5 py-3.5 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] transition text-base"
        />
        <button
          type="submit"
          disabled={estado === 'loading'}
          className="px-6 py-3.5 rounded-xl bg-[#D4AF37] text-black font-bold text-base hover:bg-[#f0c842] transition disabled:opacity-60 whitespace-nowrap flex items-center gap-2"
        >
          {estado === 'loading'
            ? <span className="inline-block w-4 h-4 border-2 border-black/40 border-t-black rounded-full animate-spin" />
            : <><Rocket className="w-4 h-4" /> Entrar gratis</>}
        </button>
      </div>
      {msg && (
        <p className={`text-sm text-center ${estado === 'error' ? 'text-red-400' : 'text-white/60'}`}>{msg}</p>
      )}
      <p className="text-xs text-white/30 text-center">Sin tarjeta · Sin contraseña · Acceso inmediato hasta el 31 de marzo</p>
    </form>
  )
}

// ─── Features ─────────────────────────────────────────────────────────────────
const features = [
  { icon: Brain, title: 'Brain IA Contable', desc: 'Pregunta sobre RESICO, ISR, CFDI o cualquier obligación fiscal. Respuesta en segundos por Telegram o WhatsApp.' },
  { icon: FileText, title: 'Facturación CFDI 4.0', desc: 'Sube tu XML, registra ingresos y egresos, genera reportes mensuales. Compatible con SAT.' },
  { icon: ShieldCheck, title: 'Anti-multa MVE', desc: 'Semáforo verde/rojo para tu Manifestación de Valor en aduanas. Evita multas de hasta $300,000 MXN.' },
  { icon: Zap, title: 'Cierre mensual automático', desc: 'IVA, ISR y DIOT listos en un clic. Declaraciones RESICO calculadas sin esfuerzo.' },
]

// ─── Planes ───────────────────────────────────────────────────────────────────
const planes = [
  {
    nombre: 'Básico', precio: '$799', tag: null, color: 'border-white/10',
    items: ['Facturación CFDI 4.0', 'Declaraciones RESICO', 'Brain IA (100 consultas/mes)', 'Soporte Telegram'],
  },
  {
    nombre: 'Business', precio: '$1,499', tag: 'MÁS POPULAR', color: 'border-[#D4AF37]',
    items: ['Todo lo del Básico', 'Anti-multa MVE aduanas', 'Brain IA ilimitado', 'WhatsApp integrado', 'Content Factory', 'Academia completa'],
  },
  {
    nombre: 'Pro', precio: '$2,999', tag: null, color: 'border-white/10',
    items: ['Todo lo del Business', 'Multi-empresa (hasta 5)', 'DIOT + reportes fiscales completos', 'Contador IA dedicado', 'Onboarding personalizado'],
  },
]

// ═══════════════════════════════════════════════════════════════════════════════
export default function Home() {
  return (
    <div className="relative min-h-screen bg-[#0a0500] text-white overflow-x-hidden">
      <ParticleField />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <HermesEyeLogo size={32} />
          <span className="font-black text-lg tracking-wide text-[#D4AF37]">HERMES</span>
        </div>
        <Link href="/login" className="text-sm text-white/60 hover:text-white border border-white/20 hover:border-white/40 rounded-lg px-4 py-1.5 transition">
          Iniciar sesión
        </Link>
      </nav>

      {/* ── 1. HERO ──────────────────────────────────────────────────────────── */}
      <section className="relative z-10 min-h-[90vh] flex flex-col items-center justify-center text-center px-4 py-20">
        <div className="mb-8"><HermesEyeLogo size={72} /></div>

        <div className="mb-6 inline-flex items-center gap-2 bg-[#D4AF37]/15 border border-[#D4AF37]/30 rounded-full px-5 py-2">
          <Sparkles className="w-4 h-4 text-[#D4AF37]" />
          <span className="text-sm font-semibold text-[#D4AF37]">Acceso gratuito hasta el 31 de marzo</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black leading-tight mb-4 max-w-3xl">
          Tu contador IA.<br />
          <span className="text-[#D4AF37]">Sin mensualidades. Sin multas.</span>
        </h1>
        <p className="text-lg sm:text-xl text-white/60 mb-10 max-w-xl">
          Facturación CFDI, RESICO, anti-multa aduanal y Brain IA por WhatsApp — en un solo lugar.
        </p>

        <div className="mb-8 flex flex-col items-center gap-2">
          <p className="text-xs font-bold uppercase tracking-widest text-white/40">Acceso gratuito termina en</p>
          <Countdown />
        </div>

        <AccesoInstantaneo />

        <div className="mt-10 flex items-center gap-6 text-sm text-white/30">
          <span>✓ Sin tarjeta</span>
          <span>✓ Acceso inmediato</span>
          <span>✓ SAT compliant</span>
        </div>
      </section>

      {/* ── 2. QUÉ INCLUYE ───────────────────────────────────────────────────── */}
      <section className="relative z-10 py-20 px-4 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-xs font-bold uppercase tracking-widest text-[#D4AF37]/60 mb-3">Incluye en tu acceso gratuito</p>
          <h2 className="text-3xl sm:text-4xl font-black">Todo lo que necesita tu PYME</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-white/5 border border-white/10 rounded-2xl p-6 flex gap-4 hover:border-[#D4AF37]/30 transition">
              <div className="shrink-0 w-12 h-12 rounded-xl bg-[#D4AF37]/10 flex items-center justify-center">
                <Icon className="w-6 h-6 text-[#D4AF37]" />
              </div>
              <div>
                <h3 className="font-bold text-white mb-1">{title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-12 text-center"><AccesoInstantaneo /></div>
      </section>

      {/* ── 3. PLANES ────────────────────────────────────────────────────────── */}
      <section className="relative z-10 py-20 px-4 max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 mb-4">
            <Lock className="w-3.5 h-3.5 text-white/40" />
            <span className="text-xs text-white/40">A partir del 1 de abril</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-black">Elige tu plan</h2>
          <p className="text-white/40 mt-2">Registrándote hoy conservas tu precio de fundador.</p>
        </div>
        <div className="grid sm:grid-cols-3 gap-6">
          {planes.map(plan => (
            <div key={plan.nombre} className={`relative bg-white/5 border-2 ${plan.color} rounded-2xl p-6 flex flex-col ${plan.tag ? 'ring-1 ring-[#D4AF37]/40' : ''}`}>
              {plan.tag && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#D4AF37] text-black text-xs font-black px-4 py-1 rounded-full flex items-center gap-1">
                  <Crown className="w-3 h-3" />{plan.tag}
                </div>
              )}
              <div className="mb-6">
                <h3 className="font-black text-xl mb-1">{plan.nombre}</h3>
                <div className="flex items-end gap-1">
                  <span className="text-3xl font-black text-[#D4AF37]">{plan.precio}</span>
                  <span className="text-white/40 text-sm mb-1">/mes</span>
                </div>
              </div>
              <ul className="space-y-2.5 flex-1 mb-6">
                {plan.items.map(item => (
                  <li key={item} className="flex items-start gap-2 text-sm text-white/70">
                    <CheckCircle2 className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />{item}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => window.location.href = '/registro'}
                className={`w-full py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition ${plan.tag ? 'bg-[#D4AF37] text-black hover:bg-[#f0c842]' : 'bg-white/10 text-white hover:bg-white/20'}`}
              >
                Comenzar <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 text-center py-10 px-4 border-t border-white/5">
        <div className="flex items-center justify-center gap-2 mb-3">
          <HermesEyeLogo size={24} />
          <span className="font-black text-[#D4AF37]">HERMES</span>
        </div>
        <p className="text-xs text-white/20">© 2026 Sonora Digital Corp · Hermosillo, Sonora, México</p>
        <div className="flex items-center justify-center gap-6 mt-3 text-xs text-white/25">
          <Link href="/privacidad" className="hover:text-white/50 transition">Privacidad</Link>
          <Link href="/terminos" className="hover:text-white/50 transition">Términos</Link>
          <Link href="/login" className="hover:text-white/50 transition">Iniciar sesión</Link>
        </div>
      </footer>
    </div>
  )
}
