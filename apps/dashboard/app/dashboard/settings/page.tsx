'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/DashboardLayout'
import { getMe, getApiKeys, regenerateApiKey, isAuthenticated, type UserProfile } from '@/lib/api'

export default function SettingsPage() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(true)
  const [regenLoading, setRegenLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/auth/login'); return }
    Promise.all([getMe(), getApiKeys()])
      .then(([p, keys]) => {
        setProfile(p)
        if (keys.length > 0) setApiKey(keys[0].key)
      })
      .finally(() => setLoading(false))
  }, [router])

  async function handleRegenKey() {
    if (!confirm('¿Regenerar tu API key? La anterior dejará de funcionar.')) return
    setRegenLoading(true)
    try {
      const res = await regenerateApiKey()
      setApiKey(res.key)
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error al regenerar')
    } finally {
      setRegenLoading(false)
    }
  }

  function copyKey() {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full" />
        </div>
      </DashboardLayout>
    )
  }

  const user = profile?.user

  return (
    <DashboardLayout>
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Configuración</h1>
          <p className="text-white/50 mt-1">Gestiona tu cuenta y credenciales.</p>
        </div>

        <div className="max-w-2xl space-y-6">
          {/* Perfil */}
          <section className="glass rounded-2xl p-6">
            <h2 className="text-base font-semibold text-white mb-4">Perfil</h2>
            <dl className="space-y-3">
              {[
                { label: 'Nombre', value: user?.full_name },
                { label: 'Empresa', value: user?.company_name },
                { label: 'Email', value: user?.email },
                { label: 'Plan', value: user?.subscription_plan?.toUpperCase() },
                { label: 'Rol', value: user?.role },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                  <dt className="text-sm text-white/40">{item.label}</dt>
                  <dd className="text-sm text-white font-medium">{item.value || '—'}</dd>
                </div>
              ))}
            </dl>
          </section>

          {/* API Keys */}
          <section className="glass rounded-2xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">API Key</h2>
            <p className="text-xs text-white/40 mb-4">
              Úsala para integrar Sonora Digital con tus sistemas externos.
            </p>

            {apiKey ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <code className="flex-1 text-xs font-mono bg-dark-950 border border-white/10 rounded-lg px-3 py-2.5 text-white/70 truncate">
                    {apiKey}
                  </code>
                  <button
                    onClick={copyKey}
                    className="btn-secondary text-xs px-3 py-2 flex-shrink-0"
                  >
                    {copied ? '✓ Copiado' : 'Copiar'}
                  </button>
                </div>
                <button
                  onClick={handleRegenKey}
                  disabled={regenLoading}
                  className="text-xs text-white/30 hover:text-yellow-400 transition-colors"
                >
                  {regenLoading ? 'Regenerando...' : '↻ Regenerar key'}
                </button>
              </div>
            ) : (
              <p className="text-sm text-white/30">No tienes una API key activa.</p>
            )}
          </section>

          {/* Suscripción */}
          {profile?.subscription && (
            <section className="glass rounded-2xl p-6">
              <h2 className="text-base font-semibold text-white mb-4">Suscripción</h2>
              <dl className="space-y-2">
                <div className="flex justify-between py-2 border-b border-white/5">
                  <dt className="text-sm text-white/40">Plan</dt>
                  <dd className="text-sm text-white font-medium capitalize">{profile.subscription.plan}</dd>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <dt className="text-sm text-white/40">Estado</dt>
                  <dd className="text-sm text-green-400 font-medium">{profile.subscription.status}</dd>
                </div>
                <div className="flex justify-between py-2">
                  <dt className="text-sm text-white/40">Vence</dt>
                  <dd className="text-sm text-white">{profile.subscription.current_period_end}</dd>
                </div>
              </dl>
              <p className="mt-4 text-xs text-white/30">
                Para cambiar de plan, escríbenos a{' '}
                <a href="mailto:sonoradigitalcorp@gmail.com" className="text-brand-400">
                  sonoradigitalcorp@gmail.com
                </a>
              </p>
            </section>
          )}

          {/* Danger zone */}
          <section className="rounded-2xl p-6 border border-red-500/20 bg-red-500/5">
            <h2 className="text-base font-semibold text-red-400 mb-1">Zona de peligro</h2>
            <p className="text-xs text-white/40 mb-4">
              Las siguientes acciones son irreversibles.
            </p>
            <button
              onClick={() => alert('Para eliminar tu cuenta, escríbenos a sonoradigitalcorp@gmail.com')}
              className="text-sm text-red-400/70 hover:text-red-400 border border-red-500/20 px-4 py-2 rounded-lg transition-colors"
            >
              Eliminar cuenta
            </button>
          </section>
        </div>
      </motion.div>
    </DashboardLayout>
  )
}
