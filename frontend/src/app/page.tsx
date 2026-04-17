'use client'

import { useState } from 'react'
import { ChevronRight, Zap, Lock, BarChart3 } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPass, setLoginPass] = useState('')
  const [loginSlug, setLoginSlug] = useState('restaurante')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPass,
          tenant_slug: loginSlug,
        }),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Login fallido')
      }

      const { access_token } = await res.json()
      localStorage.setItem('hermes_token', access_token)
      localStorage.setItem('hermes_user', loginEmail)
      setSuccess('✅ Login exitoso. Redirigiendo...')

      setTimeout(() => {
        window.location.href = `/dashboard/${loginSlug}`
      }, 1000)
    } catch (err) {
      setError(`❌ ${err instanceof Error ? err.message : 'Error desconocido'}`)
    } finally {
      setLoading(false)
    }
  }

  const niches = [
    { slug: 'restaurante', name: '🍽️ Restaurantes', desc: 'Pedidos, reservas, inventario' },
    { slug: 'pastelero', name: '🎂 Panaderías', desc: 'Órdenes 24/7, confirmaciones automáticas' },
    { slug: 'abogado', name: '⚖️ Despachos', desc: 'Consultas iniciales, seguimiento de casos' },
    { slug: 'fontanero', name: '🔧 Servicios', desc: 'Agenda, presupuestos, notificaciones' },
    { slug: 'consultor', name: '💼 Consultores', desc: 'Proyectos, propuestas, análisis automático' },
    { slug: 'comercio', name: '🛒 E-commerce', desc: 'Soporte, recomendaciones, upsell IA' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
            HERMES OS
          </div>
          <nav className="hidden md:flex gap-8 text-sm">
            <a href="#niches" className="text-slate-300 hover:text-amber-400">Nichos</a>
            <a href="#features" className="text-slate-300 hover:text-amber-400">Características</a>
            <a href="#login" className="text-slate-300 hover:text-amber-400">Login</a>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 py-20 text-center">
        <div className="text-7xl mb-6 animate-bounce">🤖</div>
        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-amber-200 to-orange-400 bg-clip-text text-transparent">
          HERMES OS
        </h1>
        <p className="text-xl text-slate-300 mb-4">
          Orquestador IA para PYMEs mexicanas
        </p>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-12">
          Agentes IA que automatizan tu negocio. Operan 24/7 en Telegram y WhatsApp.
          <br />
          Sin código. Sin complicaciones. Listo en minutos.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <a
            href="#login"
            className="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-600 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-amber-500/50 transition transform hover:scale-105 flex items-center justify-center gap-2"
          >
            Acceder Ahora <ChevronRight size={20} />
          </a>
          <a
            href="#niches"
            className="px-8 py-4 border-2 border-amber-500 text-amber-400 font-bold rounded-xl hover:bg-amber-500/10 transition"
          >
            Explorar Nichos
          </a>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="bg-slate-700/40 border border-slate-600 rounded-lg p-4">
            <Zap className="w-6 h-6 text-amber-400 mx-auto mb-2" />
            <p className="text-sm text-slate-300">⚡ Instantánea</p>
          </div>
          <div className="bg-slate-700/40 border border-slate-600 rounded-lg p-4">
            <Lock className="w-6 h-6 text-amber-400 mx-auto mb-2" />
            <p className="text-sm text-slate-300">🔒 Segura</p>
          </div>
          <div className="bg-slate-700/40 border border-slate-600 rounded-lg p-4">
            <BarChart3 className="w-6 h-6 text-amber-400 mx-auto mb-2" />
            <p className="text-sm text-slate-300">📈 Escalable</p>
          </div>
        </div>
      </section>

      {/* Niches */}
      <section id="niches" className="max-w-6xl mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-16 text-white">
          Cualquier Negocio. Cualquier Industria.
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {niches.map((niche) => (
            <Link
              key={niche.slug}
              href={`/${niche.slug}`}
              className="group relative bg-gradient-to-br from-slate-700/60 to-slate-800/60 border border-slate-600 rounded-lg p-6 hover:border-amber-500/50 transition overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-amber-500/0 to-orange-500/0 group-hover:from-amber-500/5 group-hover:to-orange-500/5 transition" />
              <div className="relative z-10">
                <h3 className="text-2xl font-bold text-white mb-1">{niche.name}</h3>
                <p className="text-sm text-slate-300 mb-4">{niche.desc}</p>
                <span className="inline-block px-3 py-1 bg-amber-500/20 text-amber-300 text-xs rounded-full">
                  Ver landing →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Login Form */}
      <section id="login" className="max-w-md mx-auto px-4 py-20">
        <div className="bg-gradient-to-br from-slate-700/80 to-slate-800/80 border border-slate-600 rounded-2xl p-8 backdrop-blur">
          <h2 className="text-3xl font-bold text-white mb-2">Acceso Usuarios</h2>
          <p className="text-sm text-slate-400 mb-6">Demo credentials por niche</p>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Niche Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Selecciona tu niche:
              </label>
              <select
                value={loginSlug}
                onChange={(e) => setLoginSlug(e.target.value)}
                className="w-full px-4 py-2 bg-slate-600 border border-slate-500 rounded-lg text-white text-sm focus:outline-none focus:border-amber-500"
              >
                {niches.map((n) => (
                  <option key={n.slug} value={n.slug}>
                    {n.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-slate-400 mt-2 p-2 bg-slate-700/50 rounded">
                Email: {loginSlug}@demo.sonoradigitalcorp.com
              </p>
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Email:
              </label>
              <input
                type="email"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                placeholder={`${loginSlug}@demo.sonoradigitalcorp.com`}
                className="w-full px-4 py-2 bg-slate-600 border border-slate-500 rounded-lg text-white placeholder-slate-400 text-sm focus:outline-none focus:border-amber-500"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Contraseña:
              </label>
              <input
                type="password"
                value={loginPass}
                onChange={(e) => setLoginPass(e.target.value)}
                placeholder="Demo2026!Niche"
                className="w-full px-4 py-2 bg-slate-600 border border-slate-500 rounded-lg text-white placeholder-slate-400 text-sm focus:outline-none focus:border-amber-500"
                required
              />
              <p className="text-xs text-slate-400 mt-2 p-2 bg-slate-700/50 rounded">
                Patrón: Demo2026!{loginSlug.charAt(0).toUpperCase() + loginSlug.slice(1)}
              </p>
            </div>

            {/* Messages */}
            {error && (
              <div className="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-300 text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="p-3 bg-green-500/20 border border-green-500/50 rounded text-green-300 text-sm">
                {success}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white font-bold rounded-lg hover:shadow-lg transition disabled:opacity-50"
            >
              {loading ? '⏳ Conectando...' : '🚀 Acceder'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-600">
            <p className="text-xs text-slate-400 mb-3">
              📖 <strong>Credenciales demo:</strong>
            </p>
            <ul className="text-xs text-slate-400 space-y-1">
              {niches.map((n) => (
                <li key={n.slug}>
                  {n.slug}@demo: <code className="text-amber-300">Demo2026!{n.slug.charAt(0).toUpperCase() + n.slug.slice(1)}</code>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-slate-800/50 py-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-white">
            Qué incluye HERMES
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '💬', title: 'Chat IA', desc: 'HERMES responde 24/7 via WhatsApp/Telegram' },
              { icon: '📄', title: 'Facturas CFDI', desc: 'Emisión automática en segundos' },
              { icon: '🧠', title: 'RAG Inteligente', desc: 'Retrieval 150+ documentos normativos' },
              { icon: '📊', title: 'Reportes', desc: 'Análisis automáticos por niche' },
              { icon: '🔐', title: 'Multi-tenant', desc: 'RLS PostgreSQL, JWT revocable' },
              { icon: '⚡', title: 'API RESTful', desc: 'Integración con tus sistemas' },
            ].map((f, i) => (
              <div key={i} className="bg-slate-700/40 border border-slate-600 rounded-lg p-6 hover:border-amber-500/50 transition">
                <div className="text-3xl mb-3">{f.icon}</div>
                <h3 className="font-bold text-white mb-2">{f.title}</h3>
                <p className="text-sm text-slate-300">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 py-8 bg-slate-900">
        <div className="max-w-6xl mx-auto px-4 text-center text-slate-400 text-sm">
          <p>© 2026 Sonora Digital Corp — HERMES OS</p>
          <p className="mt-2">Para PYMEs mexicanas. Bot-first. Sin intervención manual.</p>
        </div>
      </footer>
    </div>
  )
}
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
      setTimeout(() => { window.location.href = '/dashboard' }, 1200)
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

      {/* ── SOLUCIONES ESPECIALIZADAS ────────────────────────────────────── */}
      <section className="relative z-10 py-20 px-4 max-w-5xl mx-auto border-t border-white/5">
        <div className="text-center mb-12">
          <p className="text-xs font-bold uppercase tracking-widest text-white/40 mb-3">Para tu industria</p>
          <h2 className="text-3xl sm:text-4xl font-black">HERMES especializado</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-6">
          <Link href="/contadores" className="group bg-gradient-to-br from-blue-900/20 to-blue-800/10 border border-blue-400/20 hover:border-blue-400/50 rounded-2xl p-8 transition">
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center mb-4 group-hover:bg-blue-500/30 transition">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="font-black text-lg mb-2 text-blue-300 group-hover:text-blue-200 transition">Para Contadores</h3>
            <p className="text-white/60 text-sm leading-relaxed group-hover:text-white/80 transition">
              Normatividad MX, alertas fiscales, reportes DIOT/RESICO automáticos. Reduce 30% tiempo administrativo.
            </p>
            <div className="mt-4 text-blue-400 font-semibold text-sm flex items-center gap-2 group-hover:translate-x-1 transition">
              Ver solución <ArrowRight className="w-4 h-4" />
            </div>
          </Link>
          <Link href="/artistas" className="group bg-gradient-to-br from-purple-900/20 to-purple-800/10 border border-purple-400/20 hover:border-purple-400/50 rounded-2xl p-8 transition">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mb-4 group-hover:bg-purple-500/30 transition">
              <Sparkles className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="font-black text-lg mb-2 text-purple-300 group-hover:text-purple-200 transition">Para Creadores</h3>
            <p className="text-white/60 text-sm leading-relaxed group-hover:text-white/80 transition">
              Distribución en 50+ plataformas, regalías en tiempo real, promoción automática. De demo a Spotify en 48h.
            </p>
            <div className="mt-4 text-purple-400 font-semibold text-sm flex items-center gap-2 group-hover:translate-x-1 transition">
              Ver solución <ArrowRight className="w-4 h-4" />
            </div>
          </Link>
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
