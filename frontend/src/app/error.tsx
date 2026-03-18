'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('App error:', error)
  }, [error])

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#111827' }}>
      <div style={{ background: '#1f2937', borderRadius: 16, padding: 32, maxWidth: 480, textAlign: 'center' }}>
        <h2 style={{ color: '#f87171', fontSize: 18, fontWeight: 600, marginBottom: 12 }}>
          Error del sistema
        </h2>
        <p style={{ color: '#9ca3af', fontSize: 14, marginBottom: 8 }}>
          {error.message || 'Error desconocido'}
        </p>
        {error.digest && (
          <p style={{ color: '#6b7280', fontSize: 12, fontFamily: 'monospace', marginBottom: 16 }}>
            ID: {error.digest}
          </p>
        )}
        <p style={{ color: '#6b7280', fontSize: 11, marginBottom: 16 }}>
          {error.stack?.split('\n').slice(0, 3).join(' | ')}
        </p>
        <button
          onClick={reset}
          style={{ background: '#3b5bf5', color: 'white', border: 'none', borderRadius: 8, padding: '8px 20px', fontSize: 14, cursor: 'pointer' }}
        >
          Reintentar
        </button>
      </div>
    </div>
  )
}
