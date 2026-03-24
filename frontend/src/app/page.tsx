'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import Link from 'next/link'
import { Countdown } from './countdown'
import {
  ArrowRight, Sparkles, CheckCircle2, Zap, Brain, FileText, Globe,
  Smartphone, GraduationCap, Package, Users, Star, ShieldCheck,
  Mic, Bell, Share2, Play, ChevronRight, Flame, Crown,
  BookOpen, Code2, Coins, Layers, TrendingUp, MessageSquare,
  Rocket, Lock, Wallet, ExternalLink, Award, Briefcase,
  ChevronDown, X, CheckSquare, BarChart3, Target,
  AlertTriangle, ShieldOff, TrendingDown, Hexagon, Quote,
  Trophy, BadgeCheck, Image as ImageIcon, Cpu,
} from 'lucide-react'

// ─── Logo SVG — Ojo Místico ────────────────────────────────────────────────
function MysticEyeLogo({ size = 40 }: { size?: number }) {
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
      {/* Outer triangle */}
      <polygon points="50,4 96,86 4,86" fill="none" stroke="url(#eyeGold)" strokeWidth="2.5" filter="url(#glow)" />
      {/* Inner inverted triangle (hexagram hidden geometry — 6 triangles) */}
      <polygon points="50,28 76,74 24,74" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      <polygon points="50,72 74,28 26,28" fill="none" stroke="#D4AF37" strokeWidth="0.8" opacity="0.4" />
      {/* Rays */}
      {[0,30,60,90,120,150,210,240,270,300,330].map((deg, i) => {
        const rad = (deg * Math.PI) / 180
        const x1 = 50 + Math.cos(rad) * 18
        const y1 = 54 + Math.sin(rad) * 14
        const x2 = 50 + Math.cos(rad) * 23
        const y2 = 54 + Math.sin(rad) * 18
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#D4AF37" strokeWidth="0.8" opacity="0.5" />
      })}
      {/* Eye outline */}
      <ellipse cx="50" cy="54" rx="16" ry="10" fill="none" stroke="url(#eyeGold)" strokeWidth="1.5" />
      {/* Iris */}
      <circle cx="50" cy="54" r="7" fill="url(#irisGrad)" />
      {/* Pupil */}
      <circle cx="50" cy="54" r="3" fill="#0a0500" />
      {/* Pupil highlight */}
      <circle cx="52" cy="52" r="1" fill="#D4AF37" opacity="0.8" />
      {/* Upper/lower eyelid lines */}
      <path d="M34,54 Q50,44 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
      <path d="M34,54 Q50,64 66,54" stroke="#D4AF37" strokeWidth="1" fill="none" />
      {/* Corner dots (subtle) */}
      <circle cx="50" cy="6" r="1.5" fill="#D4AF37" />
      <circle cx="94" cy="85" r="1.5" fill="#D4AF37" />
      <circle cx="6" cy="85" r="1.5" fill="#D4AF37" />
    </svg>
  )
}

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
    const pts = Array.from({ length: 60 }, () => ({
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
        ctx.fillStyle = `rgba(212,175,55,${p.a * .5})`; ctx.fill()
      })
      for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) {
        const dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y
        const d = Math.sqrt(dx * dx + dy * dy)
        if (d < 120) {
          ctx.beginPath(); ctx.moveTo(pts[i].x, pts[i].y); ctx.lineTo(pts[j].x, pts[j].y)
          ctx.strokeStyle = `rgba(212,175,55,${(1 - d / 120) * .1})`; ctx.lineWidth = .5; ctx.stroke()
        }
      }
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [])
  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />
}

// ─── Tilt Card ─────────────────────────────────────────────────────────────
function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const onMove = (e: React.MouseEvent) => {
    const el = ref.current!
    const { left, top, width, height } = el.getBoundingClientRect()
    const x = (e.clientX - left) / width - .5, y = (e.clientY - top) / height - .5
    el.style.transform = `perspective(800px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) scale3d(1.02,1.02,1.02)`
  }
  const onLeave = () => { if (ref.current) ref.current.style.transform = 'perspective(800px) rotateY(0) rotateX(0) scale3d(1,1,1)' }
  return <div ref={ref} onMouseMove={onMove} onMouseLeave={onLeave} className={`transition-transform duration-200 ${className}`}>{children}</div>
}

// ─── Flash Banner ─────────────────────────────────────────────────────────
function FlashBanner() {
  const [v, setV] = useState(true)
  if (!v) return null
  return (
    <div className="relative bg-gradient-to-r from-[#8B7520] via-[#D4AF37] to-[#8B7520] text-black text-xs font-bold py-2.5 text-center overflow-hidden">
      <span className="animate-pulse mr-2">⚡</span>
      OFERTA FUNDADOR — Acceso Freemium GRATIS · Primer mes Soberanía a $1,199 MXN · Expira 1 Abril
      <span className="animate-pulse mx-2">🔥</span>
      <button onClick={() => setV(false)} className="absolute right-4 top-1/2 -translate-y-1/2 text-black/60 hover:text-black text-base leading-none">✕</button>
    </div>
  )
}

// ─── Client Quiz Component ────────────────────────────────────────────────
const QUIZ_QUESTIONS = [
  { id: 'facturas', label: '¿Cuántas facturas emites por mes?', options: ['Menos de 30', 'Entre 30 y 150', 'Entre 150 y 500', 'Más de 500'] },
  { id: 'usuarios', label: '¿Cuántas personas necesitan acceso?', options: ['Solo yo', '2 a 3 personas', '4 a 8 personas', 'Más de 8'] },
  { id: 'ingresos', label: '¿Cuánto generas mensualmente?', options: ['Menos de $30k MXN', '$30k – $150k MXN', '$150k – $500k MXN', 'Más de $500k MXN'] },
  { id: 'objetivo', label: '¿Qué es lo más importante para ti?', options: ['Ahorrar en contador', 'Escalar mi negocio', 'Educación financiera', 'Automatización total'] },
]

const PLAN_MAP = [
  { min: 0, max: 3, plan: 'acceso' },
  { min: 4, max: 6, plan: 'libertad' },
  { min: 7, max: 9, plan: 'soberania' },
  { min: 10, max: 16, plan: 'poder' },
]

