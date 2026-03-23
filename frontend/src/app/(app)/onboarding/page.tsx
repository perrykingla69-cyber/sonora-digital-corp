'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import {
  Building2, Scale, Users, Puzzle, CheckCircle2,
  ChevronRight, ChevronLeft, Loader2, Zap,
  FileText, MessageCircle, Receipt, BarChart3, CreditCard,
} from 'lucide-react'

// ── Types ─────────────────────────────────────────────────────────────────────

type Giro = 'manufactura' | 'comercio' | 'servicios' | 'construccion'
type Regimen = 'personas_morales' | 'resico' | 'actividad_empresarial' | 'asalariados'
type RangoEmpleados = '0' | '1-5' | '6-20' | '21+'
type Modulo = 'facturas' | 'nomina' | 'cierre_mensual' | 'whatsapp' | 'diot'

interface FormData {
  // Paso 1
  rfc: string
  nombre_empresa: string
  giro: Giro | ''
  // Paso 2
  regimen_fiscal: Regimen | ''
  // Paso 3
  rango_empleados: RangoEmpleados | ''
  // Paso 4
  modulos: Modulo[]
}

const INITIAL_FORM: FormData = {
  rfc: '',
  nombre_empresa: '',
  giro: '',
  regimen_fiscal: '',
  rango_empleados: '',
  modulos: [],
}

// ── Config opciones ───────────────────────────────────────────────────────────

const GIROS: { value: Giro; label: string; emoji: string }[] = [
  { value: 'manufactura',  label: 'Manufactura',   emoji: '🏭' },
  { value: 'comercio',     label: 'Comercio',       emoji: '🛒' },
  { value: 'servicios',    label: 'Servicios',      emoji: '💼' },
  { value: 'construccion', label: 'Construcción',   emoji: '🏗️' },
]

const REGIMENES: { value: Regimen; label: string; desc: string }[] = [
  { value: 'personas_morales',     label: 'Personas Morales',       desc: 'Sociedad Anónima, SRL, AC, etc.' },
  { value: 'resico',               label: 'RESICO',                  desc: 'Régimen Simplificado de Confianza' },
  { value: 'actividad_empresarial', label: 'Actividad Empresarial',  desc: 'Personas físicas con actividad' },
  { value: 'asalariados',          label: 'Asalariados',             desc: 'Solo ingresos por salario' },
]

const RANGOS_EMPLEADOS: { value: RangoEmpleados; label: string; desc: string }[] = [
  { value: '0',    label: 'Sin empleados', desc: 'Solo socios o dueño' },
  { value: '1-5',  label: '1 – 5',         desc: 'Micro empresa' },
  { value: '6-20', label: '6 – 20',        desc: 'Pequeña empresa' },
  { value: '21+',  label: '21 o más',      desc: 'Mediana empresa' },
]

const MODULOS_CONFIG: {
  value: Modulo
  label: string
  desc: string
  icon: React.ReactNode
}[] = [
  { value: 'facturas',       label: 'Facturas CFDI',     desc: 'Emisión y recepción de CFDI 4.0',            icon: <FileText size={18} /> },
  { value: 'nomina',         label: 'Nómina',            desc: 'Timbrado, cálculo IMSS, ISR',                icon: <CreditCard size={18} /> },
  { value: 'cierre_mensual', label: 'Cierre Mensual',    desc: 'Declaraciones, IVA, ISR, EBITDA',            icon: <BarChart3 size={18} /> },
  { value: 'whatsapp',       label: 'WhatsApp IA',       desc: 'Consultas contables por WhatsApp 24/7',      icon: <MessageCircle size={18} /> },
  { value: 'diot',           label: 'DIOT',              desc: 'Declaración Informativa de Operaciones',     icon: <Receipt size={18} /> },
]

