import Link from 'next/link'
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  FileText,
  Lock,
  MessageCircle,
  Sparkles,
  Workflow,
  Zap,
} from 'lucide-react'
import { Countdown } from './countdown'

const products = [
  {
    badge: 'En vivo',
    badgeColor: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/20',
    icon: FileText,
    iconColor: 'text-amber-300',
    title: 'Mystic Contable',
    description:
      '147 cálculos SAT automatizados. CFDI 4.0, IVA, ISR, IMSS y multi-RFC desde un solo panel.',
  },
  {
    badge: 'En vivo',
    badgeColor: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/20',
    icon: BrainCircuit,
    iconColor: 'text-cyan-300',
    title: 'Mystic Brain',
    description:
      'IA entrenada con tus datos. Responde preguntas fiscales, genera reportes y aprende de tu operación. Sin costo por consulta.',
  },
  {
    badge: 'En vivo',
    badgeColor: 'bg-emerald-400/15 text-emerald-300 border-emerald-400/20',
    icon: Workflow,
    iconColor: 'text-violet-300',
    title: 'Mystic Automator',
    description:
      '+400 integraciones. Automatiza procesos repetitivos con workflows drag & drop sin escribir código.',
  },
  {
    badge: 'Beta',
    badgeColor: 'bg-amber-400/15 text-amber-300 border-amber-400/20',
    icon: MessageCircle,
    iconColor: 'text-sky-300',
    title: 'Mystic Bot',
    description:
      'Tu contador responde por WhatsApp y Telegram. Consultas en lenguaje natural, 24/7, sin abrir el sistema.',
  },
]

const metrics = [
  { value: '147', label: 'Cálculos fiscales SAT' },
  { value: '90%', label: 'Open source' },
  { value: '24/7', label: 'Disponibilidad' },
  { value: '$0', label: 'Por consulta IA' },
]

const plans = [
  {
    name: 'Starter',
    price: '$0',
    period: '/mes',
    highlight: false,
    description: 'Para conocer Mystic sin riesgo.',
    features: ['50 facturas/mes', '1 usuario', 'IA local incluida', 'Soporte comunidad'],
    cta: 'Empezar gratis',
    href: '/login',
  },
  {
    name: 'Pro',
    price: '$1,499',
    period: '/mes',
    highlight: true,
    description: 'Para el contador que ya quiere escalar.',
    features: ['Facturas ilimitadas', '5 usuarios', 'IA avanzada', 'Soporte prioritario'],
    cta: 'Empezar Pro',
    href: '/login',
  },
  {
    name: 'Empresarial',
    price: '$3,999',
    period: '/mes',
    highlight: false,
    description: 'Para despachos y empresas en crecimiento.',
    features: ['Todo ilimitado', 'Servidor dedicado', 'Onboarding personal', 'SLA 99.9%'],
    cta: 'Contactar ventas',
    href: '/login',
  },
]