function ClientQuiz({ onResult }: { onResult: (plan: string) => void }) {
  const [step, setStep] = useState(0)
  const [answers, setAnswers] = useState<number[]>([])

  const choose = (idx: number) => {
    const newAnswers = [...answers, idx]
    if (step < QUIZ_QUESTIONS.length - 1) {
      setAnswers(newAnswers)
      setStep(step + 1)
    } else {
      const score = newAnswers.reduce((a, b) => a + b, 0)
      const match = PLAN_MAP.find(p => score >= p.min && score <= p.max)
      onResult(match?.plan || 'soberania')
    }
  }

  const q = QUIZ_QUESTIONS[step]
  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex gap-1 mb-8">
        {QUIZ_QUESTIONS.map((_, i) => (
          <div key={i} className={`h-1 flex-1 rounded-full transition-all duration-500 ${i <= step ? 'bg-[#D4AF37]' : 'bg-white/10'}`} />
        ))}
      </div>
      <p className="text-xs text-[#D4AF37]/70 uppercase tracking-widest mb-3">Pregunta {step + 1} de {QUIZ_QUESTIONS.length}</p>
      <h3 className="text-2xl font-bold text-white mb-8">{q.label}</h3>
      <div className="grid sm:grid-cols-2 gap-3">
        {q.options.map((opt, i) => (
          <button
            key={opt}
            onClick={() => choose(i)}
            className="text-left px-6 py-4 rounded-2xl border border-white/15 bg-white/3 hover:border-[#D4AF37]/50 hover:bg-[#D4AF37]/5 text-white/80 hover:text-white transition-all font-medium"
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

// ─── Data ─────────────────────────────────────────────────────────────────
const PLANS = [
  {
    id: 'acceso',
    name: 'Acceso',
    subtitle: 'Tu primer paso hacia la autonomía',
    badge: '🌱 FREEMIUM',
    badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    price: '$0',
    period: '/mes para siempre',
    highlight: false,
    borderColor: 'border-emerald-500/20',
    bg: 'bg-[#F8F5EE]',
    textColor: 'text-[#1a1a1a]',
    subtextColor: 'text-[#555]',
    cta: 'Empezar gratis',
    ctaClass: 'border-2 border-emerald-600 text-emerald-700 hover:bg-emerald-600 hover:text-white',
    features: [
      '30 facturas CFDI 4.0 / mes',
      '1 usuario',
      '10 consultas Brain IA / día',
      '5 posts de contenido / mes',
      '2 módulos de Academia',
      'Dashboard fiscal básico',
      'Soporte comunidad',
    ],
  },
  {
    id: 'libertad',
    name: 'Libertad',
    subtitle: 'Para el profesional que empieza a escalar',
    badge: '🔑 LIBERTAD',
    badgeClass: 'bg-sky-500/15 text-sky-300 border-sky-500/25',
    price: '$699',
    period: '/mes',
    highlight: false,
    borderColor: 'border-sky-500/20',
    bg: 'bg-[#F8F5EE]',
    textColor: 'text-[#1a1a1a]',
    subtextColor: 'text-[#555]',
    cta: 'Activar Libertad',
    ctaClass: 'border-2 border-sky-600 text-sky-700 hover:bg-sky-600 hover:text-white',
    features: [
      '150 facturas / mes',
      '3 usuarios',
      '50 consultas Brain IA / día',
      '20 posts de contenido / mes',
      '10 módulos de Academia',
      'CRM básico (50 contactos)',
      'Alertas SAT + IMSS',
      'Soporte chat 24/7',
    ],
  },
  {
    id: 'soberania',
    name: 'Soberanía',
    subtitle: 'El arsenal completo del consultor de élite',
    badge: '⚡ MÁS POPULAR',
    badgeClass: 'bg-[#D4AF37]/20 text-[#D4AF37] border-[#D4AF37]/30',
    price: '$1,699',
    period: '/mes',
    highlight: true,
    borderColor: 'border-[#D4AF37]/50',
    bg: 'bg-gradient-to-br from-[#1a1200] to-[#0a0a0f]',
    textColor: 'text-white',
    subtextColor: 'text-white/60',
    cta: 'Activar Soberanía',
    ctaClass: 'bg-gradient-to-r from-[#D4AF37] to-[#f0c842] text-black font-black hover:shadow-[0_0_30px_rgba(212,175,55,0.4)]',
    features: [
      '500 facturas / mes',
      '8 usuarios',
      'Brain IA completo + voz bidireccional',
      'Contenido ilimitado (4 plataformas)',
      'Academia completa con certificación',
      'CRM avanzado (500 contactos)',
      'Alertas configurables + push notifications',
      'Red de Aliados (recibe comisiones)',
      'Consultoría IA mensual (1 sesión)',
      'Soporte prioritario 24/7',
    ],
  },
  {
    id: 'poder',
    name: 'Poder',
    subtitle: 'Infraestructura de alto rendimiento para imperios',
    badge: '👑 ELITE',
    badgeClass: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
    price: '$3,999',
    period: '/mes',
    highlight: false,
    borderColor: 'border-violet-500/20',
    bg: 'bg-[#F8F5EE]',
    textColor: 'text-[#1a1a1a]',
    subtextColor: 'text-[#555]',
    cta: 'Construir mi Imperio',
    ctaClass: 'border-2 border-violet-600 text-violet-700 hover:bg-violet-600 hover:text-white',
    features: [
      '2,000 facturas / mes',
      '20 usuarios + roles personalizados',
      'Agente IA personal (OpenClaw)',
      'Academia white-label para tus clientes',
      'CRM empresarial ilimitado',
      'Estrategia de reinversión personalizada',
      'Kit merch: USB + kit ejecutivo Mystic',
      '4 sesiones de consultoría mensual',
      'Publicidad cruzada en Red Mystic',
      'SLA 99.9% + onboarding dedicado',
      'A.C. donataria — deducción fiscal',
    ],
  },
]

const ACADEMY_MODULES = [
  {
    track: 'Inteligencia Artificial',
    icon: Brain,
    color: 'text-cyan-400',
    borderColor: 'border-cyan-500/20',
    bg: 'from-cyan-900/10',
    modules: [
      { title: 'Fundamentos de IA para negocios', competencia: 'Identificar oportunidades de automatización', herramienta: 'ChatGPT, Claude, Ollama', objetivo: 'Ahorra 20h/mes en tareas repetitivas' },
      { title: 'Prompts de alto valor para contadores', competencia: 'Crear prompts que generan documentos fiscales', herramienta: 'Claude API, Mystic Brain', objetivo: 'Generar reportes en 2 minutos' },
      { title: 'Agentes IA personalizados', competencia: 'Construir y desplegar agentes autónomos', herramienta: 'OpenClaw, MCP Servers', objetivo: 'Tu asistente digital 24/7' },
    ],
  },
  {
    track: 'Blockchain & Cripto',
    icon: Coins,
    color: 'text-[#D4AF37]',
    borderColor: 'border-amber-500/20',
    bg: 'from-amber-900/10',
    modules: [
      { title: 'Bitcoin para empresarios mexicanos', competencia: 'Usar BTC como reserva de valor y pago', herramienta: 'Bitso, Ledger, Bitcoin Core', objetivo: 'Protege tu capital de la inflación' },
      { title: 'USDC y pagos internacionales', competencia: 'Cobrar en USD sin intermediarios', herramienta: 'Bitso, Metamask, Stellar', objetivo: 'Cobra a clientes del mundo sin banco' },
      { title: 'DeFi: finanzas sin banco', competencia: 'Generar rendimientos con criptomonedas', herramienta: 'Uniswap, AAVE, Compound', objetivo: 'Rendimientos del 5-12% anual' },
    ],
  },
  {
    track: 'Smart Contracts',
    icon: Code2,
    color: 'text-violet-400',
    borderColor: 'border-violet-500/20',
    bg: 'from-violet-900/10',
    modules: [
      { title: 'Solidity desde cero', competencia: 'Escribir contratos inteligentes funcionales', herramienta: 'Hardhat, Remix, OpenZeppelin', objetivo: 'Automatiza acuerdos comerciales' },
      { title: 'Tokeniza tu negocio', competencia: 'Crear tokens de utilidad para tu empresa', herramienta: 'ERC-20, ERC-721, Polygon', objetivo: 'Fidelización y captación de inversión' },
    ],
  },
]

const CONSULTING_SERVICES = [
  { icon: BarChart3, title: 'Estrategia Fiscal IA', desc: 'Análisis profundo de tu situación fiscal + hoja de ruta para minimizar carga tributaria legalmente. Incluye RESICO, ISR, IVA optimizados.', price: '$2,500 / sesión', tag: 'FISCAL' },
  { icon: Target, title: 'Arquitectura de Ingresos', desc: 'Diseñamos juntos tu modelo de negocio: precios, paquetes, canales de venta, funnel automático con IA. Te ayudamos a cobrar lo que mereces.', price: '$3,500 / sesión', tag: 'VENTAS' },
  { icon: Globe, title: 'Expansión Digital', desc: 'Estrategia de contenido + presencia web + automatización completa. De 0 a 500 seguidores calificados en 90 días con el sistema Mystic.', price: '$4,000 / mes', tag: 'MARKETING' },
  { icon: Wallet, title: 'Onboarding Cripto Empresarial', desc: 'Te llevamos de la mano: wallet segura, primera transacción en BTC/USDC, integración en tu negocio, estrategia de reserva de valor.', price: '$1,500 / sesión', tag: 'CRIPTO' },
]

// ─── Score Segments ──────────────────────────────────────────────────────────
const SCORE_SEGMENTS = [
  {
    name: 'Explorador',
    range: '0 – 249',
    color: 'text-slate-400',
    bg: 'bg-slate-500/10 border-slate-500/20',
    bar: 'bg-slate-400',
    pct: 25,
    desc: 'Acaba de descubrir el sistema. Le mostramos valor rápido.',
    signal: ['< 10 facturas/mes', 'Poco uso Brain IA', 'Sin cursos completados'],
    offer: 'Flash: 1er mes Libertad a $399',
  },
  {
    name: 'Activo',
    range: '250 – 499',
    color: 'text-sky-400',
    bg: 'bg-sky-500/10 border-sky-500/20',
    bar: 'bg-sky-400',
    pct: 50,
    desc: 'Usa la plataforma con regularidad. Listo para escalar.',
    signal: ['30-100 facturas/mes', '10+ consultas/día Brain', '1-2 módulos academia'],
    offer: 'Upgrade a Soberanía + 1 sesión consultoría gratis',
  },
  {
    name: 'Estratégico',
    range: '500 – 749',
    color: 'text-[#D4AF37]',
    bg: 'bg-amber-500/10 border-amber-500/20',
    bar: 'bg-[#D4AF37]',
    pct: 75,
    desc: 'Operador de alto rendimiento. Candidato a Poder.',
    signal: ['100+ facturas/mes', 'Referidos activos', '3+ cursos completados'],
    offer: 'NFT Estratega + acceso beta features',
  },
  {
    name: 'Élite',
    range: '750 – 1000',
    color: 'text-violet-400',
    bg: 'bg-violet-500/10 border-violet-500/20',
    bar: 'bg-violet-500',
    pct: 100,
    desc: 'Embajador Mystic. Acceso total + mentoría 1v1.',
    signal: ['500+ facturas/mes', '5+ referidos activos', 'Academia certificado'],
    offer: 'NFT Élite + mentoría semanal 1v1 + merch exclusivo',
  },
]

// ─── NFT Tiers ────────────────────────────────────────────────────────────────
const NFT_TIERS = [
  {
    tier: 'Acceso',
    symbol: '◈',
    color: 'text-slate-300',
    border: 'border-slate-500/30',
    bg: 'from-slate-800/30',
    price: '50 $MYS',
    perks: ['Acceso a sala privada Telegram', 'Badge verificado en perfil', 'Descuentos en merch básico'],
  },
  {
    tier: 'Estratega',
    symbol: '⬡',
    color: 'text-[#D4AF37]',
    border: 'border-amber-500/40',
    bg: 'from-amber-900/20',
    price: '250 $MYS',
    perks: ['Acceso anticipado a features beta', 'Hack fiscal exclusivo / mes', 'Foto de perfil NFT certificada', 'Insignia oro en todo el ecosistema'],
  },
  {
    tier: 'Élite',
    symbol: '◆',
    color: 'text-violet-400',
    border: 'border-violet-500/40',
    bg: 'from-violet-900/20',
    price: '1,000 $MYS',
    perks: ['Mentoría 1v1 mensual (4 sesiones)', 'Acceso vitalicio a un módulo', 'NFT coleccionable edición limitada', 'Voto en roadmap de features', 'Comisiones 20% para siempre'],
  },
]

// ─── Testimonials ────────────────────────────────────────────────────────────
const TESTIMONIALS = [
  {
    name: 'María E. González Ruiz',
    role: 'Contadora Pública',
    city: 'Hermosillo, Sonora',
    avatar: 'MG',
    avatarBg: 'bg-rose-700',
    score: 820,
    tier: 'Élite',
    quote: 'Antes tardaba 3 días en cerrar la contabilidad de cada cliente. Ahora lo hago en 40 minutos con el Brain IA. Subí mis honorarios un 60% porque entrego más valor en menos tiempo.',
    result: '+$18,000 MXN/mes extra en honorarios',
    stars: 5,
  },
  {
    name: 'Carlos R. Valenzuela',
    role: 'Importador y Agente Aduanal',
    city: 'Nogales, Sonora',
    avatar: 'CV',
    avatarBg: 'bg-sky-700',
    score: 710,
    tier: 'Estratégico',
    quote: 'El sistema MVE antimultas me salvó de una multa de $240,000 MXN. El aviso llegó por Telegram a las 6am antes de que venciera el plazo. Eso solo ya pagó el sistema por 10 años.',
    result: '$240,000 MXN en multas evitadas',
    stars: 5,
  },
  {
    name: 'Ana Sofía Beltrán',
    role: 'Emprendedora · E-commerce',
    city: 'Guaymas, Sonora',
    avatar: 'AB',
    avatarBg: 'bg-violet-700',
    score: 490,
    tier: 'Activo',
    quote: 'No tenía contador y tenía miedo de los impuestos. Mystic me enseñó RESICO en un fin de semana y ahora declaro yo misma. La academia de Blockchain me abrió un mundo completamente nuevo.',
    result: '$8,500 MXN/mes ahorrado en contador',
    stars: 5,
  },
  {
    name: 'Roberto A. Félix Mendez',
    role: 'Dueño de Restaurantes (3 sucursales)',
    city: 'Ciudad Obregón, Sonora',
    avatar: 'RF',
    avatarBg: 'bg-emerald-700',
    score: 650,
    tier: 'Estratégico',
    quote: 'Tenía a un contador cobrándome $15,000/mes por hacer lo mismo que Mystic hace automáticamente. Ahora ese dinero va a expandir mi negocio. La IA nunca se enferma, nunca llega tarde.',
    result: '$180,000 MXN ahorrado al año',
    stars: 5,
  },
  {
    name: 'Ing. Patricia Morales',
    role: 'Despacho Contable (12 clientes)',
    city: 'Culiacán, Sinaloa',
    avatar: 'PM',
    avatarBg: 'bg-amber-700',
    score: 890,
    tier: 'Élite',
    quote: 'Tengo 12 clientes y con Mystic los atiendo sola. Antes necesitaba 2 asistentes. El Content Factory genera el contenido para mis clientes automáticamente. Mis clientes están felices y yo duermo 8 horas.',
    result: '$35,000 MXN/mes más sin contratar personal',
    stars: 5,
  },
  {
    name: 'Miguel Á. Contreras',
    role: 'Contador PYME · RESICO',
    city: 'Los Mochis, Sinaloa',
    avatar: 'MC',
    avatarBg: 'bg-indigo-700',
    score: 380,
    tier: 'Activo',
    quote: 'Empecé con el plan Acceso para probar. A las 2 semanas ya estaba en Soberanía. El Brain IA resuelve en segundos lo que me tomaba consultar libros por horas. Es como tener un SAT advisor 24/7.',
    result: 'De 5 a 18 clientes en 3 meses',
    stars: 5,
  },
]

const UNIFORMS = [
  {
    name: 'Ejecutivo Clásico',
    desc: 'Traje oxford azul marino profundo, corbata dorada con triángulo Mystic bordado, camisa blanca perla. Solapa con pin del ojo místico.',
    colors: ['#0d1b2a', '#D4AF37', '#F5F0E8'],
    context: 'Juntas directivas, cierres de alto ticket, eventos corporativos',
    icon: '👔',
  },
  {
    name: 'Consultora Élite',
    desc: 'Blazer crema con vivos dorados, blusa de seda ivory, pantalón negro. Insignia del triángulo en el bolsillo superior.',
    colors: ['#F5F0E8', '#D4AF37', '#1a1a1a'],
    context: 'Consultoría presencial, presentaciones, networking',
    icon: '🥼',
  },
  {
    name: 'Digital Force',
    desc: 'Polo negro técnico con logo Mystic 3D en pecho, pantalón cargo gris carbón, tenis blancos. Para el equipo en campo y eventos tech.',
    colors: ['#1a1a1a', '#D4AF37', '#9ca3af'],
    context: 'Eventos tech, trabajo en campo, representación casual',
    icon: '👕',
  },
]

// ─── Component ────────────────────────────────────────────────────────────────
export default function HomePage() {
  const [quizDone, setQuizDone] = useState(false)
  const [recommendedPlan, setRecommendedPlan] = useState('')
  const [showQuiz, setShowQuiz] = useState(false)
  const [openModule, setOpenModule] = useState<string | null>(null)

  const handleQuizResult = (plan: string) => {
    setRecommendedPlan(plan)
    setQuizDone(true)
    setTimeout(() => {
      document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })
    }, 400)
  }

  return (
    <main className="min-h-screen text-[#1a1a1a] overflow-x-hidden" style={{ background: '#F5F0E8' }}>
      <FlashBanner />

      {/* ── NAV ────────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-[#D4AF37]/20 bg-[#F5F0E8]/95 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
          <div className="flex items-center gap-3">
            <MysticEyeLogo size={42} />
            <div>
              <p className="text-[9px] font-bold uppercase tracking-[0.35em] text-[#8B7520]">Sonora Digital Corp</p>
              <p className="text-sm font-black text-[#1a1a1a] leading-none tracking-tight">MYSTIC CONSULTING</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-7 text-sm text-[#555] font-medium">
            <a href="#quiz" className="hover:text-[#D4AF37] transition-colors">¿Qué plan me conviene?</a>
            <a href="#pricing" className="hover:text-[#D4AF37] transition-colors">Planes</a>
            <a href="#academia" className="hover:text-[#D4AF37] transition-colors">Academia</a>
            <a href="#consulting" className="hover:text-[#D4AF37] transition-colors">Consultoría</a>
            <a href="#cripto" className="hover:text-[#D4AF37] transition-colors">Cripto</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link href="/login" className="px-4 py-2 text-sm text-[#555] hover:text-[#1a1a1a] font-medium transition-colors">
              Entrar
            </Link>
            <Link
              href="/login"
              className="px-5 py-2.5 bg-[#1a1a1a] text-[#D4AF37] text-sm font-bold rounded-xl hover:bg-[#D4AF37] hover:text-black transition-all border border-[#D4AF37]/40"
            >
              Empezar gratis
            </Link>
          </div>
        </div>
      </header>

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section className="relative min-h-[95vh] flex items-center justify-center overflow-hidden bg-[#020208]">
        <ParticleField />
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-[#D4AF37]/5 rounded-full blur-[130px]" />
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-violet-500/4 rounded-full blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto px-6 py-32 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-[#D4AF37]/25 bg-[#D4AF37]/8 px-5 py-2 text-sm text-[#D4AF37] mb-10">
            <Sparkles className="w-3.5 h-3.5" />
            La consultoría que los contadores no quieren que conozcas
            <span className="bg-[#D4AF37] text-black text-[10px] font-black px-2 py-0.5 rounded-full ml-1">2026</span>
          </div>

          {/* Headline — estilo Miguel Baena */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-[1.05] tracking-tight mb-8 text-white">
            <span className="block">Si tu negocio no tiene</span>
            <span className="block bg-gradient-to-r from-[#D4AF37] via-[#f0c842] to-[#D4AF37] bg-clip-text text-transparent py-1">
              inteligencia artificial,
            </span>
            <span className="block">ya está perdiendo.</span>
          </h1>

          <p className="mx-auto max-w-2xl text-lg text-white/55 leading-relaxed mb-4">
            Mientras tú procesas facturas a mano, tu competencia ya automatizó todo. Mystic Consulting es el sistema que convierte a cualquier PYME mexicana en una empresa de alto rendimiento — en menos de 30 días.
          </p>
          <p className="text-sm text-[#D4AF37]/80 mb-12 font-semibold">
            Hermosillo, Sonora → para el mundo. Tecnología de clase mundial, precio mexicano.
          </p>

          {/* Countdown */}
          <div className="flex flex-col items-center gap-2 mb-10">
            <p className="text-xs uppercase tracking-widest text-white/30">Oferta fundador expira en</p>
            <Countdown />
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#D4AF37] to-[#f0c842] text-black font-black text-base rounded-2xl hover:shadow-[0_0_50px_rgba(212,175,55,0.4)] transition-all"
            >
              <Zap className="w-5 h-5" />
              Acceso freemium — GRATIS
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="#quiz"
              className="inline-flex items-center gap-2 px-8 py-4 border border-white/15 text-white font-medium text-base rounded-2xl hover:bg-white/5 transition-all"
            >
              ¿Qué plan me conviene?
              <ChevronDown className="w-4 h-4 text-[#D4AF37]" />
            </a>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {[
              { n: '147', l: 'Cálculos SAT', c: 'text-[#D4AF37]' },
              { n: '$110k', l: 'MXN ahorrados/mes', c: 'text-emerald-400' },
              { n: '4', l: 'Redes auto-publicadas', c: 'text-cyan-400' },
              { n: '24/7', l: 'Asistente por voz', c: 'text-violet-400' },
            ].map(({ n, l, c }) => (
              <TiltCard key={l}>
                <div className="rounded-2xl border border-white/8 bg-white/3 backdrop-blur p-5 text-center">
                  <p className={`text-3xl font-black ${c}`}>{n}</p>
                  <p className="text-xs text-white/40 mt-1">{l}</p>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROI PROOF BAR ────────────────────────────────────────────────── */}
      <section className="py-8 bg-[#D4AF37]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid sm:grid-cols-3 gap-6 text-center">
            {[
              { n: '10,910%', l: 'ROI promedio primer mes', sub: 'vs costo de Soberanía $1,699' },
              { n: '40 hrs', l: 'Ahorradas por contador/mes', sub: 'Que puedes vender a $500/hr' },
              { n: '$20,000+', l: 'Valor extra que puedes cobrar', sub: 'Con los mismos clientes actuales' },
            ].map(({ n, l, sub }) => (
              <div key={l} className="text-black">
                <p className="text-4xl font-black">{n}</p>
                <p className="font-bold text-sm mt-1">{l}</p>
                <p className="text-xs text-black/60 mt-0.5">{sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── QUIZ ─────────────────────────────────────────────────────────── */}
      <section id="quiz" className="py-24 bg-[#0d0d12]">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-14">
            <p className="text-sm font-semibold uppercase tracking-widest text-[#D4AF37]/70 mb-3">Filtro de Diagnóstico</p>
            <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
              ¿Cuánto dinero estás dejando<br />
              <span className="text-[#D4AF37]">en la mesa cada mes?</span>
            </h2>
            <p className="text-white/45 max-w-xl mx-auto">
              Responde 4 preguntas y el sistema te dice exactamente qué plan saca más ventaja de tu situación actual. Sin compromisos.
            </p>
          </div>

          {!showQuiz && !quizDone ? (
            <div className="text-center">
              <button
                onClick={() => setShowQuiz(true)}
                className="inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-[#D4AF37] to-[#f0c842] text-black font-black text-lg rounded-2xl hover:shadow-[0_0_40px_rgba(212,175,55,0.4)] transition-all"
              >
                <Target className="w-5 h-5" />
                Descubrir mi plan ideal — gratis
                <ArrowRight className="w-5 h-5" />
              </button>
              <p className="mt-4 text-xs text-white/30">No se requiere registro · 30 segundos</p>
            </div>
          ) : quizDone ? (
            <div className="text-center">
              <div className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl border border-[#D4AF37]/40 bg-[#D4AF37]/10 mb-6">
                <CheckSquare className="w-6 h-6 text-[#D4AF37]" />
                <div className="text-left">
                  <p className="text-xs text-[#D4AF37]/70 uppercase tracking-wider">Tu plan recomendado</p>
                  <p className="text-2xl font-black text-white capitalize">{recommendedPlan}</p>
                </div>
              </div>
              <p className="text-white/50 mb-6">Basado en tus respuestas, este plan maximiza tu ROI inmediato.</p>
              <a href="#pricing" className="inline-flex items-center gap-2 px-7 py-3.5 bg-[#D4AF37] text-black font-bold rounded-xl hover:bg-[#f0c842] transition-colors">
                Ver mi plan <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          ) : (
            <ClientQuiz onResult={handleQuizResult} />
          )}
        </div>
      </section>

      {/* ── PRICING ───────────────────────────────────────────────────────── */}
      <section id="pricing" className="py-24 bg-[#F5F0E8]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Planes y Precios</p>
            <h2 className="text-4xl sm:text-5xl font-black text-[#1a1a1a]">
              El precio del éxito es menor<br />
              <span className="text-[#8B7520]">al costo del fracaso.</span>
            </h2>
            <p className="mt-4 text-[#555] max-w-xl mx-auto">
              Cada plan tiene límites coherentes con su precio. Nada prometido que no podamos entregar. Todo documentado. Sin letra chica.
            </p>
            {recommendedPlan && (
              <div className="inline-flex items-center gap-2 mt-4 bg-[#D4AF37]/20 border border-[#D4AF37]/40 rounded-full px-5 py-2 text-sm text-[#8B7520] font-semibold">
                <Star className="w-4 h-4" /> Tu diagnóstico recomienda el plan <span className="capitalize font-black">{recommendedPlan}</span>
              </div>
            )}
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {PLANS.map(plan => {
              const isRecommended = recommendedPlan === plan.id
              return (
                <TiltCard key={plan.id}>
                  <div className={`relative flex flex-col h-full rounded-3xl border-2 ${plan.borderColor} ${plan.bg} p-7 ${plan.highlight ? 'shadow-[0_0_40px_rgba(212,175,55,0.15)]' : 'shadow-lg'} ${isRecommended ? 'ring-2 ring-[#D4AF37]' : ''}`}>
                    {isRecommended && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#D4AF37] text-black text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wide whitespace-nowrap">
                        ★ Recomendado para ti
                      </div>
                    )}
                    {plan.highlight && (
                      <div className="absolute -top-px left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent rounded-t-3xl" />
                    )}
                    <div className={`self-start text-[11px] font-bold px-3 py-1 rounded-full border ${plan.badgeClass} mb-5`}>
                      {plan.badge}
                    </div>
                    <p className={`text-2xl font-black ${plan.textColor} mb-1`}>{plan.name}</p>
                    <p className={`text-xs ${plan.subtextColor} mb-5 leading-snug`}>{plan.subtitle}</p>
                    <div className="flex items-end gap-1 mb-6">
                      <span className={`text-4xl font-black ${plan.textColor}`}>{plan.price}</span>
                      <span className={`${plan.subtextColor} mb-1.5 text-xs`}>{plan.period}</span>
                    </div>
                    <ul className="space-y-2.5 flex-1 mb-8">
                      {plan.features.map(f => (
                        <li key={f} className={`flex items-start gap-2 text-xs ${plan.subtextColor}`}>
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
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
              )
            })}
          </div>

          <p className="text-center mt-8 text-sm text-[#888]">
            Paga con SPEI · BTC · USDC · Tarjeta MX · OXXO — Factura fiscal disponible
          </p>
          <p className="text-center mt-2 text-xs text-[#aaa]">
            ¿Eres contador y ya tienes clientes? Pregunta por nuestro precio de revendedor. Tu plan se paga solo con el primer cliente que migryes.
          </p>
        </div>
      </section>

      {/* ── CRIPTO ────────────────────────────────────────────────────────── */}
      <section id="cripto" className="py-24 bg-[#020208]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-sm font-bold uppercase tracking-widest text-[#D4AF37]/70 mb-4">Pagos del Futuro</p>
              <h2 className="text-4xl font-black text-white mb-6 leading-tight">
                El peso pierde valor.<br />
                <span className="text-[#D4AF37]">Bitcoin nunca.</span>
              </h2>
              <p className="text-white/50 leading-relaxed mb-8">
                Mystic acepta pagos en Bitcoin y USDC porque creemos en la soberanía financiera. No dependas de bancos, no pagues comisiones absurdas, no esperes 3 días hábiles. Paga desde tu wallet en segundos.
              </p>
              <div className="space-y-4 mb-8">
                {[
                  { icon: '₿', label: 'Bitcoin (BTC)', desc: 'Red principal · Lightning Network disponible', color: 'text-orange-400' },
                  { icon: '◎', label: 'USDC / USDT', desc: 'Stablecoins en red Stellar o Polygon', color: 'text-sky-400' },
                  { icon: '🏦', label: 'SPEI + OXXO', desc: 'Para quienes aún no dan el salto cripto', color: 'text-emerald-400' },
                ].map(({ icon, label, desc, color }) => (
                  <div key={label} className="flex items-center gap-4 p-4 rounded-2xl border border-white/8 bg-white/3">
                    <span className={`text-2xl ${color}`}>{icon}</span>
                    <div>
                      <p className="text-white font-bold text-sm">{label}</p>
                      <p className="text-white/40 text-xs">{desc}</p>
                    </div>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 ml-auto" />
                  </div>
                ))}
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <Link href="/login" className="inline-flex items-center gap-2 px-6 py-3 bg-[#D4AF37] text-black font-bold rounded-xl hover:bg-[#f0c842] transition-colors">
                  <Wallet className="w-4 h-4" /> Conectar mi wallet
                </Link>
                <a
                  href="https://bitso.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 border border-white/15 text-white font-medium rounded-xl hover:bg-white/5 transition-colors"
                >
                  <ExternalLink className="w-4 h-4 text-[#D4AF37]" /> Crear cuenta en Bitso
                </a>
              </div>
              <p className="text-xs text-white/25 mt-3">¿No tienes wallet? Te guiamos desde cero. La educación cripto está incluida en todos los planes.</p>
            </div>
            <div className="space-y-4">
              <div className="rounded-3xl border border-[#D4AF37]/20 bg-[#D4AF37]/3 p-8">
                <Coins className="w-10 h-10 text-[#D4AF37] mb-4" />
                <h3 className="text-xl font-black text-white mb-2">¿Por qué pagar en cripto?</h3>
                <ul className="space-y-3 text-sm text-white/50">
                  {[
                    'Sin comisión bancaria (ahorras 3-5% por transacción)',
                    'Privacidad financiera garantizada',
                    'Tus pagos no se pueden congelar ni bloquear',
                    'Descuento del 5% en todos los planes pagando en BTC/USDC',
                    'Construyes historial cripto para crédito futuro',
                  ].map(item => (
                    <li key={item} className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="rounded-3xl border border-white/8 bg-white/2 p-6 text-center">
                <p className="text-xs text-white/30 uppercase tracking-widest mb-2">Próximamente</p>
                <p className="text-white font-bold">Staking de tokens Mystic</p>
                <p className="text-xs text-white/40 mt-1">Gana rendimientos por participar en la red</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CONTENT FACTORY ──────────────────────────────────────────────── */}
      <section className="py-24 bg-[#F5F0E8]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Content Factory</p>
            <h2 className="text-4xl sm:text-5xl font-black text-[#1a1a1a]">
              Contenido para tus clientes.<br />
              <span className="text-[#8B7520]">Un click. Cuatro plataformas.</span>
            </h2>
            <p className="mt-4 text-[#666] max-w-2xl mx-auto">
              Cada 6 horas, la IA genera posts optimizados en tu tono, con hashtags, horario y formato correcto para cada red. Tú cierras clientes mientras el sistema trabaja.
            </p>
          </div>
          <TiltCard>
            <div className="max-w-4xl mx-auto rounded-3xl border border-[#D4AF37]/20 bg-[#020208] p-6">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="ml-2 text-xs text-white/25 font-mono">mystic-content-factory · ciclo automático cada 6h</span>
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  { p: 'Instagram', e: '📸', c: 'from-purple-600/15 to-pink-600/15 border-purple-500/25', t: '🔮 Tu contador está cobrándote $8,000/mes por hacer esto en 2 horas. Nosotros lo automatizamos en 3 minutos. #FiscalIA #PYMEsMéxico #Hermosillo' },
                  { p: 'TikTok', e: '🎵', c: 'from-gray-700/15 to-black/20 border-gray-600/25', t: 'Truco que tu contador no quiere que sepas: con IA puedes generar tu declaración anual en 4 minutos. Thread 🧵 #Contador #ISR2026' },
                  { p: 'LinkedIn', e: '💼', c: 'from-blue-700/15 to-blue-900/15 border-blue-600/25', t: 'Las PYMEs que automatizaron su contabilidad con IA en Q1 2026 reportan un ahorro promedio de 40hrs/mes. ROI del sistema: 10,910%. El dato completo ↓' },
                  { p: 'X / Twitter', e: '✖️', c: 'from-gray-600/15 to-gray-800/15 border-gray-500/25', t: 'Si eres contador y no tienes IA en tu flujo de trabajo, alguien más ya está ofreciendo lo mismo que tú por la mitad del tiempo y el doble de margen →' },
                ].map(({ p, e, c, t }) => (
                  <div key={p} className={`rounded-2xl border bg-gradient-to-br ${c} p-4`}>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-base">{e}</span>
                      <span className="text-xs font-bold text-white/80">{p}</span>
                      <span className="ml-auto text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full">Auto ✓</span>
                    </div>
                    <p className="text-xs text-white/55 leading-relaxed">{t}</p>
                  </div>
                ))}
              </div>
            </div>
          </TiltCard>
        </div>
      </section>

      {/* ── ACADEMIA ─────────────────────────────────────────────────────── */}
      <section id="academia" className="py-24 bg-[#0d0d12]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-violet-400/70 mb-3">Escuela Mystic</p>
            <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
              Aprende. Certifícate.<br />
              <span className="text-violet-400">Cobra más.</span>
            </h2>
            <p className="text-white/45 max-w-2xl mx-auto">
              Cada módulo tiene objetivo práctico aplicable a tu negocio en la semana siguiente. No es teoría. Es dinero.
            </p>
            <div className="mt-4 inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-2 text-sm text-violet-300">
              <Award className="w-4 h-4" /> Certificado Mystic · Currículum reconocido · Sell what you learn
            </div>
          </div>

          <div className="space-y-5">
            {ACADEMY_MODULES.map((track) => {
              const Icon = track.icon
              const isOpen = openModule === track.track
              return (
                <div key={track.track} className={`rounded-3xl border ${track.borderColor} bg-gradient-to-br ${track.bg} to-transparent overflow-hidden`}>
                  <button
                    onClick={() => setOpenModule(isOpen ? null : track.track)}
                    className="w-full flex items-center justify-between p-7 text-left hover:bg-white/2 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <Icon className={`w-8 h-8 ${track.color} shrink-0`} />
                      <div>
                        <h3 className="text-lg font-black text-white">{track.track}</h3>
                        <p className="text-sm text-white/40">{track.modules.length} módulos · Acceso con todos los planes</p>
                      </div>
                    </div>
                    <ChevronDown className={`w-5 h-5 text-white/40 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                  </button>
                  {isOpen && (
                    <div className="px-7 pb-7 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {track.modules.map((mod) => (
                        <div key={mod.title} className="rounded-2xl border border-white/8 bg-white/3 p-5">
                          <p className="font-bold text-white text-sm mb-4">{mod.title}</p>
                          <div className="space-y-3 text-xs">
                            <div>
                              <p className="text-white/30 uppercase tracking-wider mb-1">Competencia</p>
                              <p className="text-white/60">{mod.competencia}</p>
                            </div>
                            <div>
                              <p className="text-white/30 uppercase tracking-wider mb-1">Herramientas</p>
                              <p className="text-white/60">{mod.herramienta}</p>
                            </div>
                            <div className="pt-2 border-t border-white/8">
                              <p className={`font-bold ${track.color}`}>🎯 {mod.objetivo}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          <div className="mt-12 text-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-4 bg-violet-600 hover:bg-violet-500 text-white font-bold rounded-2xl transition-all"
            >
              <BookOpen className="w-5 h-5" /> Acceder a la Academia completa
              <ChevronRight className="w-4 h-4" />
            </Link>
            <p className="mt-3 text-xs text-white/25">Los primeros 2 módulos son gratis con el plan Acceso</p>
          </div>
        </div>
      </section>

      {/* ── MYSTIC CONSULTING ────────────────────────────────────────────── */}
      <section id="consulting" className="py-24 bg-[#F5F0E8]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Mystic Consulting</p>
            <h2 className="text-4xl sm:text-5xl font-black text-[#1a1a1a] mb-4">
              No solo software.<br />
              <span className="text-[#8B7520]">Estrategia de élite.</span>
            </h2>
            <p className="text-[#555] max-w-xl mx-auto">
              Para quienes quieren resultados en semanas, no meses. Sesiones privadas con nuestro equipo de consultores especializados en IA fiscal, finanzas y negocios digitales.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {CONSULTING_SERVICES.map(({ icon: Icon, title, desc, price, tag }) => (
              <TiltCard key={title}>
                <div className="flex flex-col h-full rounded-3xl border border-[#D4AF37]/20 bg-white shadow-sm p-7">
                  <span className="self-start text-[10px] font-black bg-[#1a1a1a] text-[#D4AF37] px-3 py-1 rounded-full uppercase tracking-widest mb-5">{tag}</span>
                  <div className="w-10 h-10 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center mb-5">
                    <Icon className="w-5 h-5 text-[#8B7520]" />
                  </div>
                  <h3 className="text-base font-black text-[#1a1a1a] mb-3">{title}</h3>
                  <p className="text-xs text-[#666] leading-relaxed flex-1">{desc}</p>
                  <div className="mt-6 pt-4 border-t border-[#e8e0d0]">
                    <p className="text-[#8B7520] font-black text-base">{price}</p>
                    <button className="mt-3 w-full py-2.5 border-2 border-[#D4AF37] text-[#8B7520] text-sm font-bold rounded-xl hover:bg-[#D4AF37] hover:text-black transition-all">
                      Reservar sesión
                    </button>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── VS COMPETIDORES ───────────────────────────────────────────────── */}
      <section className="py-20 bg-[#020208]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12">
            <p className="text-sm font-bold uppercase tracking-widest text-rose-400/70 mb-3">Comparativa directa</p>
            <h2 className="text-3xl sm:text-4xl font-black text-white">¿Por qué no Factura.com?</h2>
            <p className="text-white/35 mt-2">Ellos facturan. Nosotros transformamos negocios.</p>
          </div>
          <div className="overflow-x-auto rounded-2xl border border-white/8">
            <table className="w-full">
              <thead className="bg-white/3">
                <tr>
                  <th className="text-left text-xs text-white/40 py-4 px-5 font-medium">Característica</th>
                  {['Factura.com', 'CONTPAQi', 'Mystic'].map(n => (
                    <th key={n} className={`text-center py-4 px-4 text-sm font-bold ${n === 'Mystic' ? 'text-[#D4AF37]' : 'text-white/30'}`}>
                      {n === 'Mystic' && <Crown className="w-4 h-4 inline mr-1" />}{n}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  ['Contabilidad IA', '✓ básico', '✓ legacy', '✓✓✓ 147 cálculos'],
                  ['Generación de contenido', '✗', '✗', '✓ 4 plataformas'],
                  ['Academia certificada', '✗', '✗', '✓ Blockchain · IA · NFT'],
                  ['Voz bidireccional 24/7', '✗', '✗', '✓'],
                  ['Pagos en Bitcoin/USDC', '✗', '✗', '✓ + descuento 5%'],
                  ['Consultoría personalizada', '✗', '✗', '✓ Mystic Consulting'],
                  ['Red de aliados (ingresos extra)', '✗', '✗', '✓ comisiones recurrentes'],
                  ['IA local soberana (sin nube)', '✗', '✗', '✓ Ollama + Qdrant'],
                ].map(([feat, ...vals]) => (
                  <tr key={feat} className="border-t border-white/5 hover:bg-white/2 transition-colors">
                    <td className="py-3.5 px-5 text-sm text-white/55">{feat}</td>
                    {vals.map((v, i) => (
                      <td key={i} className={`py-3.5 px-4 text-center text-sm ${i === 2 ? 'text-[#D4AF37] font-semibold' : 'text-white/25'}`}>
                        {v.startsWith('✗') ? <span className="text-red-500/40">✗</span> : v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── RED DE ALIADOS (Afiliados rebranded) ─────────────────────────── */}
      <section className="py-24 bg-[#F5F0E8]">
        <div className="max-w-5xl mx-auto px-6">
          <div className="rounded-3xl border-2 border-[#D4AF37]/30 bg-white p-10 shadow-xl">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Red de Aliados</p>
                <h2 className="text-3xl sm:text-4xl font-black text-[#1a1a1a] mb-4">
                  Tu red es tu<br />
                  <span className="text-[#8B7520]">segundo ingreso.</span>
                </h2>
                <p className="text-[#666] leading-relaxed mb-6">
                  Cada persona que conectas a Mystic genera ingresos para ti. Mes tras mes. Sin límite. Los mejores aliados con 10 clientes activos ya pagan su propio plan y generan ingreso extra neto.
                </p>
                <div className="space-y-3">
                  {[
                    { label: 'Comisión mensual recurrente', value: '15%', c: 'text-emerald-600' },
                    { label: 'Bono de activación por cliente', value: '$300 MXN', c: 'text-[#8B7520]' },
                    { label: 'Bonus ranking mensual', value: 'hasta $5,000', c: 'text-violet-600' },
                  ].map(({ label, value, c }) => (
                    <div key={label} className="flex items-center justify-between py-3 border-b border-[#e8e0d0]">
                      <span className="text-sm text-[#555]">{label}</span>
                      <span className={`font-black text-lg ${c}`}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-4">
                <div className="rounded-2xl bg-[#F5F0E8] border border-[#D4AF37]/20 p-6">
                  <p className="text-xs text-[#888] uppercase tracking-wider mb-2">Ejemplo real</p>
                  <p className="text-3xl font-black text-[#1a1a1a]">$25,485 MXN</p>
                  <p className="text-sm text-[#666] mt-1">ingreso mensual con 10 aliados activos en plan Soberanía</p>
                </div>
                <Link
                  href="/login"
                  className="flex items-center justify-center gap-2 py-4 bg-[#1a1a1a] text-[#D4AF37] font-bold rounded-2xl hover:bg-[#D4AF37] hover:text-black transition-all border border-[#D4AF37]/40"
                >
                  <Users className="w-4 h-4" /> Unirme a la Red de Aliados
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── UNIFORMES ─────────────────────────────────────────────────────── */}
      <section className="py-24 bg-[#0d0d12]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#D4AF37]/70 mb-3">Imagen Corporativa</p>
            <h2 className="text-4xl font-black text-white mb-4">
              La primera impresión<br />
              <span className="text-[#D4AF37]">cierra el trato.</span>
            </h2>
            <p className="text-white/40 max-w-xl mx-auto">Tres líneas de uniforme para cada contexto de negocios. Diseñadas para comunicar poder, confianza y modernidad.</p>
          </div>
          <div className="grid sm:grid-cols-3 gap-6">
            {UNIFORMS.map((u) => (
              <TiltCard key={u.name}>
                <div className="rounded-3xl border border-white/8 bg-[#0a0a0f] p-7">
                  <div className="text-center text-6xl mb-6">{u.icon}</div>
                  {/* Color swatches */}
                  <div className="flex justify-center gap-2 mb-5">
                    {u.colors.map((c, i) => (
                      <div key={i} className="w-8 h-8 rounded-full border-2 border-white/20 shadow-lg" style={{ backgroundColor: c }} />
                    ))}
                  </div>
                  <h3 className="text-lg font-black text-white text-center mb-3">{u.name}</h3>
                  <p className="text-sm text-white/50 text-center leading-relaxed mb-4">{u.desc}</p>
                  <div className="rounded-xl bg-white/5 border border-white/8 p-3 text-center">
                    <p className="text-[10px] text-white/30 uppercase tracking-wider mb-1">Contexto ideal</p>
                    <p className="text-xs text-[#D4AF37] font-medium">{u.context}</p>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
          <p className="text-center mt-8 text-xs text-white/25">
            Producción bajo pedido · Incluye bordado del logo Mystic · Mínimo 2 piezas por línea
          </p>
        </div>
      </section>

      {/* ── MERCH ─────────────────────────────────────────────────────────── */}
      <section className="py-24 bg-[#F5F0E8]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Tienda Mystic</p>
            <h2 className="text-4xl font-black text-[#1a1a1a]">
              Porta la identidad.<br />
              <span className="text-[#8B7520]">Cierra negocios con estilo.</span>
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              { name: 'USB Mystic 32GB', desc: 'Agente digital en el bolsillo. Precargada con herramientas Mystic + biblioteca fiscal.', emoji: '💾', price: '$299' },
              { name: 'Kit Ejecutivo', desc: 'Pluma cromada + cuaderno de piel + stickers. Para cerrar tratos de alto valor.', emoji: '🖊️', price: '$249' },
              { name: 'Hoodie Mystic', desc: 'Colección limitada fundadores. 100% algodón premium con logo ojo místico bordado.', emoji: '👕', price: '$699' },
              { name: 'Pack Fundador', desc: 'USB + kit + hoodie + certificado fundador + acceso especial. Solo 100 unidades.', emoji: '👑', price: '$1,199' },
            ].map(({ name, desc, emoji, price }) => (
              <TiltCard key={name}>
                <div className="rounded-3xl border border-[#D4AF37]/20 bg-white shadow-sm p-7 text-center flex flex-col gap-4 h-full">
                  <div className="text-5xl">{emoji}</div>
                  <div className="flex-1">
                    <h3 className="font-black text-[#1a1a1a] mb-2">{name}</h3>
                    <p className="text-xs text-[#666]">{desc}</p>
                  </div>
                  <div className="text-[#8B7520] font-black text-2xl">{price} MXN</div>
                  <button className="py-3 border-2 border-[#D4AF37] text-[#8B7520] text-sm font-bold rounded-xl hover:bg-[#D4AF37] hover:text-black transition-all">
                    Pre-ordenar
                  </button>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* ── ANTIMULTAS MVE — PRODUCTO #1 ─────────────────────────────────── */}
      <section className="py-24 bg-[#020208] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-rose-900/10 to-transparent pointer-events-none" />
        <div className="max-w-6xl mx-auto px-6 relative">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-rose-500/15 border border-rose-500/30 rounded-full px-4 py-2 text-sm text-rose-300 font-bold mb-6">
                <Flame className="w-4 h-4" /> PRODUCTO #1 MÁS VENDIDO
              </div>
              <h2 className="text-4xl sm:text-5xl font-black text-white mb-6 leading-tight">
                Sistema<br />
                <span className="text-rose-400">Antimultas MVE.</span><br />
                <span className="text-white/60 text-3xl font-bold">No te corran. No pagues de más.</span>
              </h2>
              <p className="text-white/50 leading-relaxed mb-8">
                Las multas por pedimentos fuera de plazo, errores en Manifestación de Valor o datos incorrectos pueden superar los <strong className="text-white">$300,000 MXN por evento</strong>. Mystic monitorea tus obligaciones aduanales 24/7 y te avisa antes de que venzan — por Telegram, voz y push notification.
              </p>
              <div className="space-y-4 mb-10">
                {[
                  { icon: AlertTriangle, t: 'Alertas de vencimiento MVE', d: 'Te avisamos 72h, 24h y 1h antes del plazo', c: 'text-rose-400' },
                  { icon: ShieldOff, t: 'Detección de errores en pedimentos', d: 'Revisión automática antes de presentar al SAT', c: 'text-amber-400' },
                  { icon: TrendingDown, t: 'Estrategias para reducir valor en aduana', d: 'Optimización legal de base gravable y aranceles', c: 'text-emerald-400' },
                  { icon: Users, t: 'Formación de clientes en comercio exterior', d: 'Ofrece este servicio a tus clientes y cobra más', c: 'text-sky-400' },
                ].map(({ icon: Icon, t, d, c }) => (
                  <div key={t} className="flex gap-4 items-start">
                    <div className={`w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-0.5`}>
                      <Icon className={`w-5 h-5 ${c}`} />
                    </div>
                    <div>
                      <p className="text-white font-bold text-sm">{t}</p>
                      <p className="text-white/40 text-xs">{d}</p>
                    </div>
                  </div>
                ))}
              </div>
              <Link href="/login" className="inline-flex items-center gap-3 px-8 py-4 bg-rose-600 hover:bg-rose-500 text-white font-black rounded-2xl transition-all hover:shadow-[0_0_30px_rgba(239,68,68,0.3)]">
                <ShieldCheck className="w-5 h-5" /> Activar Antimultas MVE
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="space-y-4">
              {/* Fake alert card */}
              <div className="rounded-2xl border border-rose-500/30 bg-rose-500/5 p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-2 h-2 rounded-full bg-rose-400 animate-pulse" />
                  <span className="text-xs text-rose-300 font-bold uppercase tracking-wider">Alerta activa — vence en 18 horas</span>
                </div>
                <p className="text-white font-bold mb-1">MVE Pedimento #8765432 — Importación maquinaria</p>
                <p className="text-white/50 text-sm">Manifestación de Valor pendiente. Multa potencial: <span className="text-rose-300 font-bold">$180,000 MXN</span></p>
                <div className="mt-4 flex gap-2">
                  <button className="flex-1 py-2 bg-rose-600 text-white text-xs font-bold rounded-lg">Resolver ahora</button>
                  <button className="px-3 py-2 border border-white/15 text-white/60 text-xs rounded-lg">Ver detalles</button>
                </div>
              </div>
              <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs text-emerald-300 font-bold uppercase tracking-wider">Resuelta — hace 2 días</span>
                </div>
                <p className="text-white/70 text-sm">Pedimento #8765288 — Multa evitada: <span className="text-emerald-400 font-black">$240,000 MXN</span></p>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/3 p-5 text-center">
                <p className="text-3xl font-black text-[#D4AF37]">$2.4M MXN</p>
                <p className="text-white/40 text-sm mt-1">en multas evitadas para clientes este trimestre</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── SCORE DE CLIENTE ──────────────────────────────────────────────── */}
      <section className="py-24 bg-[#F5F0E8]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Sistema de Score</p>
            <h2 className="text-4xl font-black text-[#1a1a1a] mb-4">
              Cuanto más usas Mystic,<br />
              <span className="text-[#8B7520]">más te recompensamos.</span>
            </h2>
            <p className="text-[#666] max-w-xl mx-auto">
              Tu score se calcula con señales de comportamiento — sin acceder a datos sensibles. Solo cómo usas la plataforma. Más activo = mejores ofertas, acceso anticipado y recompensas exclusivas.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-12">
            {SCORE_SEGMENTS.map((seg) => (
              <TiltCard key={seg.name}>
                <div className={`rounded-3xl border ${seg.bg} p-6 h-full flex flex-col`}>
                  <div className="flex items-center justify-between mb-4">
                    <span className={`text-lg font-black ${seg.color}`}>{seg.name}</span>
                    <span className="text-xs text-[#888] bg-[#e8e0d0] px-2 py-0.5 rounded-full">{seg.range}</span>
                  </div>
                  {/* Score bar */}
                  <div className="h-2 bg-[#e8e0d0] rounded-full mb-4 overflow-hidden">
                    <div className={`h-full ${seg.bar} rounded-full transition-all`} style={{ width: `${seg.pct}%` }} />
                  </div>
                  <p className="text-xs text-[#666] mb-3 flex-1">{seg.desc}</p>
                  <div className="space-y-1 mb-4">
                    {seg.signal.map(s => (
                      <p key={s} className="text-[10px] text-[#888] flex items-center gap-1">
                        <span className="w-1 h-1 rounded-full bg-[#D4AF37] inline-block" />{s}
                      </p>
                    ))}
                  </div>
                  <div className="text-[11px] bg-[#D4AF37]/15 border border-[#D4AF37]/30 rounded-xl px-3 py-2 text-[#8B7520] font-bold">
                    🎯 {seg.offer}
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
          <div className="rounded-3xl border-2 border-[#D4AF37]/20 bg-white p-8 text-center shadow-sm">
            <p className="text-[#888] text-sm mb-2">Tu score se calcula automáticamente. Sin formularios. Sin encuestas. Solo actúa.</p>
            <p className="text-[#1a1a1a] font-black text-lg">Facturas · Consultas Brain IA · Cursos completados · Referidos activos · Pagos puntuales</p>
            <p className="text-[#D4AF37] text-xs mt-2 font-semibold">Cero datos personales sensibles utilizados en el cálculo</p>
          </div>
        </div>
      </section>

      {/* ── TOKEN $MYS + NFTs ────────────────────────────────────────────── */}
      <section className="py-24 bg-[#0d0d12]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#D4AF37]/70 mb-3">Ecosistema $MYS</p>
            <h2 className="text-4xl font-black text-white mb-4">
              No solo pagas. <span className="text-[#D4AF37]">Ganas.</span><br />
              <span className="text-white/50 text-2xl font-bold">Token de utilidad + NFTs de acceso</span>
            </h2>
            <p className="text-white/40 max-w-xl mx-auto">
              Cada factura emitida, curso completado y referido activo te genera tokens $MYS. Úsalos para acceder a contenido exclusivo, merch, mentorías y NFTs con beneficios reales.
            </p>
          </div>

          {/* Token earn/spend */}
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            <div className="rounded-3xl border border-[#D4AF37]/20 bg-[#D4AF37]/3 p-8">
              <p className="text-[#D4AF37] font-black text-lg mb-5 flex items-center gap-2">
                <Zap className="w-5 h-5" /> Cómo ganar $MYS
              </p>
              <div className="space-y-3">
                {[
                  { a: 'Pagar suscripción mensual', v: '+100 $MYS' },
                  { a: 'Emitir factura CFDI 4.0', v: '+2 $MYS c/u' },
                  { a: 'Completar módulo academia', v: '+25 $MYS' },
                  { a: 'Referir un cliente activo', v: '+200 $MYS' },
                  { a: 'Pagar en BTC/USDC', v: '+50 $MYS bonus' },
                  { a: 'Reseña verificada', v: '+30 $MYS' },
                ].map(({ a, v }) => (
                  <div key={a} className="flex items-center justify-between py-2.5 border-b border-white/5">
                    <span className="text-white/60 text-sm">{a}</span>
                    <span className="text-[#D4AF37] font-black text-sm">{v}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-3xl border border-violet-500/20 bg-violet-500/3 p-8">
              <p className="text-violet-400 font-black text-lg mb-5 flex items-center gap-2">
                <Hexagon className="w-5 h-5" /> Qué puedes hacer con $MYS
              </p>
              <div className="space-y-3">
                {[
                  { a: 'NFT Acceso (badge perfil)', v: '50 $MYS' },
                  { a: 'Hack fiscal exclusivo', v: '80 $MYS' },
                  { a: 'Módulo academia premium', v: '150 $MYS' },
                  { a: 'Kit merch Mystic', v: '300 $MYS' },
                  { a: 'NFT Estratega + beneficios', v: '250 $MYS' },
                  { a: 'Mentoría 1v1 mensual (4 sesiones)', v: '1,000 $MYS' },
                ].map(({ a, v }) => (
                  <div key={a} className="flex items-center justify-between py-2.5 border-b border-white/5">
                    <span className="text-white/60 text-sm">{a}</span>
                    <span className="text-violet-400 font-black text-sm">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* NFT Tiers */}
          <div className="grid sm:grid-cols-3 gap-5">
            {NFT_TIERS.map((nft) => (
              <TiltCard key={nft.tier}>
                <div className={`rounded-3xl border-2 ${nft.border} bg-gradient-to-b ${nft.bg} to-transparent p-7 text-center`}>
                  <div className={`text-5xl ${nft.color} font-black mb-3`}>{nft.symbol}</div>
                  <p className={`text-xl font-black ${nft.color} mb-1`}>NFT {nft.tier}</p>
                  <p className="text-white/30 text-xs mb-5">{nft.price}</p>
                  <ul className="space-y-2.5 text-left">
                    {nft.perks.map(p => (
                      <li key={p} className="flex items-start gap-2 text-xs text-white/60">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        {p}
                      </li>
                    ))}
                  </ul>
                  <button className={`mt-6 w-full py-3 rounded-xl border ${nft.border} ${nft.color} text-sm font-bold hover:bg-white/5 transition-colors`}>
                    Mintear NFT
                  </button>
                </div>
              </TiltCard>
            ))}
          </div>
          <p className="text-center mt-6 text-xs text-white/25">$MYS token en red Polygon · Próximo lanzamiento Q2 2026 · Whitelist abierta</p>
        </div>
      </section>

      {/* ── TESTIMONIALES ─────────────────────────────────────────────────── */}
      <section className="py-24 bg-[#F5F0E8]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <p className="text-sm font-bold uppercase tracking-widest text-[#8B7520] mb-3">Resultados Reales</p>
            <h2 className="text-4xl font-black text-[#1a1a1a] mb-4">
              Ellos ya lo hicieron.<br />
              <span className="text-[#8B7520]">¿Cuándo empiezas tú?</span>
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {TESTIMONIALS.map((t) => (
              <TiltCard key={t.name}>
                <div className="flex flex-col h-full rounded-3xl border border-[#D4AF37]/15 bg-white shadow-sm p-7">
                  <Quote className="w-8 h-8 text-[#D4AF37]/30 mb-4" />
                  <p className="text-[#444] text-sm leading-relaxed flex-1 mb-6 italic">"{t.quote}"</p>
                  <div className="pt-4 border-t border-[#e8e0d0]">
                    <div className="flex items-center gap-1 mb-3">
                      {[...Array(t.stars)].map((_, i) => <Star key={i} className="w-3.5 h-3.5 fill-[#D4AF37] text-[#D4AF37]" />)}
                    </div>
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full ${t.avatarBg} flex items-center justify-center text-white font-black text-xs shrink-0`}>
                        {t.avatar}
                      </div>
                      <div>
                        <p className="text-[#1a1a1a] font-bold text-sm">{t.name}</p>
                        <p className="text-[#888] text-xs">{t.role}</p>
                        <p className="text-[#aaa] text-xs">{t.city}</p>
                      </div>
                      <div className="ml-auto text-right">
                        <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                          t.tier === 'Élite' ? 'bg-violet-100 text-violet-700' :
                          t.tier === 'Estratégico' ? 'bg-amber-100 text-amber-700' :
                          'bg-sky-100 text-sky-700'
                        }`}>{t.tier}</span>
                      </div>
                    </div>
                    <div className="mt-3 rounded-xl bg-emerald-50 border border-emerald-200 px-3 py-2">
                      <p className="text-emerald-700 font-black text-xs">✓ {t.result}</p>
                    </div>
                  </div>
                </div>
              </TiltCard>
            ))}
          </div>
          <p className="text-center mt-8 text-xs text-[#bbb]">
            * Resultados basados en casos de uso reales de la plataforma. Los resultados individuales pueden variar.
          </p>
        </div>
      </section>

      {/* ── CTA FINAL ─────────────────────────────────────────────────────── */}
      <section className="relative py-32 overflow-hidden bg-[#020208]">
        <div className="absolute inset-0 bg-gradient-to-t from-[#D4AF37]/6 to-transparent" />
        <div className="relative max-w-4xl mx-auto px-6 text-center">
          <MysticEyeLogo size={64} />
          <h2 className="mt-8 text-4xl sm:text-6xl font-black text-white mb-6 leading-[1.05]">
            El que no se digitaliza,<br />
            <span className="bg-gradient-to-r from-[#D4AF37] via-[#f0c842] to-[#D4AF37] bg-clip-text text-transparent">
              se queda atrás.
            </span>
          </h2>
          <p className="text-lg text-white/40 leading-relaxed max-w-2xl mx-auto mb-10">
            No necesitas pedir permiso. No necesitas esperar. Empieza gratis hoy y cuando veas los resultados, escala. Eso es lo que hacen los que ganan.
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
            <a href="#quiz" className="inline-flex items-center gap-2 px-10 py-5 border border-white/15 text-white font-bold rounded-2xl hover:bg-white/5 transition-all">
              Hacer el diagnóstico
            </a>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 mt-10 text-xs text-white/25">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> LFPDPPP · Datos en México</span>
            <span className="flex items-center gap-1.5"><Star className="w-3.5 h-3.5 text-[#D4AF37]" /> Sin tarjeta para plan freemium</span>
            <span className="flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-cyan-400" /> Cancela cuando quieras</span>
            <span className="flex items-center gap-1.5"><Lock className="w-3.5 h-3.5 text-violet-400" /> IA local soberana</span>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────── */}
      <footer className="border-t border-[#D4AF37]/15 bg-[#F5F0E8] py-14">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid sm:grid-cols-4 gap-8 mb-10">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <MysticEyeLogo size={32} />
                <div>
                  <p className="font-black text-[#1a1a1a] text-sm">MYSTIC</p>
                  <p className="text-[10px] text-[#8B7520] uppercase tracking-widest">Consulting</p>
                </div>
              </div>
              <p className="text-xs text-[#888] leading-relaxed">
                Ecosistema digital para PYMEs mexicanas. Construido en Hermosillo, Sonora. Para el mundo.
              </p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-[#888] mb-4">Plataforma</p>
              <ul className="space-y-2 text-sm text-[#666]">
                {['Contable IA', 'Content Factory', 'Brain IA', 'Academia', 'Cripto'].map(l => (
                  <li key={l}><a href="#" className="hover:text-[#8B7520] transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-[#888] mb-4">Empresa</p>
              <ul className="space-y-2 text-sm text-[#666]">
                {['Sobre Mystic Consulting', 'Red de Aliados', 'Merch', 'A.C. Impacto Social', 'Blog'].map(l => (
                  <li key={l}><a href="#" className="hover:text-[#8B7520] transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-[#888] mb-4">Contacto</p>
              <ul className="space-y-2 text-sm text-[#666]">
                <li>sonoradigitalcorp@gmail.com</li>
                <li>Hermosillo, Sonora, México</li>
                <li className="pt-2">
                  <Link href="/login" className="text-[#8B7520] font-semibold hover:text-[#D4AF37] transition-colors">Panel de control →</Link>
                </li>
              </ul>
              <div className="mt-4 flex gap-3">
                {['📸', '🎵', '💼', '✈️'].map((e, i) => (
                  <a key={i} href="#" className="w-9 h-9 rounded-xl bg-[#1a1a1a] flex items-center justify-center text-sm hover:bg-[#D4AF37] transition-colors">
                    {e}
                  </a>
                ))}
              </div>
            </div>
          </div>
          <div className="border-t border-[#D4AF37]/15 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#aaa]">
            <p>© 2026 Sonora Digital Corp · Mystic Consulting · Hermosillo, Sonora, México</p>
            <p>LFPDPPP · Aviso de privacidad · Términos · Datos en México</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