const PASO_META = [
  { title: 'Tu empresa',       desc: 'Datos básicos de identificación fiscal',     icon: <Building2 size={22} /> },
  { title: 'Régimen fiscal',   desc: 'Tu situación ante el SAT',                  icon: <Scale size={22} /> },
  { title: 'Equipo',           desc: '¿Cuántos colaboradores tienes?',             icon: <Users size={22} /> },
  { title: 'Módulos',          desc: 'Activa las herramientas que necesitas',       icon: <Puzzle size={22} /> },
  { title: 'Confirmación',     desc: 'Revisa y activa Mystic',                    icon: <CheckCircle2 size={22} /> },
]

// ── Helpers visuales ──────────────────────────────────────────────────────────

function GoldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="block text-xs font-semibold tracking-widest uppercase text-sovereign-gold mb-2">
      {children}
    </label>
  )
}

function GoldInput({
  value,
  onChange,
  placeholder,
  maxLength,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  maxLength?: number
}) {
  return (
    <input
      className="w-full bg-sovereign-surface border border-sovereign-border rounded-lg px-4 py-3
                 text-sovereign-text placeholder-sovereign-muted
                 focus:outline-none focus:border-sovereign-gold focus:ring-1 focus:ring-sovereign-gold/30
                 transition-colors text-sm"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      maxLength={maxLength}
    />
  )
}

function RadioCard({
  selected,
  onClick,
  children,
}: {
  selected: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer
        ${selected
          ? 'border-sovereign-gold bg-sovereign-gold/10 shadow-[0_0_12px_rgba(212,175,55,0.15)]'
          : 'border-sovereign-border bg-sovereign-surface hover:border-sovereign-gold/40'
        }`}
    >
      {children}
    </button>
  )
}

function CheckCard({
  selected,
  onClick,
  children,
}: {
  selected: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 cursor-pointer flex items-start gap-3
        ${selected
          ? 'border-sovereign-gold bg-sovereign-gold/10 shadow-[0_0_12px_rgba(212,175,55,0.15)]'
          : 'border-sovereign-border bg-sovereign-surface hover:border-sovereign-gold/40'
        }`}
    >
      <div className={`mt-0.5 w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors
        ${selected ? 'border-sovereign-gold bg-sovereign-gold' : 'border-sovereign-muted'}`}>
        {selected && <CheckCircle2 size={12} className="text-black" />}
      </div>
      {children}
    </button>
  )
}

function ResumenRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-sovereign-border/50 last:border-0">
      <span className="text-sovereign-muted text-sm">{label}</span>
      <span className="text-sovereign-text text-sm font-medium">{value}</span>
    </div>
  )
}