const painPoints = [
  'Capturas lo mismo 10 veces al día en sistemas distintos',
  'El SAT cambia reglas y te enteras tarde',
  'Tus clientes llaman a cualquier hora y no tienes respuesta inmediata',
  'La carrera de 4 años no te enseñó a conseguir clientes',
]

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* NAV */}
      <header className="sticky top-0 z-50 border-b border-white/8 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 sm:px-8">
          <div>
            <span className="text-xs font-medium uppercase tracking-[0.28em] text-amber-300">
              Sonora Digital Corp
            </span>
            <h1 className="text-lg font-semibold text-white">Mystic</h1>
          </div>
          <div className="flex gap-3">
            <Link
              href="/login"
              className="rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/10"
            >
              Entrar
            </Link>
            <Link
              href="/login"
              className="rounded-full bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-300"
            >
              Registrarme
            </Link>
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.14),_transparent_30%),radial-gradient(circle_at_80%_20%,_rgba(14,165,233,0.12),_transparent_25%)]" />
        <div className="relative mx-auto max-w-5xl px-6 py-24 text-center sm:px-8 sm:py-32">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
            <Sparkles className="h-4 w-4" />
            Lanzamiento oficial — 1 de Abril 2026
          </div>

          <h2 className="mx-auto max-w-4xl text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
            La IA que trabaja por ti.<br />
            <span className="text-amber-300">Deja de ser esclavo de tu trabajo.</span>
          </h2>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
            Mystic automatiza tu contabilidad, facturación y comunicación con clientes.
            Corre en tu servidor. Sin intermediarios. Sin letra chica.
          </p>

          <div className="mt-10 flex flex-col items-center gap-6">
            <div className="flex items-center gap-3 text-sm text-slate-400">
              <span>Faltan</span>
              <Countdown />
              <span>para el lanzamiento</span>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-full bg-amber-400 px-7 py-3.5 text-sm font-bold text-slate-950 transition hover:bg-amber-300"
              >
                Quiero acceso anticipado
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-full border border-white/15 px-7 py-3.5 text-sm font-medium text-white transition hover:bg-white/5"
              >
                Ver panel demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* MÉTRICAS */}
      <section className="border-y border-white/8 bg-white/2">
        <div className="mx-auto grid max-w-4xl grid-cols-2 divide-x divide-y divide-white/8 sm:grid-cols-4 sm:divide-y-0">
          {metrics.map(m => (
            <div key={m.label} className="p-8 text-center">
              <p className="text-3xl font-bold text-white">{m.value}</p>
              <p className="mt-1 text-sm text-slate-400">{m.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* DOLOR — COPY EMOCIONAL */}
      <section className="mx-auto max-w-5xl px-6 py-20 sm:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-amber-300">¿Te identificas?</p>
            <h3 className="mt-4 text-3xl font-bold text-white leading-snug sm:text-4xl">
              4 años de carrera y sigues haciendo trabajo manual.
            </h3>
            <p className="mt-4 text-slate-300 leading-7">
              Los contadores más exitosos de México ya no compiten con horas — compiten con sistemas.
              Mystic te da ese sistema.
            </p>
          </div>
          <ul className="space-y-4">
            {painPoints.map(p => (
              <li key={p} className="flex gap-3 rounded-2xl border border-red-500/15 bg-red-500/5 p-4">
                <span className="mt-0.5 text-red-400">✕</span>
                <p className="text-sm leading-6 text-slate-200">{p}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* PRODUCTOS */}
      <section className="mx-auto max-w-7xl px-6 py-12 sm:px-8">
        <div className="mb-12 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-cyan-300">Plataforma completa</p>
          <h3 className="mt-3 text-3xl font-bold text-white sm:text-4xl">Todo lo que necesitas, en uno.</h3>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
          {products.map(({ badge, badgeColor, icon: Icon, iconColor, title, description }) => (
            <article
              key={title}
              className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-slate-900/70 p-6"
            >
              <div className="flex items-start justify-between">
                <Icon className={`h-8 w-8 ${iconColor}`} />
                <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${badgeColor}`}>
                  {badge}
                </span>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white">{title}</h4>
                <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ESCUELA CONTABLE */}
      <section className="mx-auto max-w-5xl px-6 py-16 sm:px-8">
        <div className="rounded-3xl border border-violet-400/20 bg-violet-400/5 p-8 sm:p-10">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <BookOpen className="mt-1 h-8 w-8 flex-none text-violet-300" />
              <div>
                <p className="text-xs font-medium uppercase tracking-widest text-violet-300">Próximamente</p>
                <h3 className="mt-1 text-2xl font-bold text-white">Escuela Contable Inteligente</h3>
                <p className="mt-2 max-w-xl text-sm leading-6 text-slate-300">
                  Cursos, certificaciones y rutas de aprendizaje guiadas por IA.
                  Aprende, practica y gana — con el sistema que ya usas para trabajar.
                </p>
              </div>
            </div>
            <div className="flex-none">
              <span className="rounded-2xl border border-violet-400/30 bg-violet-400/10 px-4 py-2 text-sm font-medium text-violet-200">
                Play · Learn · Earn
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* PRECIOS */}
      <section className="mx-auto max-w-5xl px-6 py-12 sm:px-8">
        <div className="mb-12 text-center">
          <p className="text-sm font-medium uppercase tracking-widest text-amber-300">Precios claros</p>
          <h3 className="mt-3 text-3xl font-bold text-white sm:text-4xl">Sin letra chica. Sin sorpresas.</h3>
          <p className="mt-3 text-slate-400">Paga con SPEI, USDC o BTC.</p>
        </div>
        <div className="grid gap-6 sm:grid-cols-3">
          {plans.map(plan => (
            <div
              key={plan.name}
              className={`flex flex-col rounded-3xl border p-7 ${
                plan.highlight
                  ? 'border-amber-400/40 bg-amber-400/8 ring-1 ring-amber-400/20'
                  : 'border-white/10 bg-slate-900/60'
              }`}
            >
              {plan.highlight && (
                <span className="mb-4 self-start rounded-full bg-amber-400 px-3 py-0.5 text-xs font-bold text-slate-950">
                  Más popular
                </span>
              )}
              <p className="text-sm font-medium text-slate-400">{plan.name}</p>
              <div className="mt-2 flex items-end gap-1">
                <span className="text-4xl font-bold text-white">{plan.price}</span>
                <span className="mb-1 text-slate-400">{plan.period}</span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{plan.description}</p>
              <ul className="mt-6 flex-1 space-y-3">
                {plan.features.map(f => (
                  <li key={f} className="flex items-center gap-2 text-sm text-slate-200">
                    <CheckCircle2 className="h-4 w-4 flex-none text-emerald-400" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href={plan.href}
                className={`mt-8 rounded-full py-3 text-center text-sm font-semibold transition ${
                  plan.highlight
                    ? 'bg-amber-400 text-slate-950 hover:bg-amber-300'
                    : 'border border-white/15 text-white hover:bg-white/5'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ROI BANNER */}
      <section className="mx-auto max-w-5xl px-6 py-8 sm:px-8">
        <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/5 p-8 text-center">
          <Zap className="mx-auto h-8 w-8 text-cyan-300" />
          <h3 className="mt-4 text-2xl font-bold text-white">
            5 hrs/día × 22 días × $200 MXN/hr
          </h3>
          <p className="mt-2 text-3xl font-bold text-cyan-300">= $110,000 MXN ahorrados al mes</p>
          <p className="mt-3 text-slate-400 text-sm">
            Costo de implementación: $3,000–$8,000 MXN (una sola vez)
          </p>
        </div>
      </section>

      {/* CTA FINAL */}
      <section className="mx-auto max-w-3xl px-6 py-24 text-center sm:px-8">
        <h3 className="text-3xl font-bold text-white sm:text-4xl">
          Sé de los primeros.<br />
          <span className="text-amber-300">El 1 de Abril cambia todo.</span>
        </h3>
        <p className="mt-4 text-slate-300 leading-7">
          Imagina cobrar por resultados, no por horas. Con Mystic, tus clientes te llaman
          para crecer — no para apagar incendios.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-full bg-amber-400 px-8 py-4 text-sm font-bold text-slate-950 transition hover:bg-amber-300"
          >
            Quiero acceso anticipado
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <p className="mt-4 text-xs text-slate-500">
          Plan Starter gratis · Sin tarjeta de crédito · Cancela cuando quieras
        </p>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/8 py-8">
        <div className="mx-auto flex max-w-7xl flex-col items-center gap-3 px-6 text-center text-sm text-slate-500 sm:flex-row sm:justify-between sm:text-left">
          <p>© 2026 Sonora Digital Corp · Hermosillo, Sonora, México</p>
          <div className="flex gap-4">
            <span>sonoradigitalcorp@gmail.com</span>
            <span>·</span>
            <span className="text-slate-600">LFPDPPP · Datos en México</span>
          </div>
        </div>
      </footer>
    </main>
  )
}
