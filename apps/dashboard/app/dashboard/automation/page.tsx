'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import DashboardLayout from '@/components/DashboardLayout'
import AutomationForm from '@/components/AutomationForm'
import { isAuthenticated } from '@/lib/api'

export default function AutomationPage() {
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) router.replace('/auth/login')
  }, [router])

  function handleSuccess(agentId: string) {
    // Redirigir a bots con mensaje de éxito
    setTimeout(() => {
      router.push(`/dashboard/bots?created=${agentId}`)
    }, 2500)
  }

  return (
    <DashboardLayout>
      <div className="max-w-2xl">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Nueva automatización</h1>
          <p className="text-white/50 mt-1">
            Describe qué quieres automatizar y te crearemos un agente IA listo para usar.
          </p>
        </div>

        <div className="glass rounded-2xl p-6">
          <AutomationForm onSuccess={handleSuccess} />
        </div>

        {/* Info box */}
        <div className="mt-6 p-4 rounded-xl bg-brand-500/5 border border-brand-500/20">
          <h3 className="text-sm font-semibold text-brand-400 mb-2">¿Cómo funciona?</h3>
          <ol className="text-xs text-white/50 space-y-1 list-decimal list-inside">
            <li>Describes tu automatización en lenguaje natural</li>
            <li>Seleccionamos el modelo IA más adecuado (Gemini/Claude)</li>
            <li>Creamos el agente y lo desplegamos en nuestro VPS</li>
            <li>Conectas el canal (Telegram/WhatsApp) y listo</li>
          </ol>
        </div>
      </div>
    </DashboardLayout>
  )
}
