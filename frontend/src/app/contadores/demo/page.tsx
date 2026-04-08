'use client'

import { useState } from 'react'
import Link from 'next/link'
import { HermesEyeLogo } from '@/components/landing/HermesEyeLogo'
import { CheckCircle2, ArrowLeft } from 'lucide-react'

export default function DemoPage() {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    empresa: '',
    clientes: '',
  })
  const [enviado, setEnviado] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch('/api/demo-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo: 'contador', ...formData }),
      })
      if (res.ok) {
        setEnviado(true)
        setTimeout(() => {
          window.location.href = '/dashboard'
        }, 2000)
      }
    } catch (err) {
      console.error(err)
    }
  }

  if (enviado) {
    return (
      <div className="relative min-h-screen bg-[#0a0500] text-white flex items-center justify-center px-4">
        <div className="text-center">
          <CheckCircle2 className="w-16 h-16 text-blue-400 mx-auto mb-4" />
          <h1 className="text-3xl font-black mb-2">¡Solicitud recibida!</h1>
          <p className="text-white/60 mb-6">Te contactaremos en 24 horas con acceso a la demo.</p>
          <p className="text-sm text-white/40">Redirigiendo...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen bg-[#0a0500] text-white overflow-x-hidden">
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <Link href="/contadores" className="flex items-center gap-2 hover:opacity-80 transition">
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm font-semibold">Volver</span>
        </Link>
        <div className="flex items-center gap-2">
          <HermesEyeLogo size={32} />
          <span className="font-black text-lg text-blue-400">HERMES</span>
        </div>
      </nav>

      <section className="relative z-10 min-h-[80vh] flex items-center justify-center px-4 py-20">
        <div className="max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-black mb-2">Solicita tu Demo</h1>
            <p className="text-white/60">15 días gratis. Acceso completo. Sin tarjeta.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Nombre</label>
              <input
                type="text"
                name="nombre"
                required
                value={formData.nombre}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
                placeholder="Tu nombre"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Email</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Despacho/Nombre Empresa</label>
              <input
                type="text"
                name="empresa"
                required
                value={formData.empresa}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
                placeholder="Mi Despacho"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">¿Cuántos clientes tienes?</label>
              <select
                name="clientes"
                required
                value={formData.clientes}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              >
                <option value="">Selecciona...</option>
                <option value="1-5">1-5 clientes</option>
                <option value="6-20">6-20 clientes</option>
                <option value="21-50">21-50 clientes</option>
                <option value="51-100">51-100 clientes</option>
                <option value="100+">100+ clientes</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-blue-500 text-white font-bold hover:bg-blue-600 transition mt-6"
            >
              Solicitar Demo
            </button>
          </form>

          <p className="text-xs text-white/30 text-center mt-6">
            Protegemos tu privacidad. Lee nuestra <Link href="/privacidad" className="hover:text-white/60">política de privacidad</Link>.
          </p>
        </div>
      </section>
    </div>
  )
}
