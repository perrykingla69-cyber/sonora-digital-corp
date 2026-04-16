'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/DashboardLayout'
import { getMe, listAgents, isAuthenticated, type UserProfile, type Agent } from '@/lib/api'

const QUICK_ACTIONS = [
  { icon: '🤖', label: 'Nueva automatización', href: '/dashboard/automation', desc: 'Crea un nuevo agente IA' },
  { icon: '📡', label: 'Ver mis bots', href: '/dashboard/bots', desc: 'Gestiona tus bots activos' },
  { icon: '⚙️', label: 'Configuración', href: '/dashboard/settings', desc: 'API keys y cuenta' },
  { icon: '💰', label: 'Ver planes', href: '/pricing', desc: 'Escala tu automatización' },
]

const STATUS_LABEL: Record<string, string> = {
  active: 'Activo', creating: 'Creando', failed: 'Error', stopped: 'Pausado',
}

export default function DashboardHome() {
  const router = useRouter()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/auth/login')
      return
    }
    Promise.all([getMe(), listAgents()])
      .then(([p, a]) => { setProfile(p); setAgents(a) })
      .catch(() => router.replace('/auth/login'))
      .finally(() => setLoading(false))
  }, [router])

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
  const firstName = user?.full_name?.split(' ')[0] || 'Usuario'
  const plan = user?.subscription_plan || 'free'
  const activeAgents = agents.filter(a => a.status === 'active').length
  const totalAgents = agents.length

  return (
    <DashboardLayout>
      {/* Welcome */}
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">
            Hola, {firstName} 👋
          </h1>
          <p className="text-white/50 mt-1">
            {user?.company_name} · Plan{' '}
            <span className="capitalize text-brand-400">{plan}</span>
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Agentes activos', value: activeAgents, icon: '🤖' },
            { label: 'Total agentes', value: totalAgents, icon: '📊' },
            { label: 'Bots en línea', value: profile?.bots?.filter(b => b.status === 'active').length ?? 0, icon: '📡' },
            { label: 'Plan actual', value: plan.toUpperCase(), icon: '💎' },
          ].map(stat => (
            <div key={stat.label} className="glass rounded-xl p-4">
              <div className="text-2xl mb-1">{stat.icon}</div>
              <div className="text-xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-white/40 mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Quick actions */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-3">
            Acciones rápidas
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {QUICK_ACTIONS.map((action, i) => (
              <motion.div
                key={action.href}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * i }}
              >
                <Link
                  href={action.href}
                  className="block glass rounded-xl p-4 hover:bg-white/5 transition-all duration-200 group"
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-200">
                    {action.icon}
                  </div>
                  <div className="text-sm font-medium text-white">{action.label}</div>
                  <div className="text-xs text-white/40 mt-0.5">{action.desc}</div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recent agents */}
        {agents.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider">
                Tus agentes
              </h2>
              <Link href="/dashboard/automation" className="text-xs text-brand-400 hover:text-brand-300">
                + Nuevo
              </Link>
            </div>
            <div className="space-y-2">
              {agents.slice(0, 5).map(agent => (
                <div key={agent.id} className="glass rounded-xl p-4 flex items-center gap-4">
                  <div className="text-xl">🤖</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-white truncate">{agent.name}</div>
                    <div className="text-xs text-white/40 truncate">{agent.description}</div>
                  </div>
                  <div className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    agent.status === 'active' ? 'badge-active' :
                    agent.status === 'creating' ? 'badge-creating' :
                    agent.status === 'failed' ? 'badge-failed' : 'badge-stopped'
                  }`}>
                    {STATUS_LABEL[agent.status] || agent.status}
                  </div>
                  {agent.status === 'creating' && (
                    <div className="text-xs text-white/30">{agent.progress}%</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {agents.length === 0 && (
          <div className="text-center py-16 glass rounded-2xl">
            <div className="text-5xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Aún no tienes agentes
            </h3>
            <p className="text-white/40 text-sm mb-6">
              Crea tu primer agente IA en minutos
            </p>
            <Link href="/dashboard/automation" className="btn-primary inline-block">
              Crear primer agente
            </Link>
          </div>
        )}
      </motion.div>
    </DashboardLayout>
  )
}
