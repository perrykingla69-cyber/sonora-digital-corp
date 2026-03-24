'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  Play, Pause, Volume2, Headphones, FileText,
  CheckCircle2, Send, Star, ChevronRight, Mic
} from 'lucide-react'
import clsx from 'clsx'
import { api } from '@/lib/api'

interface ClaseDetail {
  id: string; titulo: string; tipo: string
  contenido: string; video_url: string | null
  podcast_url: string | null; duracion_min: number
  xp_reward: number; completada: boolean
  progreso_pct: number; notas: string; es_examen: boolean
}

// ── Video Player (YouTube embed + open-source/MP4) ────────────────────────────
function VideoPlayer({ url }: { url: string }) {
  const isYoutube = url.includes('youtube.com') || url.includes('youtu.be')
  const isMP4 = url.endsWith('.mp4') || url.includes('/video/')

  if (isYoutube) {
    const embedUrl = url.includes('embed')
      ? url
      : url.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
    return (
      <div className="relative w-full" style={{paddingTop:'56.25%'}}>
        <iframe
          src={`${embedUrl}?rel=0&modestbranding=1`}
          className="absolute inset-0 w-full h-full rounded-xl"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope"
          allowFullScreen title="Clase Mystic Academy"
        />
      </div>
    )
  }

  if (isMP4) {
    return (
      <video controls className="w-full rounded-xl bg-black max-h-96">
        <source src={url} type="video/mp4"/>
        Tu navegador no soporta video HTML5.
      </video>
    )
  }

  // iFrame genérico (NotebookLM, Loom, Vimeo, etc.)
  return (
    <div className="relative w-full" style={{paddingTop:'56.25%'}}>
      <iframe src={url} className="absolute inset-0 w-full h-full rounded-xl"
              allowFullScreen title="Clase Mystic Academy"/>
    </div>
  )
}