// ── Componente principal ──────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter()
  const [step, setStep] = useState(0) // 0-indexed
  const [form, setForm] = useState<FormData>(INITIAL_FORM)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const totalSteps = PASO_META.length
  const isLast = step === totalSteps - 1
  const isFirst = step === 0

  // ── Step names ──
  const STEP_NAMES = ['empresa', 'regimen', 'empleados', 'integraciones', 'confirmacion'] as const
  type StepName = typeof STEP_NAMES[number]

  function buildStepData(name: StepName) {
    switch (name) {
      case 'empresa':
        return { rfc: form.rfc.trim().toUpperCase(), nombre_empresa: form.nombre_empresa.trim(), giro: form.giro }
      case 'regimen':
        return { regimen_fiscal: form.regimen_fiscal }
      case 'empleados':
        return { rango_empleados: form.rango_empleados }
      case 'integraciones':
        return { modulos: form.modulos }
      case 'confirmacion':
        return {}
    }
  }

  function validateStep(): string | null {
    const name = STEP_NAMES[step]
    switch (name) {
      case 'empresa':
        if (!form.rfc.trim()) return 'El RFC es requerido'
        if (form.rfc.trim().length < 12 || form.rfc.trim().length > 13) return 'El RFC debe tener 12 o 13 caracteres'
        if (!form.nombre_empresa.trim()) return 'El nombre de la empresa es requerido'
        if (!form.giro) return 'Selecciona el giro de la empresa'
        break
      case 'regimen':
        if (!form.regimen_fiscal) return 'Selecciona el régimen fiscal'
        break
      case 'empleados':
        if (!form.rango_empleados) return 'Selecciona el rango de empleados'
        break
      case 'integraciones':
        if (form.modulos.length === 0) return 'Selecciona al menos un módulo'
        break
    }
    return null
  }

  async function handleNext() {
    setError(null)
    const validationErr = validateStep()
    if (validationErr) { setError(validationErr); return }

    setLoading(true)
    try {
      let currentSid = sessionId

      // Si no hay sesión, iniciarla
      if (!currentSid) {
        const startRes = await api.post<{ session_id: string }>('/onboarding/start', {})
        currentSid = startRes.session_id
        setSessionId(currentSid)
      }

      const stepName = STEP_NAMES[step]
      // Guardar paso actual
      await api.post('/onboarding/step', {
        session_id: currentSid,
        step: stepName,
        data: buildStepData(stepName),
      })

      setStep((s) => s + 1)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error al guardar el paso')
    } finally {
      setLoading(false)
    }
  }

  function handlePrev() {
    setError(null)
    setStep((s) => Math.max(0, s - 1))
  }

  async function handleComplete() {
    if (!sessionId) return
    setError(null)
    setLoading(true)
    try {
      await api.post('/onboarding/complete', { session_id: sessionId })
      router.push('/panel/dashboard')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error al completar el onboarding')
    } finally {
      setLoading(false)
    }
  }

  function toggleModulo(mod: Modulo) {
    setForm((f) => ({
      ...f,
      modulos: f.modulos.includes(mod)
        ? f.modulos.filter((m) => m !== mod)
        : [...f.modulos, mod],
    }))
  }

  const progreso = Math.round(((step) / totalSteps) * 100)

  // ── Labels para resumen ──
  const giroLabel = GIROS.find((g) => g.value === form.giro)?.label ?? '—'
  const regimenLabel = REGIMENES.find((r) => r.value === form.regimen_fiscal)?.label ?? '—'
  const empleadosLabel = RANGOS_EMPLEADOS.find((r) => r.value === form.rango_empleados)?.label ?? '—'
  const modulosLabel = form.modulos.length
    ? form.modulos.map((m) => MODULOS_CONFIG.find((c) => c.value === m)?.label ?? m).join(', ')
    : '—'

  return (
    <div className="min-h-screen bg-sovereign-bg flex flex-col items-center justify-center px-4 py-12">
      {/* Glow de fondo */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden>
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full bg-sovereign-gold/5 blur-[120px]" />
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 text-sovereign-gold font-display font-bold text-2xl tracking-tight mb-1">
            <Zap size={24} className="text-sovereign-gold" />
            MYSTIC
          </div>
          <p className="text-sovereign-muted text-sm">Configuración inicial · {step + 1} de {totalSteps}</p>
        </div>

        {/* Barra de progreso con puntos */}
        <div className="flex items-center justify-between mb-8 px-2">
          {PASO_META.map((meta, i) => {
            const done = i < step
            const active = i === step
            return (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div className="flex items-center w-full">
                  {/* Línea izquierda */}
                  {i > 0 && (
                    <div className={`flex-1 h-0.5 transition-colors duration-500 ${done ? 'bg-sovereign-gold' : 'bg-sovereign-border'}`} />
                  )}
                  {/* Punto */}
                  <div
                    className={`w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-500
                      ${done
                        ? 'bg-sovereign-gold border-sovereign-gold text-black'
                        : active
                          ? 'bg-transparent border-sovereign-gold text-sovereign-gold shadow-[0_0_12px_rgba(212,175,55,0.4)]'
                          : 'bg-transparent border-sovereign-border text-sovereign-muted'
                      }`}
                  >
                    {done
                      ? <CheckCircle2 size={16} />
                      : <span className="text-xs font-bold">{i + 1}</span>
                    }
                  </div>
                  {/* Línea derecha */}
                  {i < totalSteps - 1 && (
                    <div className={`flex-1 h-0.5 transition-colors duration-500 ${done ? 'bg-sovereign-gold' : 'bg-sovereign-border'}`} />
                  )}
                </div>
                {/* Label paso */}
                <span className={`mt-1.5 text-[10px] tracking-wide font-medium hidden sm:block
                  ${active ? 'text-sovereign-gold' : done ? 'text-sovereign-gold/60' : 'text-sovereign-muted'}`}>
                  {meta.title}
                </span>
              </div>
            )
          })}
        </div>

        {/* Card principal */}
        <div className="bg-sovereign-card border border-sovereign-border rounded-2xl shadow-2xl overflow-hidden">
          {/* Título del paso */}
          <div className="px-8 pt-8 pb-6 border-b border-sovereign-border/50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-sovereign-gold/10 border border-sovereign-gold/20 flex items-center justify-center text-sovereign-gold">
                {PASO_META[step].icon}
              </div>
              <div>
                <h2 className="text-sovereign-text font-display font-bold text-xl">
                  {PASO_META[step].title}
                </h2>
                <p className="text-sovereign-muted text-sm">{PASO_META[step].desc}</p>
              </div>
            </div>
          </div>

          {/* Contenido del paso */}
          <div className="px-8 py-7 space-y-5 min-h-[280px]">

            {/* PASO 1 — Empresa */}
            {step === 0 && (
              <>
                <div>
                  <GoldLabel>RFC de la empresa</GoldLabel>
                  <GoldInput
                    value={form.rfc}
                    onChange={(v) => setForm((f) => ({ ...f, rfc: v.toUpperCase() }))}
                    placeholder="FME080820LC2"
                    maxLength={13}
                  />
                  <p className="text-sovereign-muted text-xs mt-1">12 caracteres (persona moral) o 13 (persona física)</p>
                </div>
                <div>
                  <GoldLabel>Nombre o razón social</GoldLabel>
                  <GoldInput
                    value={form.nombre_empresa}
                    onChange={(v) => setForm((f) => ({ ...f, nombre_empresa: v }))}
                    placeholder="Fourgea Mexico SA de CV"
                  />
                </div>
                <div>
                  <GoldLabel>Giro empresarial</GoldLabel>
                  <div className="grid grid-cols-2 gap-3">
                    {GIROS.map((g) => (
                      <RadioCard
                        key={g.value}
                        selected={form.giro === g.value}
                        onClick={() => setForm((f) => ({ ...f, giro: g.value }))}
                      >
                        <span className="text-base mr-2">{g.emoji}</span>
                        <span className="text-sovereign-text text-sm font-medium">{g.label}</span>
                      </RadioCard>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* PASO 2 — Régimen fiscal */}
            {step === 1 && (
              <div className="space-y-3">
                {REGIMENES.map((r) => (
                  <RadioCard
                    key={r.value}
                    selected={form.regimen_fiscal === r.value}
                    onClick={() => setForm((f) => ({ ...f, regimen_fiscal: r.value }))}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full border-2 flex-shrink-0 transition-colors
                        ${form.regimen_fiscal === r.value ? 'border-sovereign-gold bg-sovereign-gold' : 'border-sovereign-muted'}`} />
                      <div>
                        <div className="text-sovereign-text text-sm font-semibold">{r.label}</div>
                        <div className="text-sovereign-muted text-xs">{r.desc}</div>
                      </div>
                    </div>
                  </RadioCard>
                ))}
              </div>
            )}

            {/* PASO 3 — Empleados */}
            {step === 2 && (
              <div className="space-y-3">
                {RANGOS_EMPLEADOS.map((r) => (
                  <RadioCard
                    key={r.value}
                    selected={form.rango_empleados === r.value}
                    onClick={() => setForm((f) => ({ ...f, rango_empleados: r.value }))}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded-full border-2 flex-shrink-0 transition-colors
                        ${form.rango_empleados === r.value ? 'border-sovereign-gold bg-sovereign-gold' : 'border-sovereign-muted'}`} />
                      <div>
                        <div className="text-sovereign-text text-sm font-semibold">{r.label} empleados</div>
                        <div className="text-sovereign-muted text-xs">{r.desc}</div>
                      </div>
                    </div>
                  </RadioCard>
                ))}
              </div>
            )}

            {/* PASO 4 — Integraciones */}
            {step === 3 && (
              <div className="space-y-3">
                <p className="text-sovereign-muted text-xs mb-1">Puedes cambiar esto después desde Configuración.</p>
                {MODULOS_CONFIG.map((m) => (
                  <CheckCard
                    key={m.value}
                    selected={form.modulos.includes(m.value)}
                    onClick={() => toggleModulo(m.value)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sovereign-gold">{m.icon}</span>
                        <span className="text-sovereign-text text-sm font-semibold">{m.label}</span>
                      </div>
                      <div className="text-sovereign-muted text-xs mt-0.5 ml-6">{m.desc}</div>
                    </div>
                  </CheckCard>
                ))}
              </div>
            )}

            {/* PASO 5 — Confirmación */}
            {step === 4 && (
              <div className="space-y-5">
                <div className="rounded-xl border border-sovereign-gold/20 bg-sovereign-gold/5 p-5 backdrop-blur-sm">
                  <div className="text-sovereign-gold text-xs font-bold tracking-widest uppercase mb-4">
                    Resumen de configuración
                  </div>
                  <ResumenRow label="RFC" value={form.rfc.toUpperCase() || '—'} />
                  <ResumenRow label="Empresa" value={form.nombre_empresa || '—'} />
                  <ResumenRow label="Giro" value={giroLabel} />
                  <ResumenRow label="Régimen fiscal" value={regimenLabel} />
                  <ResumenRow label="Empleados" value={`${empleadosLabel} empleados`} />
                  <ResumenRow label="Módulos activos" value={modulosLabel} />
                </div>
                <p className="text-sovereign-muted text-xs text-center leading-relaxed">
                  Al confirmar, Mystic quedará configurado para tu empresa.
                  Podrás ajustar estas opciones en cualquier momento desde el panel.
                </p>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mx-8 mb-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Navegación */}
          <div className="px-8 py-6 border-t border-sovereign-border/50 flex items-center justify-between">
            <button
              type="button"
              onClick={handlePrev}
              disabled={isFirst || loading}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl border text-sm font-medium transition-all
                ${isFirst
                  ? 'border-sovereign-border text-sovereign-muted cursor-not-allowed opacity-40'
                  : 'border-sovereign-border text-sovereign-text hover:border-sovereign-gold/40 hover:text-sovereign-gold'
                }`}
            >
              <ChevronLeft size={16} />
              Anterior
            </button>

            {/* Indicador de progreso textual */}
            <span className="text-sovereign-muted text-xs hidden sm:block">
              {progreso}% completado
            </span>

            {isLast ? (
              <button
                type="button"
                onClick={handleComplete}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-sovereign-gold text-black
                           text-sm font-bold hover:bg-sovereign-gold/90 transition-all
                           shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:shadow-[0_0_30px_rgba(212,175,55,0.5)]
                           disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
                Activar Mystic
              </button>
            ) : (
              <button
                type="button"
                onClick={handleNext}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-sovereign-gold text-black
                           text-sm font-bold hover:bg-sovereign-gold/90 transition-all
                           shadow-[0_0_20px_rgba(212,175,55,0.3)] hover:shadow-[0_0_30px_rgba(212,175,55,0.5)]
                           disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : null}
                Siguiente
                {!loading && <ChevronRight size={16} />}
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sovereign-muted text-xs mt-6">
          Mystic · Sonora Digital Corp · {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
