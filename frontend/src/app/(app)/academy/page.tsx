'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Trophy, Zap, Flame, Target, CheckCircle2, BookOpen,
  Users, Play, FileText, HelpCircle, Layers, Lock,
  ChevronRight, Star, TrendingUp, GraduationCap, Clock, Swords
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '@/lib/api'

// ── Types ─────────────────────────────────────────────────────────────────────
interface Perfil {
  nombre: string; nivel: number; experiencia: number
  xp_siguiente_nivel: number; progreso_pct: number
  rango: string; rango_emoji: string; streak_dias: number
  misiones_activas: number; logros_desbloqueados: number; total_logros: number
  stats: Record<string, number>
}
interface Curso {
  id: string; slug: string; titulo: string; descripcion: string
  categoria: string; nivel_req: number; xp_total: number
  duracion_min: number; icono: string; desbloqueado: boolean
  progreso_pct: number; clases_completadas: number; total_clases: number
}
interface Mision {
  id: string; titulo: string; descripcion: string; tipo: string
  xp_reward: number; progreso: number; objetivo: number
  progreso_pct: number; completada: boolean
}
interface Logro {
  id: string; nombre: string; emoji: string; xp_reward: number; desbloqueado: boolean
}
interface LeaderEntry {
  posicion: number; user_id: string; nivel: number
  experiencia: number; rango: string; emoji: string; streak: number
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const tipoIcon: Record<string, any> = {
  video: Play, lectura: FileText, ejercicio: Target,
  quiz: HelpCircle, hibrido: Layers
}
const tipoColor: Record<string, string> = {
  diaria:  'text-sovereign-gold border-sovereign-gold/30 bg-sovereign-gold/10',
  semanal: 'text-blue-400 border-blue-400/30 bg-blue-400/10',
  especial:'text-purple-400 border-purple-400/30 bg-purple-400/10',
}
const catColor: Record<string, string> = {
  contabilidad: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  fiscal:       'bg-amber-500/10 text-amber-400 border-amber-500/20',
  tecnologia:   'bg-purple-500/10 text-purple-400 border-purple-500/20',
  soft_skills:  'bg-green-500/10 text-green-400 border-green-500/20',
}

function XPBar({ pct, className }: { pct: number; className?: string }) {
  return (
    <div className={clsx('w-full h-2 bg-[#222] rounded-full overflow-hidden', className)}>
      <div className="h-full bg-gradient-to-r from-[#D4AF37] to-yellow-300 rounded-full transition-all duration-700"
           style={{ width: `${pct}%` }} />
    </div>
  )
}

function Toast({ msg }: { msg: string }) {
  return (
    <div className="fixed top-4 right-4 z-50 bg-[#161616] border border-[#D4AF37]/40
                    text-[#D4AF37] px-4 py-3 rounded-xl text-sm shadow-lg animate-fade-up">
      {msg}
    </div>
  )
}

// ── Sub-páginas ───────────────────────────────────────────────────────────────
function CursosView({ cursos, onSelect }: { cursos: Curso[]; onSelect: (slug: string) => void }) {
  return (
    <div className="space-y-4">
      <h2 className="text-[#E8E8E8] font-semibold text-lg flex items-center gap-2">
        <BookOpen size={18} className="text-[#D4AF37]" /> Cursos disponibles
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {cursos.map(c => (
          <div key={c.id}
            onClick={() => c.desbloqueado && onSelect(c.slug)}
            className={clsx(
              'bg-[#161616] border rounded-2xl p-5 transition-all',
              c.desbloqueado
                ? 'border-[#222] hover:border-[#D4AF37]/40 cursor-pointer'
                : 'border-[#222] opacity-60 cursor-not-allowed'
            )}>
            <div className="flex items-start justify-between gap-3 mb-3">
              <span className="text-3xl">{c.icono}</span>
              <div className="flex flex-col items-end gap-1">
                <span className={clsx('text-xs px-2 py-0.5 rounded-full border capitalize',
                  catColor[c.categoria] ?? catColor.contabilidad)}>
                  {c.categoria.replace('_',' ')}
                </span>
                {!c.desbloqueado && (
                  <span className="flex items-center gap-1 text-xs text-[#666]">
                    <Lock size={10}/> Nivel {c.nivel_req}
                  </span>
                )}
              </div>
            </div>
            <h3 className="text-[#E8E8E8] font-semibold text-sm mb-1">{c.titulo}</h3>
            <p className="text-[#666] text-xs mb-3 line-clamp-2">{c.descripcion}</p>
            <div className="flex items-center gap-3 text-xs text-[#666] mb-3">
              <span className="flex items-center gap-1"><Clock size={10}/> {c.duracion_min}min</span>
              <span className="flex items-center gap-1"><Zap size={10} className="text-[#D4AF37]"/> {c.xp_total} XP</span>
              <span>{c.clases_completadas}/{c.total_clases} clases</span>
            </div>
            {c.progreso_pct > 0 && (
              <>
                <XPBar pct={c.progreso_pct} />
                <p className="text-[#666] text-xs mt-1">{c.progreso_pct}% completado</p>
              </>
            )}
            {c.desbloqueado && c.progreso_pct === 0 && (
              <div className="mt-2 flex items-center gap-1 text-[#D4AF37] text-xs font-medium">
                Comenzar <ChevronRight size={12}/>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function MisionesView({ misiones, onCompletar }: { misiones: Mision[]; onCompletar: (id: string) => void }) {
  const activas = misiones.filter(m => !m.completada)
  const hechas  = misiones.filter(m => m.completada)
  return (
    <div className="space-y-6">
      {activas.length > 0 && (
        <div>
          <h3 className="text-[#E8E8E8] font-semibold mb-3 flex items-center gap-2">
            <Zap size={16} className="text-[#D4AF37]"/> Activas ({activas.length})
          </h3>
          <div className="space-y-3">
            {activas.map(m => (
              <div key={m.id} className="bg-[#161616] border border-[#222] rounded-xl p-4
                                         hover:border-[#D4AF37]/30 transition-colors">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={clsx('text-xs px-2 py-0.5 rounded-full border capitalize',
                        tipoColor[m.tipo] ?? tipoColor.diaria)}>{m.tipo}</span>
                      <span className="text-[#D4AF37] text-xs font-mono">+{m.xp_reward} XP</span>
                    </div>
                    <p className="text-[#E8E8E8] font-medium text-sm">{m.titulo}</p>
                    <p className="text-[#666] text-xs mt-0.5">{m.descripcion}</p>
                  </div>
                  <button onClick={() => onCompletar(m.id)}
                    className="shrink-0 px-3 py-1.5 bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20
                               border border-[#D4AF37]/30 text-[#D4AF37] text-xs rounded-lg transition-colors">
                    Completar
                  </button>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-[#666] mb-1">
                    <span>Progreso</span><span>{m.progreso}/{m.objetivo}</span>
                  </div>
                  <XPBar pct={m.progreso_pct}/>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {hechas.length > 0 && (
        <div>
          <h3 className="text-[#666] font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 size={16}/> Completadas ({hechas.length})
          </h3>
          <div className="space-y-2">
            {hechas.map(m => (
              <div key={m.id} className="bg-[#161616] border border-[#222] rounded-xl p-3
                                         opacity-50 flex items-center gap-3">
                <CheckCircle2 size={16} className="text-green-400 shrink-0"/>
                <span className="text-[#666] text-sm">{m.titulo}</span>
                <span className="ml-auto text-[#D4AF37] text-xs">+{m.xp_reward} XP</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function LogrosView({ logros }: { logros: Logro[] }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {logros.map(l => (
        <div key={l.id} className={clsx(
          'bg-[#161616] border rounded-xl p-4 text-center transition-all',
          l.desbloqueado ? 'border-[#D4AF37]/40 bg-[#D4AF37]/5' : 'border-[#222] opacity-40 grayscale'
        )}>
          <div className="text-3xl mb-2">{l.desbloqueado ? l.emoji : '🔒'}</div>
          <p className="text-[#E8E8E8] text-xs font-medium">{l.nombre}</p>
          <p className="text-[#D4AF37] text-xs mt-1">+{l.xp_reward} XP</p>
        </div>
      ))}
    </div>
  )
}

function RankingView({ ranking }: { ranking: LeaderEntry[] }) {
  return (
    <div className="bg-[#161616] border border-[#222] rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-[#222]">
        <h3 className="text-[#E8E8E8] font-semibold flex items-center gap-2">
          <Users size={16} className="text-[#D4AF37]"/> Top 10 Usuarios
        </h3>
      </div>
      <div className="divide-y divide-[#222]">
        {ranking.map(r => (
          <div key={r.user_id} className="flex items-center gap-4 px-4 py-3
                                           hover:bg-[#111] transition-colors">
            <span className={clsx(
              'w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold',
              r.posicion===1?'bg-yellow-400/20 text-yellow-400':
              r.posicion===2?'bg-gray-400/20 text-gray-400':
              r.posicion===3?'bg-amber-700/20 text-amber-600':'text-[#666]'
            )}>{r.posicion}</span>
            <span className="text-xl">{r.emoji}</span>
            <div className="flex-1 min-w-0">
              <p className="text-[#E8E8E8] text-sm font-medium truncate">{r.user_id}</p>
              <p className="text-[#666] text-xs">{r.rango} · Nivel {r.nivel}</p>
            </div>
            <div className="text-right">
              <p className="text-[#D4AF37] text-sm font-mono">{r.experiencia.toLocaleString()} XP</p>
              {r.streak>0 && <p className="text-orange-400 text-xs">🔥 {r.streak}d</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Concursos ─────────────────────────────────────────────────────────────────
interface Concurso {
  id: string; titulo: string; descripcion: string
  fecha_fin: string; premio: string; participantes: number
  estado: 'activo'|'finalizado'; ganador?: string
}

function ConcursosView() {
  const [concursos, setConcursos] = useState<Concurso[]>([])
  const [loading, setLoading] = useState(true)
  const [joining, setJoining] = useState<string|null>(null)
  const [msg, setMsg] = useState<string|null>(null)

  useEffect(() => {
    api.get<Concurso[]>('/academy/concursos')
      .then(setConcursos)
      .catch(() => setConcursos([]))
      .finally(() => setLoading(false))
  }, [])

  const unirse = async (id: string) => {
    setJoining(id)
    try {
      await api.post(`/academy/concursos/${id}/unirse`, {})
      setMsg('¡Te uniste al concurso! Que gane el mejor 🏆')
      setTimeout(() => setMsg(null), 3000)
    } catch { setMsg('Error al unirse') }
    finally { setJoining(null) }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-32">
      <div className="w-6 h-6 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin"/>
    </div>
  )

  const activos    = concursos.filter(c => c.estado === 'activo')
  const finalizados = concursos.filter(c => c.estado === 'finalizado')

  return (
    <div className="space-y-6">
      {msg && (
        <div className="fixed top-4 right-4 z-50 bg-[#161616] border border-[#D4AF37]/40
                        text-[#D4AF37] px-4 py-3 rounded-xl text-sm shadow-lg">
          {msg}
        </div>
      )}

      {/* Banner info */}
      <div className="bg-gradient-to-r from-[#D4AF37]/10 to-purple-500/10 border border-[#D4AF37]/20
                      rounded-2xl p-5">
        <h2 className="text-[#E8E8E8] font-bold text-lg flex items-center gap-2 mb-2">
          <Swords size={20} className="text-[#D4AF37]"/> Concursos entre Contadores
        </h2>
        <p className="text-[#666] text-sm">
          Compite con otros usuarios de Hermes Academy. El ganador recibe acceso al
          <span className="text-[#D4AF37] font-semibold"> Paquete Master</span> por un mes.
          ¡Demuestra tu dominio fiscal!
        </p>
      </div>

      {activos.length === 0 && finalizados.length === 0 && (
        <div className="text-center py-12 text-[#666]">
          <Swords size={36} className="mx-auto mb-3 opacity-40"/>
          <p className="font-medium text-[#E8E8E8]">No hay concursos activos</p>
          <p className="text-sm mt-1">El próximo concurso llegará pronto. ¡Sigue estudiando!</p>
        </div>
      )}

      {activos.length > 0 && (
        <div>
          <h3 className="text-[#E8E8E8] font-semibold mb-3 flex items-center gap-2">
            <Zap size={16} className="text-[#D4AF37]"/> Concursos Activos
          </h3>
          <div className="space-y-3">
            {activos.map(c => (
              <div key={c.id} className="bg-[#161616] border border-[#D4AF37]/20 rounded-2xl p-5">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <h4 className="text-[#E8E8E8] font-semibold">{c.titulo}</h4>
                    <p className="text-[#666] text-sm mt-0.5">{c.descripcion}</p>
                  </div>
                  <span className="shrink-0 px-2 py-0.5 rounded-full text-xs bg-green-500/10
                                   text-green-400 border border-green-500/20">Activo</span>
                </div>
                <div className="flex flex-wrap gap-4 text-xs text-[#666] mb-4">
                  <span className="flex items-center gap-1">
                    <Trophy size={10} className="text-[#D4AF37]"/> Premio: <span className="text-[#D4AF37] font-medium">{c.premio}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Users size={10}/> {c.participantes} participantes
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock size={10}/> Hasta: {new Date(c.fecha_fin).toLocaleDateString('es-MX')}
                  </span>
                </div>
                <button
                  onClick={() => unirse(c.id)}
                  disabled={joining === c.id}
                  className="w-full py-2.5 bg-[#D4AF37] hover:bg-yellow-400 disabled:opacity-50
                             text-[#0A0A0A] font-semibold text-sm rounded-xl transition-colors">
                  {joining === c.id ? 'Uniéndose...' : '⚔️ Unirme al Concurso'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {finalizados.length > 0 && (
        <div>
          <h3 className="text-[#666] font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 size={16}/> Finalizados
          </h3>
          <div className="space-y-2">
            {finalizados.map(c => (
              <div key={c.id} className="bg-[#161616] border border-[#222] rounded-xl p-4 opacity-60">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[#E8E8E8] text-sm font-medium">{c.titulo}</p>
                    {c.ganador && (
                      <p className="text-[#666] text-xs mt-0.5">
                        🏆 Ganador: <span className="text-[#D4AF37]">{c.ganador}</span>
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-[#666] border border-[#333] px-2 py-0.5 rounded-full">
                    Finalizado
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Página Principal ──────────────────────────────────────────────────────────
export default function AcademyPage() {
  const router = useRouter()
  const [perfil, setPerfil]     = useState<Perfil | null>(null)
  const [cursos, setCursos]     = useState<Curso[]>([])
  const [misiones, setMisiones] = useState<Mision[]>([])
  const [logros, setLogros]     = useState<Logro[]>([])
  const [ranking, setRanking]   = useState<LeaderEntry[]>([])
  const [tab, setTab]           = useState<'cursos'|'misiones'|'logros'|'ranking'|'concursos'>('cursos')
  const [loading, setLoading]   = useState(true)
  const [toast, setToast]       = useState<string|null>(null)
  const [error, setError]       = useState(false)

  const showToast = (msg: string) => {
    setToast(msg); setTimeout(() => setToast(null), 3000)
  }

  useEffect(() => {
    Promise.all([
      api.get<Perfil>('/academy/perfil'),
      api.get<Curso[]>('/academy/cursos'),
      api.get<Mision[]>('/academy/misiones'),
      api.get<Logro[]>('/academy/logros'),
      api.get<LeaderEntry[]>('/academy/leaderboard'),
    ]).then(([p, c, m, l, r]) => {
      setPerfil(p); setCursos(c); setMisiones(m); setLogros(l); setRanking(r)
    }).catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  const completarMision = async (id: string) => {
    try {
      const res = await api.post<any>(`/academy/misiones/${id}/completar`, {})
      setMisiones(prev => prev.map(m => m.id===id ? {...m, completada:true} : m))
      setPerfil(prev => prev ? {...prev, experiencia:res.experiencia, nivel:res.nivel, rango:res.rango} : prev)
      showToast(`+${res.xp_ganada} XP — ¡Misión completada!`)
    } catch { showToast('Error al completar misión') }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin"/>
    </div>
  )

  if (error || !perfil) return (
    <div className="p-8 text-center">
      <GraduationCap size={40} className="text-[#666] mx-auto mb-3"/>
      <p className="text-[#666]">No se pudo cargar la Academy. Intenta recargar la página.</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#0A0A0A] p-4 md:p-6 space-y-6">
      {toast && <Toast msg={toast}/>}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#E8E8E8] flex items-center gap-2">
            <GraduationCap size={22} className="text-[#D4AF37]"/> Hermes Academy
          </h1>
          <p className="text-[#666] text-sm mt-0.5">Tu progreso como usuario Hermes</p>
        </div>
        <div className="text-right">
          <p className="text-[#D4AF37] font-bold">{perfil.rango_emoji} {perfil.rango}</p>
          <p className="text-[#666] text-xs">Nivel {perfil.nivel}</p>
        </div>
      </div>

      {/* Perfil Card */}
      <div className="bg-[#161616] border border-[#222] rounded-2xl p-5">
        <div className="flex flex-col md:flex-row md:items-center gap-5">
          {/* Avatar */}
          <div className="w-16 h-16 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/30
                          flex items-center justify-center text-4xl shrink-0">
            {perfil.rango_emoji}
          </div>
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-[#E8E8E8] font-bold">{perfil.nombre || 'Usuario'}</span>
              <span className="px-2 py-0.5 rounded-full text-xs bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/20">
                {perfil.rango}
              </span>
              {perfil.streak_dias > 0 && (
                <span className="text-xs text-orange-400 flex items-center gap-1">
                  <Flame size={12}/> {perfil.streak_dias}d racha
                </span>
              )}
            </div>
            <p className="text-[#666] text-xs mb-2">Nivel {perfil.nivel}</p>
            <XPBar pct={perfil.progreso_pct} />
            <p className="text-[#666] text-xs mt-1">
              {perfil.experiencia.toLocaleString()} / {perfil.xp_siguiente_nivel.toLocaleString()} XP
            </p>
          </div>
          {/* Stats rápidos */}
          <div className="flex md:flex-col gap-4 md:gap-2 text-center md:text-right shrink-0">
            <div>
              <p className="text-[#D4AF37] font-bold text-lg">{perfil.stats?.cursos_completados ?? 0}</p>
              <p className="text-[#666] text-xs">Cursos</p>
            </div>
            <div>
              <p className="text-[#D4AF37] font-bold text-lg">{perfil.logros_desbloqueados}</p>
              <p className="text-[#666] text-xs">Logros</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#111] p-1 rounded-xl overflow-x-auto">
        {([
          {id:'cursos',    label:'Cursos',    icon: BookOpen},
          {id:'misiones',  label:'Misiones',  icon: Target},
          {id:'logros',    label:'Logros',    icon: Trophy},
          {id:'ranking',   label:'Ranking',   icon: TrendingUp},
          {id:'concursos', label:'Concursos', icon: Swords},
        ] as const).map(({id, label, icon: Icon}) => (
          <button key={id} onClick={() => setTab(id)}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all',
              tab===id
                ? 'bg-[#D4AF37] text-[#0A0A0A]'
                : 'text-[#666] hover:text-[#E8E8E8]'
            )}>
            <Icon size={13}/> {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab==='cursos'    && <CursosView cursos={cursos} onSelect={(slug) => router.push(`/academy/curso/${slug}`)} />}
      {tab==='misiones'  && <MisionesView misiones={misiones} onCompletar={completarMision}/>}
      {tab==='logros'    && <LogrosView logros={logros}/>}
      {tab==='ranking'   && <RankingView ranking={ranking}/>}
      {tab==='concursos' && <ConcursosView />}
    </div>
  )
}
