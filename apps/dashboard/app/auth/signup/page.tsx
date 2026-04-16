'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import AuthLayout from '@/components/AuthLayout'
import { signup, setToken } from '@/lib/api'

export default function SignupPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    full_name: '',
    company_name: '',
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (form.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres')
      return
    }
    setLoading(true)
    try {
      const res = await signup(form)
      setToken(res.jwt_token, {
        id: res.user_id,
        email: res.email,
        full_name: form.full_name,
        company_name: form.company_name,
        tenant_id: res.tenant_id,
        tenant_slug: res.tenant_slug,
      })
      router.push('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al crear cuenta')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Crear cuenta"
      subtitle="Automatiza tu negocio en minutos"
      footer={
        <>
          ¿Ya tienes cuenta?{' '}
          <Link href="/auth/login" className="text-brand-400 hover:text-brand-300 transition-colors">
            Inicia sesión
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-white/50 mb-1.5">Nombre completo</label>
            <input
              type="text"
              value={form.full_name}
              onChange={e => setForm(p => ({ ...p, full_name: e.target.value }))}
              placeholder="Luis Daniel"
              className="input-base text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-white/50 mb-1.5">Empresa</label>
            <input
              type="text"
              value={form.company_name}
              onChange={e => setForm(p => ({ ...p, company_name: e.target.value }))}
              placeholder="Mi Empresa"
              className="input-base text-sm"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-xs text-white/50 mb-1.5">Email</label>
          <input
            type="email"
            value={form.email}
            onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
            placeholder="tu@empresa.com"
            className="input-base"
            required
          />
        </div>

        <div>
          <label className="block text-xs text-white/50 mb-1.5">Contraseña</label>
          <input
            type="password"
            value={form.password}
            onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
            placeholder="Mínimo 8 caracteres"
            className="input-base"
            required
            minLength={8}
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
          {loading ? 'Creando cuenta...' : 'Crear cuenta gratis'}
        </button>

        <p className="text-xs text-center text-white/30">
          Al registrarte aceptas nuestros{' '}
          <Link href="/legal/terms" className="underline hover:text-white/50">
            Términos de Servicio
          </Link>
        </p>
      </form>
    </AuthLayout>
  )
}
