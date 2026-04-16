'use client'
import { useEffect, useState, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import DashboardLayout from '@/components/DashboardLayout'
import BotTable from '@/components/BotTable'
import { listBots, isAuthenticated, type Bot } from '@/lib/api'

export default function BotsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const justCreated = searchParams.get('created')

  const load = useCallback(async () => {
    try {
      const data = await listBots()
      setBots(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al cargar bots')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!isAuthenticated()) { router.replace('/auth/login'); return }
    load()
    // Auto-refresh cada 30s si hay bots creándose
    const interval = setInterval(() => {
      if (bots.some(b => b.status === 'creating' || b.status === 'created')) load()
    }, 30000)
    return () => clearInterval(interval)
  }, [router, load, bots])

  return (
    <DashboardLayout>
      <div>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">Mis bots</h1>
            <p className="text-white/50 mt-1">
              Gestiona y monitorea tus bots activos.
            </p>
          </div>
          <Link href="/dashboard/automation" className="btn-primary text-sm">
            + Nueva automatización
          </Link>
        </div>

        {/* Banner si acaba de crear */}
        <AnimatePresence>
          {justCreated && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-6 p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-sm"
            >
              ✅ Agente creándose en background. Puede tomar 2-3 minutos.
              El estado se actualizará automáticamente.
            </motion.div>
          )}
        </AnimatePresence>

        <div className="glass rounded-2xl overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <div className="animate-spin w-7 h-7 border-2 border-brand-500 border-t-transparent rounded-full" />
            </div>
          ) : error ? (
            <div className="p-6 text-red-400 text-sm">{error}</div>
          ) : (
            <BotTable bots={bots} onRefresh={load} />
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
