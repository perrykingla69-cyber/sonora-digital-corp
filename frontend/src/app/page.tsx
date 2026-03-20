import Link from 'next/link'
import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Gauge,
  Lock,
  PanelsTopLeft,
  Sparkles,
  Workflow,
} from 'lucide-react'

const pillars = [
  {
    title: 'Operación unificada',
    description:
      'Contabilidad, automatización y seguimiento operativo desde una sola superficie visual.',
    icon: PanelsTopLeft,
  },
  {
    title: 'IA contextual',
    description:
      'Flujos guiados por agentes y memoria operativa para priorizar tareas sin perder contexto.',
    icon: BrainCircuit,
  },
  {
    title: 'Rendimiento soberano',
    description:
      'Arquitectura lista para despliegues propios, monitoreo continuo y control total del entorno.',
    icon: Lock,
  },
]

const metrics = [
  { label: 'Módulos activos', value: '12+' },
  { label: 'Disponibilidad objetivo', value: '99.9%' },
  { label: 'Tiempo de reacción', value: '< 5 min' },
]

const highlights = [
  'Dashboard responsivo con jerarquía clara para escritorio, tablet y móvil.',
  'Bloques listos para facturación, nómina, mensajería y automatizaciones.',
  'Llamadas a la acción directas para acceso al workspace y despliegue operativo.',
]

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.16),_transparent_28%),radial-gradient(circle_at_80%_20%,_rgba(14,165,233,0.18),_transparent_24%),linear-gradient(180deg,_rgba(15,23,42,0.96),_rgba(2,6,23,1))]" />
        <div className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-6 py-10 sm:px-8 lg:px-12">
          <header className="flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.28em] text-amber-300">Nano Banana Pro</p>
              <h1 className="mt-2 text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                Mystic · Sonora Digital Corp
              </h1>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/login"
                className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-5 py-2.5 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/10"
              >
                Entrar al sistema
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center rounded-full bg-amber-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-amber-300"
              >
                Ver workspace
              </Link>
            </div>
          </header>

          <div className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.2fr_0.8fr] lg:py-16">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
                <Sparkles className="h-4 w-4" />
                Interfaz responsiva v3.3.6
              </div>

              <div className="space-y-5">
                <h2 className="max-w-4xl text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
                  Centro operativo para finanzas, automatización y control soberano.
                </h2>
                <p className="max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
                  Una portada editorial de alto contraste para presentar el ecosistema Mystic con enfoque
                  premium, navegación directa y lectura fluida en cualquier tamaño de pantalla.
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {metrics.map(metric => (
                  <div key={metric.label} className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                    <p className="text-3xl font-semibold text-white">{metric.value}</p>
                    <p className="mt-2 text-sm text-slate-300">{metric.label}</p>
                  </div>
                ))}
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
                >
                  Abrir panel principal
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-white/15 px-6 py-3 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/5"
                >
                  Acceso seguro
                  <Lock className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="grid gap-4">
              <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur">
                <div className="flex items-center justify-between border-b border-white/10 pb-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Command view</p>
                    <h3 className="mt-2 text-xl font-semibold text-white">Estado de despliegue</h3>
                  </div>
                  <Gauge className="h-6 w-6 text-amber-300" />
                </div>
                <div className="mt-5 space-y-4">
                  {highlights.map(item => (
                    <div key={item} className="flex gap-3 rounded-2xl border border-white/8 bg-slate-900/60 p-4">
                      <CheckCircle2 className="mt-0.5 h-5 w-5 flex-none text-emerald-300" />
                      <p className="text-sm leading-6 text-slate-200">{item}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
                {pillars.map(({ title, description, icon: Icon }) => (
                  <article key={title} className="rounded-[1.75rem] border border-white/10 bg-slate-900/70 p-5">
                    <Icon className="h-8 w-8 text-cyan-300" />
                    <h4 className="mt-4 text-lg font-semibold text-white">{title}</h4>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>

          <footer className="grid gap-4 border-t border-white/10 pt-6 text-sm text-slate-400 sm:grid-cols-[1fr_auto] sm:items-center">
            <p>Protocolo de soberanía visual: contraste alto, ritmo editorial y CTAs listos para operar.</p>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-slate-200">
              <Workflow className="h-4 w-4 text-cyan-300" />
              Nano Banana Pro v3.3.6
            </div>
          </footer>
        </div>
      </section>
    </main>
  )
}
