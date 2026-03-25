'use client'

import { useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'

export default function ForgotPasswordPage() {
  const [email, setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone]     = useState(false)
  const [msg, setMsg]       = useState('')
  const [error, setError]   = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const r = await api.post<{ ok: boolean; mensaje: string; wa_sent: boolean }>(
        '/auth/forgot-password', { email }
      )
      setMsg(r.mensaje)
      setDone(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al procesar la solicitud')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="flex items-center justify-center mb-8">
          <span className="text-white font-bold text-2xl tracking-tight">Hermes</span>
        </div>

        <div className="bg-gray-800 rounded-2xl p-8 space-y-5 border border-gray-700">

          {!done ? (
            <>
              <div className="text-center">
                <div className="w-12 h-12 bg-brand-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Mail size={22} className="text-brand-400" />
                </div>
                <h1 className="text-white text-xl font-semibold">¿Olvidaste tu contraseña?</h1>
                <p className="text-gray-400 text-sm mt-1">
                  Ingresa tu correo y te enviaremos una contraseña temporal por WhatsApp.
                </p>
              </div>

              {error && (
                <div className="bg-red-900/40 border border-red-700 text-red-300 text-sm px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Correo electrónico</label>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                    className="w-full bg-gray-700 text-white rounded-lg px-4 py-2.5 text-sm
                               border border-gray-600 focus:border-brand-500 focus:outline-none"
                    placeholder="tu@correo.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                             text-white font-semibold rounded-lg py-2.5 text-sm transition-colors"
                >
                  {loading ? 'Enviando...' : 'Recuperar contraseña'}
                </button>
              </form>
            </>
          ) : (
            <div className="text-center space-y-4 py-4">
              <CheckCircle size={48} className="text-emerald-400 mx-auto" />
              <h2 className="text-white text-lg font-semibold">Solicitud enviada</h2>
              <p className="text-gray-300 text-sm">{msg}</p>
            </div>
          )}

          <Link
            href="/login"
            className="flex items-center justify-center gap-2 text-sm text-gray-400 hover:text-white transition-colors pt-2"
          >
            <ArrowLeft size={14} />
            Volver al inicio de sesión
          </Link>
        </div>

        <p className="text-center text-xs text-gray-600 mt-6">
          Sonora Digital Corp © {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
