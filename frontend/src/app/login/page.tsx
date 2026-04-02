'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { login } from '@/lib/auth'
import { Zap, Eye, EyeOff, Loader2 } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      router.push('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Credenciales incorrectas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sovereign-bg relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-sovereign-gold/5 blur-3xl" />
        <div className="absolute top-1/4 right-1/4 w-64 h-64 rounded-full bg-sovereign-gold/3 blur-3xl" />
      </div>

      <div className="w-full max-w-sm relative z-10">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <div className="w-10 h-10 rounded-full bg-sovereign-gold flex items-center justify-center gold-glow">
            <Zap size={20} className="text-sovereign-bg" />
          </div>
          <div>
            <span className="text-sovereign-text font-bold text-2xl tracking-tight">Hermes</span>
            <span className="block text-xs text-sovereign-muted tracking-widest uppercase">Sovereign System</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 space-y-5">
          <h1 className="text-sovereign-text text-lg font-semibold text-center">
            Acceso al Nodo
          </h1>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs text-sovereign-muted mb-2 uppercase tracking-wider">Correo</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="sovereign-input w-full"
              placeholder="tu@correo.com"
            />
          </div>

          <div>
            <label className="block text-xs text-sovereign-muted mb-2 uppercase tracking-wider">Contraseña</label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="sovereign-input w-full pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPass(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sovereign-muted hover:text-sovereign-text transition-colors"
              >
                {showPass ? <EyeOff size={15}/> : <Eye size={15}/>}
              </button>
            </div>
          </div>

          <div className="text-right -mt-2">
            <Link href="/forgot-password" className="text-xs text-sovereign-gold/70 hover:text-sovereign-gold transition-colors">
              ¿Olvidaste tu contraseña?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-sovereign-gold hover:opacity-90 disabled:opacity-50
                       text-sovereign-bg font-semibold rounded-xl py-3 text-sm transition-all
                       flex items-center justify-center gap-2 gold-glow"
          >
            {loading ? (
              <><Loader2 size={15} className="animate-spin" /> Autenticando...</>
            ) : (
              'Acceder'
            )}
          </button>
        </form>

        <p className="text-center text-xs text-sovereign-muted/50 mt-8">
          Sonora Digital Corp © {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
