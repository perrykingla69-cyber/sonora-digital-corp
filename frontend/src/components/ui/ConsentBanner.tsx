'use client'

import { useState, useEffect } from 'react'
import { Shield, X, ChevronDown, ChevronUp } from 'lucide-react'

export default function ConsentBanner() {
  const [visible, setVisible] = useState(false)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    const consent = localStorage.getItem('hermes_consent_v1')
    if (!consent) setVisible(true)
  }, [])

  const accept = () => {
    localStorage.setItem('hermes_consent_v1', JSON.stringify({
      accepted: true,
      date: new Date().toISOString(),
      analytics: true,
      functional: true,
    }))
    setVisible(false)
    // Registrar en backend
    fetch('/api/analytics/consent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ accepted: true, ts: Date.now() }),
    }).catch(() => {})
  }

  const decline = () => {
    localStorage.setItem('hermes_consent_v1', JSON.stringify({
      accepted: false,
      date: new Date().toISOString(),
      analytics: false,
      functional: true,
    }))
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-6 fade-up">
      <div
        className="max-w-3xl mx-auto rounded-2xl p-5"
        style={{
          background: 'rgba(255,255,255,0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(200,168,75,0.20)',
          boxShadow: '0 8px 40px rgba(0,0,0,0.12)',
        }}
      >
        <div className="flex items-start gap-4">
          <div
            className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #2D6A4F, #1B4332)' }}
          >
            <Shield size={16} className="text-white" />
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-sovereign-text mb-1">
              Tu privacidad, nuestra responsabilidad
            </p>
            <p className="text-xs text-sovereign-muted leading-relaxed">
              Usamos datos de uso (módulos, tiempos, errores) para mejorar tu experiencia.
              Nunca vendemos tu información. Cumplimos con la LFPDPPP.{' '}
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-sovereign-gold font-medium hover:underline inline-flex items-center gap-0.5"
              >
                {expanded ? 'Ver menos' : 'Ver detalle'}
                {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
            </p>

            {expanded && (
              <div className="mt-3 p-3 rounded-xl bg-gray-50 text-xs text-sovereign-muted space-y-1.5 fade-up">
                <p><span className="font-medium text-sovereign-text">✓ Recolectamos:</span> módulos usados, tiempo de sesión, ciudad aproximada (IP), tipo de dispositivo, preguntas frecuentes al asistente.</p>
                <p><span className="font-medium text-sovereign-text">✗ Nunca:</span> datos bancarios, passwords, información de terceros sin consentimiento.</p>
                <p><span className="font-medium text-sovereign-text">Finalidad:</span> optimizar el sistema, detectar errores y personalizar tu experiencia.</p>
                <p>
                  Puedes ejercer derechos ARCO en{' '}
                  <span className="text-sovereign-gold">privacidad@sonoradigitalcorp.com</span>
                </p>
              </div>
            )}
          </div>

          <button
            onClick={decline}
            className="flex-shrink-0 text-sovereign-subtle hover:text-sovereign-muted transition-colors"
            aria-label="Rechazar y cerrar"
          >
            <X size={16} />
          </button>
        </div>

        <div className="flex items-center gap-3 mt-4 pl-13">
          <button
            onClick={accept}
            className="btn-primary text-xs px-4 py-2"
          >
            Aceptar y continuar
          </button>
          <button
            onClick={decline}
            className="text-xs text-sovereign-muted hover:text-sovereign-text transition-colors"
          >
            Solo funcional
          </button>
        </div>
      </div>
    </div>
  )
}
