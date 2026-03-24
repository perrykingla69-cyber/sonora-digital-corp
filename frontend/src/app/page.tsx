'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { Countdown } from './countdown'
import {
  ArrowRight, Sparkles, CheckCircle2, Zap, Brain, FileText, Globe,
  Smartphone, GraduationCap, Package, Users, Star, ShieldCheck,
  Mic, Bell, Share2, Gift, Play, ChevronRight, Flame, Crown,
  BookOpen, Code2, Coins, Layers, TrendingUp, MessageSquare,
  Rocket, Volume2, VolumeX,
} from 'lucide-react'

// ─── Particle canvas ─────────────────────────────────────────────────────────
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
    const pts = Array.from({ length: 80 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - .5) * .4,
      vy: (Math.random() - .5) * .4,
      r: Math.random() * 1.5 + .5,
      a: Math.random(),
    }))
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(212,175,55,${p.a * .6})`
        ctx.fill()
      })
      // Lines between close particles
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y
          const d = Math.sqrt(dx * dx + dy * dy)
          if (d < 100) {
            ctx.beginPath()
            ctx.moveTo(pts[i].x, pts[i].y)
            ctx.lineTo(pts[j].x, pts[j].y)
            ctx.strokeStyle = `rgba(212,175,55,${(1 - d / 100) * .12})`
            ctx.lineWidth = .5
            ctx.stroke()
          }
        }
      }
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [])
  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
}

// ─── 3D tilt card ─────────────────────────────────────────────────────────────
function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const onMove = (e: React.MouseEvent) => {
    const el = ref.current!
    const { left, top, width, height } = el.getBoundingClientRect()
    const x = (e.clientX - left) / width - .5
    const y = (e.clientY - top) / height - .5
    el.style.transform = `perspective(800px) rotateY(${x * 12}deg) rotateX(${-y * 12}deg) scale3d(1.02,1.02,1.02)`
  }
  const onLeave = () => { if (ref.current) ref.current.style.transform = 'perspective(800px) rotateY(0) rotateX(0) scale3d(1,1,1)' }
  return (
    <div ref={ref} onMouseMove={onMove} onMouseLeave={onLeave} className={`transition-transform duration-200 ${className}`}>
      {children}
    </div>
  )
}

// ─── Flash offer banner ───────────────────────────────────────────────────────
function FlashBanner() {
  const [visible, setVisible] = useState(true)
  if (!visible) return null
  return (
    <div className="relative bg-gradient-to-r from-[#D4AF37] via-[#f0c842] to-[#D4AF37] text-black text-xs font-bold py-2 text-center overflow-hidden">
      <span className="animate-pulse mr-2">🔥</span>
      OFERTA FLASH — Acceso Freemium GRATIS antes del 1 de Abril · 3 meses de Pro a $499 MXN ·
      <span className="animate-pulse mx-2">⚡</span>
      <button onClick={() => setVisible(false)} className="absolute right-3 top-1/2 -translate-y-1/2 text-black/50 hover:text-black">✕</button>
    </div>
  )
}

// ─── Data ─────────────────────────────────────────────────────────────────────
const PLANS = [
  {
    id: 'libre',
    name: 'Mystic Libre',
    badge: '🌱 FREEMIUM',
    badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    price: '$0',
    period: '/mes para siempre',
    highlight: false,
    color: 'border-emerald-500/20',
    cta: 'Empezar gratis ahora',
    ctaClass: 'border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/10',
    description: 'Tu primer paso hacia la soberanía digital.',
    features: [
      '30 facturas CFDI 4.0 / mes',
      '1 usuario',
      'Brain IA básico (10 consultas/día)',
      '5 posts de contenido / mes',
      '2 cursos de Academia',
      'Dashboard fiscal básico',
      'Soporte comunidad',
    ],
  },
  {
    id: 'pro',
    name: 'Mystic Pro',
    badge: '⚡ MÁS POPULAR',
    badgeClass: 'bg-[#D4AF37]/20 text-[#D4AF37] border-[#D4AF37]/30',
    price: '$999',
    period: '/mes',
    highlight: true,
    color: 'border-[#D4AF37]/40',
    cta: 'Activar Mystic Pro',
    ctaClass: 'bg-[#D4AF37] text-black hover:bg-[#f0c842]',
    description: 'Para el profesional que quiere escalar su imperio.',
    features: [
      'Facturas ilimitadas',
      '5 usuarios',
      'Brain IA completo + voz bidireccional',
      'Contenido ilimitado (Instagram, TikTok, LinkedIn, X)',
      'Academia completa con certificación',
      'Alertas configurables + notificaciones push',
      'CRM + seguimiento de leads',
      'Soporte prioritario 24/7',
      'Ofertas flash exclusivas',
    ],
  },
  {
    id: 'empire',
    name: 'Mystic Empire',
    badge: '👑 TOTAL SOBERANÍA',
    badgeClass: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
    price: '$2,999',
    period: '/mes',
    highlight: false,
    color: 'border-violet-500/20',
    cta: 'Construir mi Imperio',
    ctaClass: 'border border-violet-500/40 text-violet-300 hover:bg-violet-500/10',
    description: 'El ecosistema completo. Sin límites. Sin excusas.',
    features: [
      'Todo ilimitado + servidor dedicado',
      'Agente IA personal (OpenClaw)',
      'Academia white-label para tus clientes',
      'Kit merch: USB 32GB + pluma + cuaderno Mystic',
      'Publicidad cruzada en red Mystic',
      'A.C. donataria — deducción fiscal garantizada',
      'Estrategia de reinversión personalizada',
      'Sistema de afiliados con comisión 20%',
      'SLA 99.9% + onboarding personal',
      'Acceso a red de proveedores Mystic',
    ],
  },
]

const FEATURES = [
  {
    icon: FileText,
    color: 'text-[#D4AF37]',
    bg: 'bg-[#D4AF37]/10 border-[#D4AF37]/20',
    title: 'Contabilidad IA',
    desc: '147 cálculos SAT automatizados. CFDI 4.0, IVA, ISR, IMSS, RESICO. Más rápido que cualquier contador humano.',
  },
  {
    icon: Smartphone,
    color: 'text-cyan-400',
    bg: 'bg-cyan-400/10 border-cyan-400/20',
    title: 'Contenido a 1 Click',
    desc: 'Tu marca en Instagram, TikTok, LinkedIn y X automáticamente. La IA crea, programa y publica por ti.',
  },
  {
    icon: Mic,
    color: 'text-violet-400',
    bg: 'bg-violet-400/10 border-violet-400/20',
    title: 'Voz Bidireccional',
    desc: 'Te saluda al entrar, reporta tu estado fiscal, alerta vencimientos y recomienda acciones — por voz, en tiempo real.',
  },
  {
    icon: Bell,
    color: 'text-rose-400',
    bg: 'bg-rose-400/10 border-rose-400/20',
    title: 'Alertas Inteligentes',
    desc: 'Configura alertas SAT, vencimientos IMSS, flujo de caja, declaraciones. Recibe en Telegram, email o voz.',
  },
  {
    icon: GraduationCap,
    color: 'text-emerald-400',
    bg: 'bg-emerald-400/10 border-emerald-400/20',
    title: 'Academia Blockchain',
    desc: 'Certifícate en IA, Blockchain, NFT, Smart Contracts. De 0 a 100. Currículum reconocido + valor económico real.',
  },
  {
    icon: Share2,
    color: 'text-sky-400',
    bg: 'bg-sky-400/10 border-sky-400/20',
    title: 'Red de Afiliados',
    desc: 'Gana 20% por cada cliente que traigas. Publicidad cruzada con toda la red. Tu crecimiento = nuestro crecimiento.',
  },
]

const ACADEMY_TRACKS = [
  { icon: Brain, title: 'Inteligencia Artificial', desc: 'Prompts, agentes, modelos locales, MCP servers', color: 'text-cyan-400', bg: 'from-cyan-900/20 to-transparent' },
  { icon: Coins, title: 'Blockchain & Cripto', desc: 'Bitcoin, Ethereum, wallets, exchanges, DeFi', color: 'text-[#D4AF37]', bg: 'from-amber-900/20 to-transparent' },
  { icon: Code2, title: 'Smart Contracts', desc: 'Solidity, Hardhat, deploy en mainnet, auditoría', color: 'text-violet-400', bg: 'from-violet-900/20 to-transparent' },
  { icon: Layers, title: 'NFTs & Tokenización', desc: 'Crear, vender, royalties, colecciones, marketplaces', color: 'text-emerald-400', bg: 'from-emerald-900/20 to-transparent' },
  { icon: Globe, title: 'Web3 & Metaverso', desc: 'dApps, IPFS, wallets conectadas, gobernanza DAO', color: 'text-sky-400', bg: 'from-sky-900/20 to-transparent' },
  { icon: TrendingUp, title: 'Finanzas Digitales', desc: 'Trading, DeFi yields, staking, gestión de portfolio', color: 'text-rose-400', bg: 'from-rose-900/20 to-transparent' },
]

const MERCH = [
  { name: 'USB Mystic 32GB', desc: 'Tu agente digital en el bolsillo. Precargada con herramientas Mystic.', emoji: '💾', price: '$299 MXN' },
  { name: 'Kit Ejecutivo', desc: 'Pluma + cuaderno + stickers exclusivos. Para cerrar negocios con estilo.', emoji: '🖊️', price: '$199 MXN' },
  { name: 'Hoodie Mystic', desc: 'Representa la revolución digital sonorense. Colección limitada.', emoji: '👕', price: '$599 MXN' },
  { name: 'Pack Fundador', desc: 'USB + kit + hoodie + acceso especial. Solo para los primeros 100.', emoji: '👑', price: '$999 MXN' },
]

const COMPETITORS = [
  { name: 'Factura.com', items: ['Solo facturas', 'Sin IA real', 'Sin contenido', 'Sin academia'] },
  { name: 'CONTPAQi', items: ['Sistema de escritorio', 'Sin cloud nativo', 'Sin automatización', 'Sin comunidad'] },
  { name: 'Dropbox', items: ['Solo almacenamiento', 'Sin fiscal', 'Sin IA', 'Sin valor educativo'] },
]

const SOCIALS = [
  { name: 'Instagram', handle: '@sonoradigitalcorp', emoji: '📸', color: 'from-purple-600 to-pink-600' },
  { name: 'TikTok', handle: '@sonoradigitalcorp', emoji: '🎵', color: 'from-black to-gray-800' },
  { name: 'LinkedIn', handle: 'Sonora Digital Corp', emoji: '💼', color: 'from-blue-700 to-blue-900' },
  { name: 'YouTube', handle: '@MysticAIOS', emoji: '▶️', color: 'from-red-700 to-red-900' },
  { name: 'Telegram', handle: 't.me/mysticaios', emoji: '✈️', color: 'from-sky-600 to-sky-800' },
  { name: 'WhatsApp', handle: 'Canal oficial', emoji: '💬', color: 'from-green-700 to-green-900' },
]

// ─── Component ────────────────────────────────────────────────────────────────
export default function HomePage() {
  const [muted, setMuted] = useState(true)
  const [activeSection, setActiveSection] = useState('')

  return (
    <main className="min-h-screen bg-[#030306] text-white overflow-x-hidden">
      {/* Flash Banner */}
      <FlashBanner />

      {/* NAV */}
      <header className="sticky top-0 z-50 border-b border-[#D4AF37]/10 bg-[#030306]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-xl bg-[#D4AF37]/20 blur-lg" />
              <div className="relative w-9 h-9 rounded-xl bg-gradient-to-br from-[#D4AF37] to-[#8B7520] flex items-center justify-center text-black font-black text-sm">M</div>
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.3em] text-[#D4AF37]/70">Sonora Digital Corp</p>
              <p className="text-sm font-bold text-white leading-none">MYSTIC AI OS</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-white/60">
            <a href="#features" className="hover:text-[#D4AF37] transition-colors">Plataforma</a>
            <a href="#pricing" className="hover:text-[#D4AF37] transition-colors">Precios</a>
            <a href="#academia" className="hover:text-[#D4AF37] transition-colors">Academia</a>
            <a href="#merch" className="hover:text-[#D4AF37] transition-colors">Merch</a>
            <a href="#afiliados" className="hover:text-[#D4AF37] transition-colors">Afiliados</a>
          </nav>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMuted(m => !m)}
              className="p-2 rounded-lg text-white/40 hover:text-[#D4AF37] transition-colors"
              title={muted ? 'Activar sonido' : 'Silenciar'}
            >
              {muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
            <Link href="/login" className="px-4 py-2 text-sm text-white/70 hover:text-white transition-colors">
              Entrar
            </Link>
            <Link
              href="/login"
              className="px-4 py-2 bg-[#D4AF37] text-black text-sm font-bold rounded-xl hover:bg-[#f0c842] transition-colors"
            >
              Registrarme gratis
            </Link>
          </div>
        </div>
      </header>

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <ParticleField />

        {/* Radial glows */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[900px] h-[900px] bg-[#D4AF37]/4 rounded-full blur-[120px]" />
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-violet-500/5 rounded-full blur-[100px]" />
          <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto px-6 py-32 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-[#D4AF37]/30 bg-[#D4AF37]/8 px-5 py-2 text-sm text-[#D4AF37] mb-8">
            <Sparkles className="w-4 h-4" />
            El sistema más avanzado para PYMEs mexicanas · Lanzamiento 1 Abril 2026
            <span className="bg-[#D4AF37] text-black text-[10px] font-bold px-2 py-0.5 rounded-full ml-1">NUEVO</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-8xl font-black leading-none tracking-tight mb-6">
            <span className="block text-white">No uses software.</span>
            <span className="block bg-gradient-to-r from-[#D4AF37] via-[#f0c842] to-[#D4AF37] bg-clip-text text-transparent">
              Construye tu
            </span>
            <span className="block text-white">Imperio Digital.</span>
          </h1>

          <p className="mx-auto max-w-3xl text-lg sm:text-xl text-white/60 leading-relaxed mb-4">
            Mystic automatiza tu contabilidad, crea contenido para tus redes, te enseña blockchain desde cero y convierte tu PYME en una máquina de ingresos autónoma.
          </p>
          <p className="text-sm text-[#D4AF37]/70 mb-12 font-medium">
            Mejor que Factura.com. Mejor que CONTPAQi. Sin comparación.
          </p>

          {/* Countdown */}
          <div className="flex flex-col items-center gap-3 mb-10">
            <p className="text-xs uppercase tracking-widest text-white/40">Tiempo para el lanzamiento oficial</p>
            <Countdown />
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#D4AF37] to-[#f0c842] text-black font-black text-base rounded-2xl hover:shadow-[0_0_40px_rgba(212,175,55,0.4)] transition-all"
            >
              <Zap className="w-5 h-5" />
              Acceso freemium — GRATIS
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/15 text-white font-medium text-base rounded-2xl hover:bg-white/5 transition-all"
            >
              <Play className="w-4 h-4 text-[#D4AF37]" />
              Ver demo completo
            </a>
          </div>

          <p className="mt-5 text-xs text-white/30">
            Sin tarjeta de crédito · Sin instalación · Cancela cuando quieras
          </p>

          {/* 3D floating cards */}
          <div className="mt-20 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {[
              { n: '147', l: 'Cálculos SAT', c: 'text-[#D4AF37]' },
              { n: '4', l: 'Redes sociales auto', c: 'text-cyan-400' },
              { n: '∞', l: 'Consultas IA', c: 'text-violet-400' },
              { n: '24/7', l: 'Soporte por voz', c: 'text-emerald-400' },
            ].map(({ n, l, c }) => (
              <TiltCard key={l}>
                <div className="rounded-2xl border border-white/8 bg-white/3 backdrop-blur p-5 text-center">
                  <p className={`text-3xl font-black ${c}`}>{n}</p>
                  <p className="text-xs text-white/50 mt-1">{l}</p>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── CONTENT FACTORY DEMO ─────────────────────────────────────────── */}
      <section id="features" className="py-24 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-[#030306] via-[#060610] to-[#030306]" />
        <div className="relative max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-medium uppercase tracking-widest text-cyan-400 mb-3">Content Factory</p>
            <h2 className="text-4xl sm:text-5xl font-black text-white">
              Crea contenido para tus clientes.<br />
              <span className="text-cyan-400">Un click. Cuatro plataformas.</span>
            </h2>
            <p className="mt-4 text-white/50 max-w-2xl mx-auto">
              La IA genera posts optimizados para Instagram, TikTok, LinkedIn y X — en el tono de tu marca, con hashtags, emojis y horario óptimo. Automáticamente, cada 6 horas.
            </p>
          </div>

          {/* Fake content demo UI */}
          <div className="max-w-4xl mx-auto">
            <TiltCard>
              <div className="rounded-3xl border border-cyan-500/20 bg-[#0a0a14] p-6 overflow-hidden">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="ml-2 text-xs text-white/30 font-mono">mystic-content-factory.tsx</span>
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  {[
                    { platform: 'Instagram', emoji: '📸', color: 'from-purple-600/20 to-pink-600/20 border-purple-500/30', content: '🔮 ¿Sabías que con Mystic AI puedes generar tus declaraciones fiscales en 3 minutos? Mientras tú disfrutas tu café ☕, nosotros calculamos tus impuestos. #FiscalIA #PYMEsMéxico' },
                    { platform: 'TikTok', emoji: '🎵', color: 'from-gray-700/20 to-black/20 border-gray-600/30', content: '¡El truco que los contadores no quieren que sepas! 🤫 Con IA puedes automatizar el 90% de tu contabilidad. Parte 1/3 👇 #ContabilidadIA #Emprendedor' },
                    { platform: 'LinkedIn', emoji: '💼', color: 'from-blue-700/20 to-blue-900/20 border-blue-600/30', content: 'Las PYMEs mexicanas pierden en promedio 40 horas/mes en procesos contables manuales. Mystic AI los automatiza en 4 minutos. El ROI es de 2,200% en el primer mes.' },
                    { platform: 'X / Twitter', emoji: '✖️', color: 'from-gray-600/20 to-gray-800/20 border-gray-500/30', content: 'Thread: Cómo automaticé mi contabilidad en 15 minutos con IA y ahorro $15,000 MXN/mes → (1/7)' },
                  ].map(({ platform, emoji, color, content }) => (
                    <div key={platform} className={`rounded-2xl border bg-gradient-to-br ${color} p-4`}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-lg">{emoji}</span>
                        <span className="text-xs font-bold text-white/80">{platform}</span>
                        <span className="ml-auto text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full">Auto ✓</span>
                      </div>
                      <p className="text-xs text-white/60 leading-relaxed">{content}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-6 flex items-center justify-between">
                  <p className="text-xs text-white/30">Generado automáticamente · Siguiente ciclo en 5h 42m</p>
                  <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-semibold rounded-xl hover:bg-cyan-500/30 transition-colors">
                    <Zap className="w-3.5 h-3.5" /> Generar ahora
                  </button>
                </div>
              </div>
            </TiltCard>
          </div>
        </div>
      </section>

      {/* ── FEATURES GRID ────────────────────────────────────────────────── */}
      <section className="py-16 max-w-7xl mx-auto px-6">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: Icon, color, bg, title, desc }) => (
            <TiltCard key={title}>
              <div className={`h-full rounded-3xl border ${bg} p-7 bg-[#0A0A0F]`}>
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-2xl border ${bg} mb-5`}>
                  <Icon className={`w-6 h-6 ${color}`} />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{desc}</p>
              </div>
            </TiltCard>
          ))}
        </div>
      </section>

      {/* ── VS COMPETIDORES ───────────────────────────────────────────────── */}
      <section className="py-20 bg-[#060610]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <p className="text-sm font-medium uppercase tracking-widest text-rose-400 mb-3">Comparativa honesta</p>
            <h2 className="text-3xl sm:text-4xl font-black text-white">
              Ellos se quedan lejos.
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left text-sm text-white/40 py-4 pr-6">Característica</th>
                  {['Factura.com', 'CONTPAQi', 'Dropbox', 'Mystic'].map(n => (
                    <th key={n} className={`text-center py-4 px-4 text-sm font-bold ${n === 'Mystic' ? 'text-[#D4AF37]' : 'text-white/40'}`}>
                      {n === 'Mystic' && <Crown className="w-4 h-4 inline mr-1 text-[#D4AF37]" />}{n}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  ['Contabilidad IA', '✓ básico', '✓ legacy', '✗', '✓✓✓ 147 cálculos'],
                  ['Creación de contenido', '✗', '✗', '✗', '✓ 4 plataformas auto'],
                  ['Academia certificada', '✗', '✗', '✗', '✓ Blockchain · IA · NFT'],
                  ['Voz bidireccional', '✗', '✗', '✗', '✓ 24/7'],
                  ['Sistema de afiliados', '✗', '✗', '✗', '✓ 20% comisión'],
                  ['Tienda merch', '✗', '✗', '✗', '✓ USB · Kit · Ropa'],
                  ['IA local soberana', '✗', '✗', '✗', '✓ Sin intermediarios'],
                  ['A.C. deducción fiscal', '✗', '✗', '✗', '✓ En proceso'],
                ].map(([feat, ...vals]) => (
                  <tr key={feat} className="border-t border-white/5">
                    <td className="py-3 pr-6 text-sm text-white/60">{feat}</td>
                    {vals.map((v, i) => (
                      <td key={i} className={`py-3 px-4 text-center text-sm ${i === 3 ? 'text-[#D4AF37] font-semibold' : 'text-white/30'}`}>
                        {v.startsWith('✗') ? <span className="text-red-500/50">✗</span> : v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── PRICING ───────────────────────────────────────────────────────── */}
      <section id="pricing" className="py-24 max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-sm font-medium uppercase tracking-widest text-[#D4AF37] mb-3">Precios</p>
          <h2 className="text-4xl sm:text-5xl font-black text-white">
            Sin letra chica.<br />Sin sorpresas.
          </h2>
          <p className="mt-4 text-white/50 max-w-xl mx-auto">
            Empieza gratis antes del 1 de Abril y mantén el plan Libre por siempre. Actualiza cuando estés listo para escalar.
          </p>
          <div className="inline-flex items-center gap-2 mt-4 bg-rose-500/10 border border-rose-500/20 rounded-full px-4 py-2 text-sm text-rose-300">
            <Flame className="w-4 h-4" /> Oferta flash: 3 meses de Pro a $499 hasta el 31 de marzo
          </div>
        </div>

        <div className="grid sm:grid-cols-3 gap-6">
          {PLANS.map(plan => (
            <TiltCard key={plan.id}>
              <div className={`relative flex flex-col h-full rounded-3xl border ${plan.color} p-7 ${plan.highlight ? 'bg-[#D4AF37]/5' : 'bg-[#0A0A0F]'}`}>
                {plan.highlight && (
                  <div className="absolute -top-px left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent" />
                )}
                <div className={`self-start text-[11px] font-bold px-3 py-1 rounded-full border ${plan.badgeClass} mb-5`}>
                  {plan.badge}
                </div>
                <p className="text-xl font-bold text-white mb-1">{plan.name}</p>
                <p className="text-xs text-white/40 mb-5">{plan.description}</p>
                <div className="flex items-end gap-1 mb-6">
                  <span className="text-5xl font-black text-white">{plan.price}</span>
                  <span className="text-white/40 mb-2 text-sm">{plan.period}</span>
                </div>
                <ul className="space-y-3 flex-1 mb-8">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-start gap-2.5 text-sm text-white/70">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className={`block text-center py-3.5 rounded-2xl text-sm font-bold transition-all ${plan.ctaClass}`}
                >
                  {plan.cta}
                </Link>
              </div>
            </TiltCard>
          ))}
        </div>
        <p className="text-center mt-6 text-xs text-white/30">
          Paga con SPEI · USDC · BTC · Tarjeta MX · Pago en efectivo (OXXO)
        </p>
      </section>

      {/* ── ACADEMIA ─────────────────────────────────────────────────────── */}
      <section id="academia" className="py-24 bg-gradient-to-b from-[#060610] to-[#030306]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-medium uppercase tracking-widest text-violet-400 mb-3">Escuela Mystic</p>
            <h2 className="text-4xl sm:text-5xl font-black text-white">
              De 0 a 100 en las tecnologías<br />
              <span className="text-violet-400">que mueven el dinero.</span>
            </h2>
            <p className="mt-4 text-white/50 max-w-2xl mx-auto">
              Cada plan incluye acceso a la Academia. Certifícate en las tecnologías del futuro y véndelas como servicio a tus propios clientes. La educación es el producto más rentable que existe.
            </p>
            <div className="mt-4 inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-2 text-sm text-violet-300">
              <GraduationCap className="w-4 h-4" /> Valor curricular reconocido · Sell what you learn
            </div>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {ACADEMY_TRACKS.map(({ icon: Icon, title, desc, color, bg }) => (
              <TiltCard key={title}>
                <div className={`relative overflow-hidden rounded-3xl border border-white/8 bg-gradient-to-br ${bg} bg-[#0A0A14] p-7`}>
                  <div className="flex items-start gap-4">
                    <Icon className={`w-8 h-8 ${color} shrink-0 mt-1`} />
                    <div>
                      <h3 className="text-base font-bold text-white mb-1">{title}</h3>
                      <p className="text-sm text-white/50">{desc}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <div className="flex -space-x-2">
                      {[...Array(4)].map((_, i) => (
                        <div key={i} className="w-6 h-6 rounded-full bg-gradient-to-br from-[#D4AF37]/40 to-[#D4AF37]/10 border border-[#D4AF37]/20" />
                      ))}
                    </div>
                    <span className="text-[11px] text-white/30">+{Math.floor(Math.random() * 200 + 50)} alumnos</span>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-4 bg-violet-600 hover:bg-violet-500 text-white font-bold text-base rounded-2xl transition-all"
            >
              <BookOpen className="w-5 h-5" /> Acceder a la Academia
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── MERCH ─────────────────────────────────────────────────────────── */}
      <section id="merch" className="py-24 max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-sm font-medium uppercase tracking-widest text-[#D4AF37] mb-3">Tienda Mystic</p>
          <h2 className="text-4xl font-black text-white">
            Porta la revolución.<br />
            <span className="text-[#D4AF37]">Sé el proveedor de todo.</span>
          </h2>
          <p className="mt-4 text-white/50">
            Mystic no es solo software. Es una marca. Una identidad. Un movimiento.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {MERCH.map(({ name, desc, emoji, price }) => (
            <TiltCard key={name}>
              <div className="rounded-3xl border border-[#D4AF37]/15 bg-[#0A0A0F] p-6 text-center flex flex-col gap-4">
                <div className="text-5xl">{emoji}</div>
                <div>
                  <h3 className="font-bold text-white mb-1">{name}</h3>
                  <p className="text-xs text-white/50">{desc}</p>
                </div>
                <div className="text-[#D4AF37] font-black text-xl">{price}</div>
                <button className="py-2.5 border border-[#D4AF37]/30 text-[#D4AF37] text-sm font-semibold rounded-xl hover:bg-[#D4AF37]/10 transition-colors">
                  Pre-ordenar
                </button>
              </div>
            </TiltCard>
          ))}
        </div>
        <p className="text-center mt-8 text-sm text-white/30">
          🎯 Próximamente: publicidad cruzada en todas las plataformas · Conviértete en distribuidor
        </p>
      </section>

      {/* ── AFILIADOS ─────────────────────────────────────────────────────── */}
      <section id="afiliados" className="py-24 bg-[#060610]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="rounded-3xl border border-emerald-500/20 bg-gradient-to-br from-emerald-900/10 to-transparent p-10 text-center">
            <Gift className="w-12 h-12 text-emerald-400 mx-auto mb-6" />
            <p className="text-sm font-medium uppercase tracking-widest text-emerald-400 mb-3">Programa de Afiliados</p>
            <h2 className="text-4xl font-black text-white mb-4">
              Gana mientras duermes.<br />
              <span className="text-emerald-400">20% por cada referido.</span>
            </h2>
            <p className="text-white/50 max-w-2xl mx-auto mb-8 leading-relaxed">
              Comparte tu link único. Cuando alguien se suscribe, ganas el 20% de su plan mensual — para siempre mientras sea cliente. Trae 10 clientes Pro y ya pagaste tu propio plan y más.
            </p>
            <div className="grid sm:grid-cols-3 gap-5 mb-10">
              {[
                { n: '20%', l: 'Comisión mensual recurrente', c: 'text-emerald-400' },
                { n: '$200', l: 'Bono por primer referido', c: 'text-[#D4AF37]' },
                { n: '∞', l: 'Sin límite de referidos', c: 'text-violet-400' },
              ].map(({ n, l, c }) => (
                <div key={l} className="rounded-2xl border border-white/8 bg-white/3 p-5">
                  <p className={`text-3xl font-black ${c}`}>{n}</p>
                  <p className="text-xs text-white/50 mt-1">{l}</p>
                </div>
              ))}
            </div>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-7 py-3.5 bg-emerald-500 hover:bg-emerald-400 text-white font-bold rounded-2xl transition-all"
              >
                <Users className="w-4 h-4" /> Unirme al programa
              </Link>
              <button className="inline-flex items-center gap-2 px-7 py-3.5 border border-white/15 text-white font-medium rounded-2xl hover:bg-white/5 transition-all">
                <Share2 className="w-4 h-4 text-[#D4AF37]" /> Ver beneficios completos
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── REDES SOCIALES ───────────────────────────────────────────────── */}
      <section className="py-20 max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <p className="text-sm font-medium uppercase tracking-widest text-sky-400 mb-3">Síguenos</p>
          <h2 className="text-3xl font-black text-white">El movimiento crece en todas partes.</h2>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {SOCIALS.map(({ name, handle, emoji, color }) => (
            <div key={name} className={`rounded-2xl bg-gradient-to-br ${color} p-5 text-center border border-white/10 hover:scale-105 transition-transform cursor-pointer`}>
              <div className="text-3xl mb-2">{emoji}</div>
              <p className="text-sm font-bold text-white">{name}</p>
              <p className="text-[11px] text-white/60 mt-1">{handle}</p>
            </div>
          ))}
        </div>
        <p className="text-center mt-6 text-xs text-white/30">
          Cuentas activadas para sonoradigitalcorp@gmail.com · En proceso de verificación
        </p>
      </section>

      {/* ── ROI BANNER ───────────────────────────────────────────────────── */}
      <section className="py-12 bg-[#060610]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="rounded-3xl border border-[#D4AF37]/20 bg-[#D4AF37]/3 p-10 text-center">
            <TrendingUp className="w-10 h-10 text-[#D4AF37] mx-auto mb-4" />
            <p className="text-sm uppercase tracking-widest text-[#D4AF37]/70 mb-3">ROI Calculado</p>
            <h3 className="text-2xl sm:text-3xl font-black text-white">
              5 hrs/día × 22 días × $200 MXN/hr
            </h3>
            <p className="text-4xl sm:text-5xl font-black text-[#D4AF37] my-3">= $110,000 MXN ahorrados/mes</p>
            <p className="text-white/40 text-sm">Inversión en Mystic Pro: $999 MXN/mes · ROI del 10,910%</p>
          </div>
        </div>
      </section>

      {/* ── CTA FINAL ─────────────────────────────────────────────────────── */}
      <section className="relative py-32 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-t from-[#D4AF37]/8 to-transparent" />
        </div>
        <div className="relative max-w-4xl mx-auto px-6 text-center">
          <Rocket className="w-12 h-12 text-[#D4AF37] mx-auto mb-6" />
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-6">
            El 1 de Abril<br />
            <span className="bg-gradient-to-r from-[#D4AF37] via-[#f0c842] to-[#D4AF37] bg-clip-text text-transparent">
              comienza la revolución.
            </span>
          </h2>
          <p className="text-lg text-white/50 leading-relaxed max-w-2xl mx-auto mb-10">
            Tú decides: seguir usando sistemas del siglo pasado, o construir tu imperio digital desde Sonora, México. Registra tu lugar freemium hoy — sin costo, sin riesgo, sin excusas.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-[#D4AF37] to-[#f0c842] text-black font-black text-lg rounded-2xl hover:shadow-[0_0_60px_rgba(212,175,55,0.5)] transition-all"
            >
              <Sparkles className="w-5 h-5" />
              Empezar GRATIS ahora
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
          <div className="flex items-center justify-center gap-8 mt-10 text-xs text-white/30">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> LFPDPPP · Datos en México</span>
            <span className="flex items-center gap-1.5"><Star className="w-3.5 h-3.5 text-[#D4AF37]" /> Sin tarjeta de crédito</span>
            <span className="flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-cyan-400" /> 100% open source core</span>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/8 bg-[#030306] py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid sm:grid-cols-4 gap-8 mb-10">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#D4AF37] to-[#8B7520] flex items-center justify-center text-black font-black text-xs">M</div>
                <span className="font-bold text-white">MYSTIC AI OS</span>
              </div>
              <p className="text-xs text-white/40 leading-relaxed">
                El ecosistema digital más avanzado para PYMEs mexicanas. Construido en Sonora, para el mundo.
              </p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-white/50 mb-4">Plataforma</p>
              <ul className="space-y-2 text-sm text-white/40">
                {['Contable IA', 'Content Factory', 'Brain IA', 'Academia', 'Merch'].map(l => (
                  <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-white/50 mb-4">Empresa</p>
              <ul className="space-y-2 text-sm text-white/40">
                {['Sobre nosotros', 'Blog', 'Afiliados', 'A.C. Impacto Social', 'Proveedores'].map(l => (
                  <li key={l}><a href="#" className="hover:text-white transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-white/50 mb-4">Contacto</p>
              <ul className="space-y-2 text-sm text-white/40">
                <li>sonoradigitalcorp@gmail.com</li>
                <li>Hermosillo, Sonora, México</li>
                <li className="pt-2">
                  <Link href="/login" className="text-[#D4AF37] hover:underline">Panel de control →</Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/30">
            <p>© 2026 Sonora Digital Corp · Mystic AI OS · Hermosillo, Sonora, México</p>
            <p>LFPDPPP · Aviso de privacidad · Términos · Datos almacenados en México</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
