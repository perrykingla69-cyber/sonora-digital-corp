'use client'

import { useEffect, useState, useCallback } from 'react'
import { api } from '@/lib/api'
import {
  Music, Users, Mic2, Trophy, Star, TrendingUp, Play,
  DollarSign, RefreshCw, ChevronRight, GraduationCap,
  Calendar, Zap, ArrowRight, Radio,
} from 'lucide-react'
import Link from 'next/link'

// ── Tipos ─────────────────────────────────────────────────────
interface AbeStats {
  kpis: {
    total_artistas: number
    total_canciones: number
    total_fans: number
    total_contrataciones: number
    contrataciones_confirmadas: number
    ingresos_contrataciones: number
    estudiantes_academy: number
    cursos_completados: number
  }
  top_artistas: { posicion: number; nombre: string; xp: number; nivel: number; rango: string; emoji: string }[]
  artistas_recientes: { nombre: string; genero: string; status: string; desde: string }[]
  concurso_activo: { titulo: string; fecha_fin: string; participantes: number; estado: string }
}

interface AbePerfilData {
  nivel: number
  experiencia: number
  xp_siguiente_nivel: number
  progreso_pct: number
  rango: string
  rango_emoji: string
  stats: { canciones_catalogo: number; fans_totales: number; cursos_completados: number }
}

// ── Helpers ───────────────────────────────────────────────────
const mxn = (v: number) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(v)

const STATUS_LABEL: Record<string, string> = {
  activo: '🟢 Activo',
  pendiente: '🟡 Pendiente',
  inactivo: '⚫ Inactivo',
}

// ── KPI Card ──────────────────────────────────────────────────
function KpiCard({
  label, value, sub, icon: Icon, color,
}: { label: string; value: string; sub: string; icon: React.ElementType; color: string }) {
  return (
    <div className="glass rounded-2xl p-4">
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs text-sovereign-muted">{label}</p>
        <Icon size={16} className={color} />
      </div>
      <p className="text-xl font-bold text-sovereign-text font-display">{value}</p>
      <p className="text-xs text-sovereign-muted mt-0.5">{sub}</p>
    </div>
  )
}

