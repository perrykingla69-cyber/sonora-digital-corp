'use client'

import { useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { Zap } from 'lucide-react'

function ResetForm() {
  const params = useSearchParams()
  const router = useRouter()
  const token  = params.get('token') || ''

  const [password, setPassword]   = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [done, setDone]           = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== password2) { setError('Las contraseñas no coinciden'); return }
    if (password.length < 8)   { setError('Mínimo 8 caracteres'); return }
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/reset-password', { token, new_password: password })
      setDone(true)
      setTimeout(() => router.push('/login'), 2500)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Token inválido o expirado')
    } finally {
      setLoading(false)
    }
  }

  if (!token) return (
    <p className="text-red-400 text-sm text-center">Token no válido. Solicita un nuevo enlace.</p>
  )

  return done ? (
    <div className="text-center space-y-3">
      <div className="text-4xl">✅</div>
      <p className="text-white font-semibold">Contraseña actualizada</p>
      <p className="text-gray-400 text-sm">Redirigiendo al login...</p>
    </div>
  ) : (
    <form onSubmit={handleSubmit} className="space-y-5">
      <h1 className="text-white text-xl font-semibold text-center">Nueva contraseña</h1>

      {error && (
        <div className="bg-red-900/40 text-red-300 text-sm px-4 py-2 rounded-lg">{error}</div>
      )}

      <div>
        <label className="block text-sm text-gray-400 mb-1.5">Nueva contraseña</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required minLength={8}
          className="w-full bg-gray-700 text-white rounded-lg px-4 py-2.5 text-sm
                     border border-gray-600 focus:border-brand-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="block text-sm text-gray-400 mb-1.5">Confirmar contraseña</label>
        <input
          type="password"
          value={password2}
          onChange={e => setPassword2(e.target.value)}
          required
          className="w-full bg-gray-700 text-white rounded-lg px-4 py-2.5 text-sm
                     border border-gray-600 focus:border-brand-500 focus:outline-none"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                   text-white font-semibold rounded-lg py-2.5 text-sm transition-colors"
      >
        {loading ? 'Guardando...' : 'Cambiar contraseña'}
      </button>
    </form>
  )
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Zap className="text-brand-500" size={28} />
          <span className="text-white font-bold text-2xl tracking-tight">Hermes</span>
        </div>
        <div className="bg-gray-800 rounded-2xl p-8">
          <Suspense fallback={<p className="text-gray-400 text-sm text-center">Cargando...</p>}>
            <ResetForm />
          </Suspense>
        </div>
      </div>
    </div>
  )
}