// ── Podcast Player (NotebookLM Audio Overview) ────────────────────────────────
function PodcastPlayer({ url }: { url: string }) {
  return (
    <div className="bg-[#111] border border-[#D4AF37]/20 rounded-xl p-4">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-[#D4AF37]/10 flex items-center justify-center">
          <Headphones size={18} className="text-[#D4AF37]"/>
        </div>
        <div>
          <p className="text-[#E8E8E8] text-sm font-medium">Audio Overview — NotebookLM</p>
          <p className="text-[#666] text-xs flex items-center gap-1">
            <Mic size={10}/> Podcast generado con IA
          </p>
        </div>
      </div>
      {url.endsWith('.mp3') || url.endsWith('.wav') || url.endsWith('.ogg') ? (
        <audio controls className="w-full">
          <source src={url}/>
        </audio>
      ) : (
        <a href={url} target="_blank" rel="noopener noreferrer"
           className="flex items-center gap-2 text-[#D4AF37] text-sm hover:underline">
          <Play size={14}/> Abrir podcast en NotebookLM
          <ChevronRight size={12}/>
        </a>
      )}
    </div>
  )
}

// ── Contenido Markdown (simple renderer) ─────────────────────────────────────
function MarkdownContent({ md }: { md: string }) {
  const rendered = md
    .replace(/^### (.+)$/gm, '<h3 class="text-[#E8E8E8] font-semibold text-base mt-4 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-[#E8E8E8] font-bold text-lg mt-5 mb-2">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-[#D4AF37] font-bold text-xl mt-4 mb-3">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-[#E8E8E8]">$1</strong>')
    .replace(/`(.+?)`/g, '<code class="bg-[#222] text-[#D4AF37] px-1 py-0.5 rounded text-xs font-mono">$1</code>')
    .replace(/^\| (.+) \|$/gm, '<tr>$1</tr>')
    .replace(/^- (.+)$/gm, '<li class="text-[#666] text-sm ml-4 list-disc">$1</li>')
    .replace(/\n\n/g, '<br/><br/>')

  return (
    <div className="prose prose-invert max-w-none text-[#666] text-sm leading-relaxed"
         dangerouslySetInnerHTML={{ __html: rendered }}/>
  )
}

// ── Quiz interactivo ──────────────────────────────────────────────────────────
function QuizView({ contenido, onComplete }: { contenido: string; onComplete: (pct: number) => void }) {
  const preguntas = JSON.parse(contenido || '[]')
  const [respuestas, setRespuestas] = useState<Record<number, number>>({})
  const [enviado, setEnviado] = useState(false)

  const enviar = () => {
    const correctas = preguntas.filter((_: any, i: number) =>
      respuestas[i] === preguntas[i].correcta).length
    const pct = Math.round(correctas / preguntas.length * 100)
    setEnviado(true)
    onComplete(pct)
  }

  return (
    <div className="space-y-6">
      {preguntas.map((p: any, i: number) => (
        <div key={i} className="bg-[#111] border border-[#222] rounded-xl p-4">
          <p className="text-[#E8E8E8] text-sm font-medium mb-3">
            {i + 1}. {p.pregunta}
          </p>
          <div className="space-y-2">
            {p.opciones.map((op: string, j: number) => {
              const selected = respuestas[i] === j
              const isCorrect = enviado && j === p.correcta
              const isWrong = enviado && selected && j !== p.correcta
              return (
                <button key={j}
                  onClick={() => !enviado && setRespuestas(r => ({...r, [i]: j}))}
                  className={clsx(
                    'w-full text-left px-4 py-2.5 rounded-lg border text-sm transition-colors',
                    isCorrect ? 'bg-green-500/10 border-green-500/40 text-green-400' :
                    isWrong   ? 'bg-red-500/10 border-red-500/40 text-red-400' :
                    selected  ? 'bg-[#D4AF37]/10 border-[#D4AF37]/40 text-[#D4AF37]' :
                                'bg-[#161616] border-[#222] text-[#666] hover:border-[#333]'
                  )}>
                  {op}
                </button>
              )
            })}
          </div>
        </div>
      ))}
      {!enviado && (
        <button onClick={enviar}
          disabled={Object.keys(respuestas).length < preguntas.length}
          className="w-full py-3 bg-[#D4AF37] text-[#0A0A0A] font-bold rounded-xl
                     hover:bg-yellow-400 transition-colors disabled:opacity-50">
          Enviar respuestas
        </button>
      )}
      {enviado && (
        <div className="text-center p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
          <p className="text-green-400 font-bold text-lg">
            {Math.round(Object.entries(respuestas).filter(([i,v]) =>
              v === preguntas[parseInt(i)].correcta).length / preguntas.length * 100)}% correcto
          </p>
          <p className="text-[#666] text-sm mt-1">¡Sigue practicando!</p>
        </div>
      )}
    </div>
  )
}

// ── Tarea con calificación IA ─────────────────────────────────────────────────
function TareaView({ claseId, enunciado }: { claseId: string; enunciado: string }) {
  const [respuesta, setRespuesta] = useState('')
  const [resultado, setResultado] = useState<{calificacion:number; feedback:string} | null>(null)
  const [loading, setLoading] = useState(false)

  const enviar = async () => {
    if (!respuesta.trim()) return
    setLoading(true)
    try {
      const res = await api.post<any>(`/academy/tareas/${claseId}/calificar`, {
        respuesta, enunciado
      })
      setResultado(res)
    } catch {
      setResultado({ calificacion: 0, feedback: 'Error al calificar. Intenta de nuevo.' })
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <div className="bg-[#111] border border-[#222] rounded-xl p-4">
        <p className="text-[#E8E8E8] text-sm font-medium mb-1">📋 Enunciado</p>
        <p className="text-[#666] text-sm">{enunciado}</p>
      </div>
      {!resultado ? (
        <>
          <textarea
            value={respuesta}
            onChange={e => setRespuesta(e.target.value)}
            placeholder="Escribe tu respuesta aquí..."
            rows={6}
            className="w-full bg-[#161616] border border-[#222] rounded-xl p-4
                       text-[#E8E8E8] text-sm placeholder:text-[#444] resize-none
                       focus:outline-none focus:border-[#D4AF37]/40"/>
          <button onClick={enviar} disabled={loading || !respuesta.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-[#D4AF37] text-[#0A0A0A]
                       font-bold rounded-xl hover:bg-yellow-400 transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed">
            {loading
              ? <span className="w-4 h-4 border-2 border-[#0A0A0A] border-t-transparent rounded-full animate-spin"/>
              : <Send size={16}/>
            }
            {loading ? 'Calificando con IA...' : 'Enviar para calificar'}
          </button>
        </>
      ) : (
        <div className="bg-[#161616] border border-[#D4AF37]/30 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex gap-0.5">
              {[1,2,3,4,5].map(s => (
                <Star key={s} size={20}
                  className={s <= Math.round(resultado.calificacion/2)
                    ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-[#333]'}/>
              ))}
            </div>
            <span className="text-[#D4AF37] font-bold text-xl">{resultado.calificacion}/10</span>
          </div>
          <div className="bg-[#111] rounded-xl p-4">
            <p className="text-xs text-[#D4AF37] font-semibold mb-2">🤖 Retroalimentación IA</p>
            <p className="text-[#666] text-sm leading-relaxed">{resultado.feedback}</p>
          </div>
          <button onClick={() => { setResultado(null); setRespuesta('') }}
            className="text-[#666] text-xs hover:text-[#E8E8E8]">
            Intentar de nuevo
          </button>
        </div>
      )}
    </div>
  )
}

// ── Página principal de Clase ─────────────────────────────────────────────────
export default function ClasePage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [clase, setClase] = useState<ClaseDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [completada, setCompletada] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  const showToast = (msg: string) => {
    setToast(msg); setTimeout(() => setToast(null), 3000)
  }

  useEffect(() => {
    api.get<ClaseDetail>(`/academy/clases/${id}`)
      .then(d => { setClase(d); setCompletada(d.completada) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  const marcarCompleta = async () => {
    try {
      const res = await api.post<any>(`/academy/clases/${id}/completar`, {})
      setCompletada(true)
      showToast(`+${res.xp_ganada} XP — ¡Clase completada!`)
    } catch { showToast('Error al marcar como completada') }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin"/>
    </div>
  )
  if (!clase) return <div className="p-8 text-center text-[#666]">Clase no encontrada.</div>

  return (
    <div className="min-h-screen bg-[#0A0A0A] max-w-4xl mx-auto">
      {toast && (
        <div className="fixed top-4 right-4 z-50 bg-[#161616] border border-[#D4AF37]/40
                        text-[#D4AF37] px-4 py-3 rounded-xl text-sm shadow-lg">
          {toast}
        </div>
      )}

      {/* Sticky header */}
      <div className="sticky top-0 z-10 bg-[#0A0A0A]/95 backdrop-blur border-b border-[#222] px-4 py-3">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-[#666] hover:text-[#E8E8E8]">←</button>
          <div className="flex-1 min-w-0">
            <p className="text-[#E8E8E8] text-sm font-medium truncate">{clase.titulo}</p>
            <p className="text-[#666] text-xs">{clase.duracion_min} min · +{clase.xp_reward} XP</p>
          </div>
          {completada
            ? <span className="flex items-center gap-1 text-green-400 text-xs font-medium">
                <CheckCircle2 size={14}/> Completada
              </span>
            : <button onClick={marcarCompleta}
                className="px-3 py-1.5 bg-[#D4AF37]/10 border border-[#D4AF37]/30
                           text-[#D4AF37] text-xs rounded-lg hover:bg-[#D4AF37]/20 transition-colors">
                Marcar lista
              </button>
          }
        </div>
      </div>

      <div className="p-4 md:p-6 space-y-6">
        {/* Video principal */}
        {clase.video_url && <VideoPlayer url={clase.video_url}/>}

        {/* Podcast NotebookLM */}
        {clase.podcast_url && <PodcastPlayer url={clase.podcast_url}/>}

        {/* Título */}
        <div>
          <h1 className="text-[#E8E8E8] font-bold text-xl">{clase.titulo}</h1>
          {clase.es_examen && (
            <span className="inline-flex items-center gap-1 mt-2 px-3 py-1 bg-purple-500/10
                             border border-purple-500/30 text-purple-400 text-xs rounded-full">
              📝 Examen — calificado por IA
            </span>
          )}
        </div>

        {/* Contenido según tipo */}
        {clase.tipo === 'quiz' && clase.contenido && (
          <QuizView
            contenido={clase.contenido}
            onComplete={(pct) => {
              api.post(`/academy/clases/${id}/progreso`, { pct }).catch(()=>{})
              if (pct >= 70) marcarCompleta()
            }}
          />
        )}

        {clase.tipo === 'ejercicio' && clase.contenido && (
          <>
            <MarkdownContent md={clase.contenido}/>
            <TareaView claseId={id} enunciado={clase.contenido}/>
          </>
        )}

        {['video','lectura','hibrido'].includes(clase.tipo) && clase.contenido && (
          <div className="bg-[#161616] border border-[#222] rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <FileText size={14} className="text-[#D4AF37]"/>
              <span className="text-[#D4AF37] text-xs font-semibold uppercase tracking-wide">
                Material de clase
              </span>
            </div>
            <MarkdownContent md={clase.contenido}/>
          </div>
        )}

        {/* Botón completar al final */}
        {!completada && clase.tipo !== 'quiz' && (
          <button onClick={marcarCompleta}
            className="w-full py-4 bg-[#D4AF37] text-[#0A0A0A] font-bold rounded-2xl
                       hover:bg-yellow-400 transition-colors flex items-center justify-center gap-2">
            <CheckCircle2 size={18}/>
            Completar clase · +{clase.xp_reward} XP
          </button>
        )}
      </div>
    </div>
  )
}
