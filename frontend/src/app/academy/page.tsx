'use client'

import { useEffect, useState } from 'react'
import {
  Trophy, Star, Zap, Flame, Target, CheckCircle2,
  Lock, TrendingUp, Award, Users, ChevronRight
} from 'lucide-react'
import clsx from 'clsx'

// ── Types ─────────────────────────────────────────────────────────────────────
interface Perfil {
  nombre: string
  nivel: number
  experiencia: number
  xp_siguiente_nivel: number
  progreso_pct: number
  rango: string
  rango_emoji: string
  streak_dias: number
  misiones_activas: number
  logros_desbloqueados: number
  stats: Record<string, number>
}

interface Mision {
  id: string
  titulo: string
  descripcion: string
  tipo: string
  xp_reward: number
  progreso: number
  objetivo: number
  progreso_pct: number
  completada: boolean
}

interface Logro {
  id: string
  nombre: string
  emoji: string
  xp_reward: number
  desbloqueado: boolean
}

interface LeaderEntry {
  posicion: number
  user_id: string
  nivel: number
  experiencia: number
  rango: string
  emoji: string
  streak: number
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function apiFetch(path: string, opts?: RequestInit) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : ''
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...opts?.headers },
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

const tipoColor: Record<string, string> = {
  diaria: 'text-sovereign-gold border-sovereign-gold/30 bg-sovereign-gold/10',
  semanal: 'text-blue-400 border-blue-400/30 bg-blue-400/10',
  especial: 'text-purple-400 border-purple-400/30 bg-purple-400/10',
}

// ── Componentes ───────────────────────────────────────────────────────────────

