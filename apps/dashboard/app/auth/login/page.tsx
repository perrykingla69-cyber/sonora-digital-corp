'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import AuthLayout from '@/components/AuthLayout'
import { login, setToken } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(form)
      setToken(res.jwt_token, {
        id: res.user_id,
        tenant_id: res.tenant_id,
        tenant_slug: res.tenant_slug,
      })
      router.push('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Bienvenido de vuelta"
      subtitle="Accede a tu panel de automatizaciones"
      footer={
        <>
          ¿No tienes cuenta?{' '}
          <Link href="/auth/signup" className="text-brand-400 hover:text-brand-300 transition-colors">
            Regístrate gratis
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs text-white/50 mb-1.5">Email</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
            placeholder="tu@empresa.com"
            className="input-base"
            required
            autoFocus
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs text-white/50">Contraseña</label>
            <Link href="/auth/forgot-password" className="text-xs text-brand-400 hover:text-brand-300">
              ¿Olvidaste tu contraseña?
            </Link>
          </div>
          <input
            type="password"
            value={form.password}
            onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
            placeholder="Tu contraseña"
            className="input-base"
            required
          />
        </div>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-400 bg-red-500/10 px-3 py-2 rounded-lg"
          >
            {error}
          </motion.p>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
          {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
        </button>
      </form>
    </AuthLayout>
  )
}
