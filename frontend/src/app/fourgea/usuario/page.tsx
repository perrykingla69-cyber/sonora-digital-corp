'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { login } from '@/lib/auth'
import { LogIn, Eye, EyeOff } from 'lucide-react'

export default function FourgeaLoginPage() {
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
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 px-4">
      {/* Card */}
      <div className="w-full max-w-sm">

        {/* Logo Fourgea */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4 shadow-lg">
            <span className="text-white font-black text-2xl">F</span>
          </div>
          <h1 className="text-white font-bold text-2xl">Fourgea México</h1>
          <p className="text-blue-300 text-sm mt-1">Portal de Gestión Fiscal</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white/10 backdrop-blur rounded-2xl p-8 space-y-5 border border-white/10 shadow-2xl">

          {error && (
            <div className="bg-red-500/20 border border-red-500/40 text-red-200 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-blue-200 mb-1.5 font-medium">Correo electrónico</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full bg-white/10 text-white rounded-lg px-4 py-2.5 text-sm border border-white/20
                         focus:border-blue-400 focus:outline-none placeholder-white/30"
              placeholder="usuario@fourgea.mx"
            />
          </div>

          <div>
            <label className="block text-sm text-blue-200 mb-1.5 font-medium">Contraseña</label>
            <div className="relative">
              <input
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full bg-white/10 text-white rounded-lg px-4 py-2.5 pr-10 text-sm border border-white/20
                           focus:border-blue-400 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPass(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/70"
              >
                {showPass ? <EyeOff size={16}/> : <Eye size={16}/>}
              </button>
            </div>
          </div>

          {/* Olvidaste contraseña */}
          <div className="text-right">
            <Link href="/forgot-password" className="text-xs text-blue-300 hover:text-blue-100 underline underline-offset-2">
              ¿Olvidaste tu contraseña?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500
                       disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 text-sm
                       transition-all shadow-lg shadow-blue-900/40"
          >
            <LogIn size={16} />
            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>

        <p className="text-center text-xs text-white/20 mt-6">
          Powered by Mystic · Sonora Digital Corp © {new Date().getFullYear()}
        </p>
      </div>
    </div>
  )
}