// ── XP Progress Bar ───────────────────────────────────────────
function XpBar({ pct, nivel, rango, emoji }: { pct: number; nivel: number; rango: string; emoji: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-sovereign-text">
          {emoji} {rango} — Nivel {nivel}
        </span>
        <span className="text-sovereign-muted">{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-white/40 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-600 transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────
export default function AbeMusicDashboard({ nombre }: { nombre: string }) {
  const [stats, setStats] = useState<AbeStats | null>(null)
  const [perfil, setPerfil] = useState<AbePerfilData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    try {
      const [s, p] = await Promise.allSettled([
        api.get<AbeStats>('/academy/stats'),
        api.get<AbePerfilData>('/academy/perfil'),
      ])
      if (s.status === 'fulfilled') setStats(s.value)
      if (p.status === 'fulfilled') setPerfil(p.value)
    } catch {}
    setLoading(false)
    setRefreshing(false)
  }, [])

  useEffect(() => { loadData() }, [loadData])

  const hora = new Date().getHours()
  const saludo = hora < 12 ? 'Buenos días' : hora < 19 ? 'Buenas tardes' : 'Buenas noches'

  return (
    <div className="min-h-screen p-4 md:p-6 space-y-6 max-w-7xl mx-auto">

      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-sovereign-text font-display">
            {saludo}, {nombre} 🎵
          </h1>
          <p className="text-sm text-sovereign-muted mt-0.5">
            Panel CEO — ABE Music
          </p>
        </div>
        <button
          onClick={() => loadData(true)}
          className="p-2 rounded-xl glass hover:bg-white/80 transition-colors"
          title="Actualizar"
        >
          <RefreshCw size={16} className={`text-sovereign-muted ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── Mi perfil (XP + rango) ── */}
      {perfil && (
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Star size={16} className="text-amber-500" />
              <p className="font-semibold text-sovereign-text text-sm">Mi Progreso ABE Academy</p>
            </div>
            <Link href="/academy" className="text-xs text-sovereign-muted hover:text-sovereign-gold flex items-center gap-1 transition-colors">
              Ver detalle <ArrowRight size={11} />
            </Link>
          </div>
          <XpBar
            pct={perfil.progreso_pct}
            nivel={perfil.nivel}
            rango={perfil.rango}
            emoji={perfil.rango_emoji}
          />
          <div className="grid grid-cols-3 gap-3 mt-4">
            {[
              { label: 'XP Total',    value: String(perfil.experiencia) },
              { label: 'Canciones',   value: String(perfil.stats.canciones_catalogo) },
              { label: 'Fans',        value: String(perfil.stats.fans_totales) },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-lg font-bold text-sovereign-text font-display">{s.value}</p>
                <p className="text-xs text-sovereign-muted">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── KPIs de la plataforma ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <KpiCard
          label="Artistas registrados"
          value={loading ? '—' : String(stats?.kpis.total_artistas ?? 0)}
          sub="en la plataforma"
          icon={Mic2}
          color="text-purple-600"
        />
        <KpiCard
          label="Canciones en catálogo"
          value={loading ? '—' : String(stats?.kpis.total_canciones ?? 0)}
          sub="tracks registrados"
          icon={Music}
          color="text-amber-600"
        />
        <KpiCard
          label="Fans totales"
          value={loading ? '—' : String(stats?.kpis.total_fans ?? 0)}
          sub="seguidores"
          icon={Users}
          color="text-pink-600"
        />
        <KpiCard
          label="Contrataciones"
          value={loading ? '—' : String(stats?.kpis.total_contrataciones ?? 0)}
          sub={`${stats?.kpis.contrataciones_confirmadas ?? 0} confirmadas`}
          icon={Calendar}
          color="text-green-700"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* ── Leaderboard artistas ── */}
        <div className="lg:col-span-2 glass rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy size={16} className="text-amber-500" />
              <p className="font-semibold text-sovereign-text text-sm">Ranking de Artistas</p>
            </div>
            <Link href="/academy" className="text-xs text-sovereign-muted hover:text-sovereign-gold flex items-center gap-1 transition-colors">
              Ver completo <ChevronRight size={12} />
            </Link>
          </div>

          {loading ? (
            <p className="text-sm text-sovereign-muted">Cargando...</p>
          ) : stats?.top_artistas.length === 0 ? (
            <p className="text-sm text-sovereign-muted">Aún no hay artistas en el ranking.</p>
          ) : (
            <div className="space-y-3">
              {stats?.top_artistas.map((a) => (
                <div key={a.posicion} className="flex items-center gap-4 p-3 rounded-xl bg-white/50 border border-white/80">
                  <span className="text-lg font-bold text-sovereign-muted w-6 text-center">
                    {a.posicion === 1 ? '🥇' : a.posicion === 2 ? '🥈' : '🥉'}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-sovereign-text">{a.nombre}</p>
                    <p className="text-xs text-sovereign-muted">{a.emoji} {a.rango} · Nivel {a.nivel}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-amber-600">{a.xp} XP</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Concurso activo */}
          {stats?.concurso_activo && (
            <div className="p-3 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
              <div className="flex items-center gap-2 mb-1">
                <Radio size={13} className="text-amber-600 animate-pulse" />
                <span className="text-xs font-semibold text-amber-700">Concurso Activo</span>
              </div>
              <p className="text-sm font-semibold text-sovereign-text">{stats.concurso_activo.titulo}</p>
              <p className="text-xs text-sovereign-muted mt-0.5">
                {stats.concurso_activo.participantes} participante{stats.concurso_activo.participantes !== 1 ? 's' : ''} · Termina {stats.concurso_activo.fecha_fin}
              </p>
            </div>
          )}
        </div>

        {/* ── Acciones rápidas ── */}
        <div className="glass rounded-2xl p-5 space-y-3">
          <p className="font-semibold text-sovereign-text text-sm">Acceso rápido</p>
          {[
            { label: 'ABE Academy',         href: '/academy',    icon: GraduationCap, color: 'bg-purple-50 text-purple-700' },
            { label: 'Mis Misiones',         href: '/academy',    icon: Zap,           color: 'bg-amber-50 text-amber-700'   },
            { label: 'Mis Logros',           href: '/academy',    icon: Star,          color: 'bg-yellow-50 text-yellow-700' },
            { label: 'Ranking Artistas',     href: '/academy',    icon: Trophy,        color: 'bg-orange-50 text-orange-700' },
            { label: 'Streams y Regalías',   href: '/directorio', icon: TrendingUp,    color: 'bg-green-50 text-green-700'   },
            { label: 'Ingresos y Contratos', href: '/clientes',   icon: DollarSign,    color: 'bg-blue-50 text-blue-700'     },
          ].map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/60 transition-colors group"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${item.color}`}>
                <item.icon size={15} />
              </div>
              <span className="text-sm text-sovereign-text">{item.label}</span>
              <ChevronRight size={14} className="ml-auto text-sovereign-muted group-hover:text-sovereign-text transition-colors" />
            </Link>
          ))}
        </div>
      </div>

      {/* ── Artistas recientes ── */}
      {stats && stats.artistas_recientes.length > 0 && (
        <div className="glass rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Mic2 size={16} className="text-purple-600" />
              <p className="font-semibold text-sovereign-text text-sm">Artistas en la Plataforma</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {stats.artistas_recientes.map((a) => (
              <div key={a.nombre} className="p-3 rounded-xl bg-white/50 border border-white/80">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-sovereign-text">{a.nombre}</p>
                  <span className="text-xs">{STATUS_LABEL[a.status] ?? a.status}</span>
                </div>
                <p className="text-xs text-sovereign-muted mt-0.5">{a.genero ?? 'Género por definir'}</p>
                <p className="text-xs text-sovereign-muted">Desde {a.desde}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Academy stats ── */}
      <div className="glass rounded-2xl p-5 space-y-3">
        <div className="flex items-center gap-2">
          <GraduationCap size={16} className="text-purple-600" />
          <p className="font-semibold text-sovereign-text text-sm">ABE Academy — Resumen</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'Ingresos contratos', value: loading ? '—' : mxn(stats?.kpis.ingresos_contrataciones ?? 0), icon: DollarSign, color: 'text-green-700' },
            { label: 'Estudiantes',         value: loading ? '—' : String(stats?.kpis.estudiantes_academy ?? 0),  icon: Users,      color: 'text-blue-600'  },
            { label: 'Cursos completados',  value: loading ? '—' : String(stats?.kpis.cursos_completados ?? 0),   icon: Play,       color: 'text-amber-600' },
            { label: 'Contratos activos',   value: loading ? '—' : String(stats?.kpis.contrataciones_confirmadas ?? 0), icon: Calendar, color: 'text-purple-600' },
          ].map((item) => (
            <div key={item.label} className="p-3 rounded-xl bg-white/50 border border-white/80 flex items-center gap-3">
              <item.icon size={20} className={item.color} />
              <div>
                <p className="text-lg font-bold text-sovereign-text font-display">{item.value}</p>
                <p className="text-xs text-sovereign-muted">{item.label}</p>
              </div>
            </div>
          ))}
        </div>
        <Link href="/academy" className="inline-flex items-center gap-1 text-xs text-sovereign-gold hover:text-amber-600 transition-colors mt-1">
          Ir a ABE Academy completa <ArrowRight size={12} />
        </Link>
      </div>

    </div>
  )
}
