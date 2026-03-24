'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  Play, FileText, HelpCircle, Layers, Target,
  ChevronRight, Lock, CheckCircle2, Clock, Zap,
  BookOpen, ChevronDown, ChevronUp, Calendar
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '@/lib/api'

interface Clase {
  id: string; titulo: string; tipo: string
  duracion_min: number; xp_reward: number; orden: number
  completada: boolean; progreso_pct: number; semana: number
  es_examen: boolean; accesible: boolean
}
interface Modulo {
  id: string; titulo: string; orden: number
  xp_reward: number; clases: Clase[]
}
interface CursoDetail {
  id: string; slug: string; titulo: string
  descripcion: string; icono: string
  xp_total: number; duracion_min: number; modulos: Modulo[]
}

const tipoIcon: Record<string, any> = {
  video: Play, lectura: FileText, ejercicio: Target,
  quiz: HelpCircle, hibrido: Layers
}
const tipoLabel: Record<string, string> = {
  video:'Video', lectura:'Lectura', ejercicio:'Ejercicio',
  quiz:'Quiz', hibrido:'Video + Práctica'
}
const semanaLabel = (s: number) => s === 0 ? 'Examen Final' : `Semana ${s}`

export default function CursoPage() {
  const { slug } = useParams<{ slug: string }>()
  const router = useRouter()
  const [curso, setCurso] = useState<CursoDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [openMod, setOpenMod] = useState<string | null>(null)

  useEffect(() => {
    api.get<CursoDetail>(`/academy/cursos/${slug}`)
      .then(d => { setCurso(d); setOpenMod(d.modulos[0]?.id ?? null) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin"/>
    </div>
  )
  if (!curso) return <div className="p-8 text-[#666] text-center">Curso no encontrado.</div>

  const totalClases = curso.modulos.reduce((a, m) => a + m.clases.length, 0)
  const completadas = curso.modulos.reduce((a, m) =>
    a + m.clases.filter(c => c.completada).length, 0)

  return (
    <div className="min-h-screen bg-[#0A0A0A] p-4 md:p-6">
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <button onClick={() => router.back()}
          className="mt-1 text-[#666] hover:text-[#E8E8E8] transition-colors">
          ← Volver
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <span className="text-3xl">{curso.icono}</span>
            <h1 className="text-xl font-bold text-[#E8E8E8]">{curso.titulo}</h1>
          </div>
          <p className="text-[#666] text-sm">{curso.descripcion}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-[#666]">
            <span className="flex items-center gap-1"><Clock size={10}/> {curso.duracion_min} min</span>
            <span className="flex items-center gap-1"><Zap size={10} className="text-[#D4AF37]"/>{curso.xp_total} XP</span>
            <span className="flex items-center gap-1"><BookOpen size={10}/>{completadas}/{totalClases} clases</span>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="bg-[#161616] border border-[#222] rounded-xl p-4 mb-6">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-[#E8E8E8] font-medium">Tu progreso</span>
          <span className="text-[#D4AF37] font-mono">
            {totalClases > 0 ? Math.round(completadas / totalClases * 100) : 0}%
          </span>
        </div>
        <div className="w-full h-3 bg-[#222] rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-[#D4AF37] to-yellow-300 rounded-full transition-all duration-700"
               style={{ width: `${totalClases > 0 ? completadas / totalClases * 100 : 0}%` }}/>
        </div>
      </div>

      {/* Módulos accordion */}
      <div className="space-y-3">
        {curso.modulos.map((mod, mi) => {
          const isOpen = openMod === mod.id
          const semanas = [...new Set(mod.clases.map(c => c.semana))].sort()
          return (
            <div key={mod.id} className="bg-[#161616] border border-[#222] rounded-2xl overflow-hidden">
              <button
                onClick={() => setOpenMod(isOpen ? null : mod.id)}
                className="w-full flex items-center justify-between p-4 hover:bg-[#1a1a1a] transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/30
                                  flex items-center justify-center text-[#D4AF37] text-sm font-bold">
                    {mi + 1}
                  </div>
                  <div className="text-left">
                    <p className="text-[#E8E8E8] font-medium text-sm">{mod.titulo}</p>
                    <p className="text-[#666] text-xs">
                      {mod.clases.filter(c => c.completada).length}/{mod.clases.length} clases
                      · +{mod.xp_reward} XP
                    </p>
                  </div>
                </div>
                {isOpen ? <ChevronUp size={16} className="text-[#666]"/> : <ChevronDown size={16} className="text-[#666]"/>}
              </button>

              {isOpen && (
                <div className="border-t border-[#222]">
                  {semanas.map(semana => (
                    <div key={semana}>
                      <div className="px-4 py-2 bg-[#111] flex items-center gap-2">
                        <Calendar size={12} className="text-[#D4AF37]"/>
                        <span className="text-[#D4AF37] text-xs font-semibold">{semanaLabel(semana)}</span>
                      </div>
                      {mod.clases.filter(c => c.semana === semana).map((cl) => {
                        const Icon = tipoIcon[cl.tipo] ?? Play
                        return (
                          <button key={cl.id}
                            onClick={() => cl.accesible && router.push(`/academy/clase/${cl.id}`)}
                            className={clsx(
                              'w-full flex items-center gap-4 px-4 py-3 border-t border-[#1a1a1a]',
                              'transition-colors text-left',
                              cl.accesible
                                ? 'hover:bg-[#1a1a1a] cursor-pointer'
                                : 'opacity-50 cursor-not-allowed'
                            )}>
                            {/* Thumbnail / tipo icon */}
                            <div className={clsx(
                              'w-10 h-10 rounded-lg flex items-center justify-center shrink-0',
                              cl.completada
                                ? 'bg-green-500/10 border border-green-500/30'
                                : cl.es_examen
                                  ? 'bg-purple-500/10 border border-purple-500/30'
                                  : 'bg-[#D4AF37]/10 border border-[#D4AF37]/20'
                            )}>
                              {cl.completada
                                ? <CheckCircle2 size={18} className="text-green-400"/>
                                : cl.es_examen
                                  ? <HelpCircle size={18} className="text-purple-400"/>
                                  : <Icon size={18} className="text-[#D4AF37]"/>
                              }
                            </div>

                            <div className="flex-1 min-w-0">
                              <p className={clsx(
                                'text-sm font-medium truncate',
                                cl.completada ? 'text-[#666]' : 'text-[#E8E8E8]'
                              )}>
                                {cl.es_examen && '📝 '}{cl.titulo}
                              </p>
                              <div className="flex items-center gap-3 mt-0.5">
                                <span className="text-[#666] text-xs">{tipoLabel[cl.tipo] ?? cl.tipo}</span>
                                <span className="text-[#666] text-xs flex items-center gap-1">
                                  <Clock size={9}/>{cl.duracion_min}min
                                </span>
                                <span className="text-[#D4AF37] text-xs">+{cl.xp_reward} XP</span>
                              </div>
                              {cl.progreso_pct > 0 && !cl.completada && (
                                <div className="mt-1 w-24 h-1 bg-[#222] rounded-full overflow-hidden">
                                  <div className="h-full bg-[#D4AF37] rounded-full"
                                       style={{width:`${cl.progreso_pct}%`}}/>
                                </div>
                              )}
                            </div>

                            {cl.accesible
                              ? <ChevronRight size={14} className="text-[#666] shrink-0"/>
                              : <Lock size={14} className="text-[#666] shrink-0"/>
                            }
                          </button>
                        )
                      })}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