function XPBar({ pct }: { pct: number }) {
  return (
    <div className="w-full h-2 bg-sovereign-border rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-sovereign-gold to-yellow-300 rounded-full transition-all duration-700"
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function StatBadge({ label, value, icon }: { label: string; value: number; icon: string }) {
  return (
    <div className="flex flex-col items-center gap-1 p-3 bg-sovereign-card rounded-xl border border-sovereign-border">
      <span className="text-xl">{icon}</span>
      <span className="text-sovereign-gold font-bold text-lg">{value}</span>
      <span className="text-sovereign-muted text-xs">{label}</span>
    </div>
  )
}

function MisionCard({ mision, onCompletar }: { mision: Mision; onCompletar: (id: string) => void }) {
  return (
    <div className={clsx(
      'glass rounded-xl p-4 border transition-all',
      mision.completada ? 'opacity-50 border-sovereign-border' : 'border-sovereign-border hover:border-sovereign-gold/40'
    )}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={clsx(
              'text-xs px-2 py-0.5 rounded-full border capitalize',
              tipoColor[mision.tipo] ?? tipoColor.diaria
            )}>
              {mision.tipo}
            </span>
            <span className="text-sovereign-gold text-xs font-mono">+{mision.xp_reward} XP</span>
          </div>
          <p className="text-sovereign-text font-medium text-sm">{mision.titulo}</p>
          <p className="text-sovereign-muted text-xs mt-0.5">{mision.descripcion}</p>
        </div>
        {mision.completada ? (
          <CheckCircle2 size={20} className="text-green-400 shrink-0 mt-0.5" />
        ) : (
          <button
            onClick={() => onCompletar(mision.id)}
            className="shrink-0 px-3 py-1.5 bg-sovereign-gold/10 hover:bg-sovereign-gold/20 border border-sovereign-gold/30 text-sovereign-gold text-xs rounded-lg transition-colors"
          >
            Completar
          </button>
        )}
      </div>
      {!mision.completada && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-sovereign-muted mb-1">
            <span>Progreso</span>
            <span>{mision.progreso}/{mision.objetivo}</span>
          </div>
          <XPBar pct={mision.progreso_pct} />
        </div>
      )}
    </div>
  )
}

// ── Página Principal ──────────────────────────────────────────────────────────
export default function AcademyPage() {
  const [perfil, setPerfil]       = useState<Perfil | null>(null)
  const [misiones, setMisiones]   = useState<Mision[]>([])
  const [logros, setLogros]       = useState<Logro[]>([])
  const [ranking, setRanking]     = useState<LeaderEntry[]>([])
  const [tab, setTab]             = useState<'misiones' | 'logros' | 'ranking'>('misiones')
  const [loading, setLoading]     = useState(true)
  const [toast, setToast]         = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      apiFetch('/academy/perfil'),
      apiFetch('/academy/misiones'),
      apiFetch('/academy/logros'),
      apiFetch('/academy/leaderboard'),
    ]).then(([p, m, l, r]) => {
      setPerfil(p); setMisiones(m); setLogros(l); setRanking(r)
    }).catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const completarMision = async (id: string) => {
    try {
      const res = await apiFetch(`/academy/misiones/${id}/completar`, { method: 'POST' })
      setMisiones(prev => prev.map(m => m.id === id ? { ...m, completada: true } : m))
      setPerfil(prev => prev ? { ...prev, experiencia: res.experiencia, nivel: res.nivel_actual, rango: res.rango } : prev)
      showToast(`+${res.xp_ganada} XP — ¡Misión completada!`)
    } catch {
      showToast('Error al completar misión')
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-sovereign-gold border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (!perfil) return (
    <div className="p-8 text-sovereign-muted text-center">No se pudo cargar tu perfil de Academy.</div>
  )

  const misionesActivas = misiones.filter(m => !m.completada)
  const misionesCompletadas = misiones.filter(m => m.completada)

  return (
    <div className="min-h-screen bg-sovereign-bg p-4 md:p-8 space-y-6 animate-fade-up">

      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 glass-gold border border-sovereign-gold/40 text-sovereign-gold px-4 py-3 rounded-xl text-sm animate-fade-up">
          {toast}
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-sovereign-text">Mystic Academy</h1>
        <p className="text-sovereign-muted text-sm mt-1">Gamificación — tu progreso como usuario Mystic</p>
      </div>

      {/* Perfil Card */}
      <div className="glass rounded-2xl p-6 border border-sovereign-border">
        <div className="flex flex-col md:flex-row md:items-center gap-6">
          {/* Avatar / Rango */}
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-sovereign-gold/10 border border-sovereign-gold/30 flex items-center justify-center text-4xl">
              {perfil.rango_emoji}
            </div>
            <div>
              <p className="text-sovereign-text font-bold text-lg">{perfil.nombre}</p>
              <p className="text-sovereign-gold text-sm">{perfil.rango_emoji} {perfil.rango}</p>
              <p className="text-sovereign-muted text-xs">Nivel {perfil.nivel}</p>
            </div>
          </div>

          {/* XP Bar */}
          <div className="flex-1">
            <div className="flex justify-between text-xs text-sovereign-muted mb-2">
              <span>Experiencia</span>
              <span className="text-sovereign-gold font-mono">{perfil.experiencia} / {perfil.xp_siguiente_nivel} XP</span>
            </div>
            <XPBar pct={perfil.progreso_pct} />
            <p className="text-sovereign-muted text-xs mt-1">{perfil.progreso_pct.toFixed(1)}% al siguiente nivel</p>
          </div>

          {/* Quick Stats */}
          <div className="flex gap-3">
            <div className="text-center p-3 bg-sovereign-card rounded-xl border border-sovereign-border">
              <Flame size={16} className="text-orange-400 mx-auto mb-1" />
              <p className="text-sovereign-text font-bold">{perfil.streak_dias}</p>
              <p className="text-sovereign-muted text-xs">Racha</p>
            </div>
            <div className="text-center p-3 bg-sovereign-card rounded-xl border border-sovereign-border">
              <Target size={16} className="text-sovereign-gold mx-auto mb-1" />
              <p className="text-sovereign-text font-bold">{perfil.misiones_activas}</p>
              <p className="text-sovereign-muted text-xs">Misiones</p>
            </div>
            <div className="text-center p-3 bg-sovereign-card rounded-xl border border-sovereign-border">
              <Trophy size={16} className="text-yellow-400 mx-auto mb-1" />
              <p className="text-sovereign-text font-bold">{perfil.logros_desbloqueados}</p>
              <p className="text-sovereign-muted text-xs">Logros</p>
            </div>
          </div>
        </div>

        {/* Stats RPG */}
        <div className="mt-6 grid grid-cols-5 gap-2">
          {Object.entries(perfil.stats).map(([k, v]) => (
            <StatBadge key={k} label={k.slice(0,4).toUpperCase()} value={v} icon={
              k === 'inteligencia' ? '🧠' : k === 'creatividad' ? '🎨' :
              k === 'colaboracion' ? '🤝' : k === 'resiliencia' ? '🛡️' : '⚡'
            } />
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {(['misiones', 'logros', 'ranking'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              'px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors',
              tab === t
                ? 'bg-sovereign-gold text-sovereign-bg'
                : 'bg-sovereign-card text-sovereign-muted hover:text-sovereign-text border border-sovereign-border'
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab: Misiones */}
      {tab === 'misiones' && (
        <div className="space-y-4">
          {misionesActivas.length > 0 && (
            <div>
              <h3 className="text-sovereign-text font-semibold mb-3 flex items-center gap-2">
                <Zap size={16} className="text-sovereign-gold" /> Activas ({misionesActivas.length})
              </h3>
              <div className="space-y-3">
                {misionesActivas.map(m => (
                  <MisionCard key={m.id} mision={m} onCompletar={completarMision} />
                ))}
              </div>
            </div>
          )}
          {misionesCompletadas.length > 0 && (
            <div>
              <h3 className="text-sovereign-muted font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 size={16} /> Completadas ({misionesCompletadas.length})
              </h3>
              <div className="space-y-3">
                {misionesCompletadas.map(m => (
                  <MisionCard key={m.id} mision={m} onCompletar={completarMision} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Logros */}
      {tab === 'logros' && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {logros.map(l => (
            <div key={l.id} className={clsx(
              'glass rounded-xl p-4 border text-center transition-all',
              l.desbloqueado
                ? 'border-sovereign-gold/40 bg-sovereign-gold/5'
                : 'border-sovereign-border opacity-50 grayscale'
            )}>
              <div className="text-3xl mb-2">{l.desbloqueado ? l.emoji : '🔒'}</div>
              <p className="text-sovereign-text text-xs font-medium">{l.nombre}</p>
              <p className="text-sovereign-gold text-xs mt-1">+{l.xp_reward} XP</p>
            </div>
          ))}
        </div>
      )}

      {/* Tab: Ranking */}
      {tab === 'ranking' && (
        <div className="glass rounded-2xl border border-sovereign-border overflow-hidden">
          <div className="p-4 border-b border-sovereign-border">
            <h3 className="text-sovereign-text font-semibold flex items-center gap-2">
              <Users size={16} className="text-sovereign-gold" /> Leaderboard Top 10
            </h3>
          </div>
          <div className="divide-y divide-sovereign-border">
            {ranking.map(r => (
              <div key={r.user_id} className="flex items-center gap-4 px-4 py-3 hover:bg-sovereign-surface/50 transition-colors">
                <span className={clsx(
                  'w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold',
                  r.posicion === 1 ? 'bg-yellow-400/20 text-yellow-400' :
                  r.posicion === 2 ? 'bg-gray-400/20 text-gray-400' :
                  r.posicion === 3 ? 'bg-amber-700/20 text-amber-600' :
                  'text-sovereign-muted'
                )}>
                  {r.posicion}
                </span>
                <span className="text-xl">{r.emoji}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sovereign-text text-sm font-medium truncate">{r.user_id}</p>
                  <p className="text-sovereign-muted text-xs">{r.rango} · Nivel {r.nivel}</p>
                </div>
                <div className="text-right">
                  <p className="text-sovereign-gold text-sm font-mono">{r.experiencia.toLocaleString()} XP</p>
                  {r.streak > 0 && <p className="text-orange-400 text-xs">🔥 {r.streak}d</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
