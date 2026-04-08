'use client'

import { useState } from 'react'
import Link from 'next/link'
import { HermesEyeLogo } from '@/components/landing/HermesEyeLogo'
import { CheckCircle2, ArrowLeft } from 'lucide-react'

export default function OnboardingPage() {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    artistName: '',
    genero: '',
  })
  const [enviado, setEnviado] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch('/api/artist-signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo: 'artista', ...formData }),
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
          <CheckCircle2 className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h1 className="text-3xl font-black mb-2">¡Bienvenido a HERMES!</h1>
          <p className="text-white/60 mb-6">Tu cuenta está lista. Empieza a subir tu música ahora.</p>
          <p className="text-sm text-white/40">Redirigiendo al panel...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen bg-[#0a0500] text-white overflow-x-hidden">
      <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <Link href="/artistas" className="flex items-center gap-2 hover:opacity-80 transition">
          <ArrowLeft className="w-5 h-5" />
          <span className="text-sm font-semibold">Volver</span>
        </Link>
        <div className="flex items-center gap-2">
          <HermesEyeLogo size={32} />
          <span className="font-black text-lg text-purple-400">HERMES</span>
        </div>
      </nav>

      <section className="relative z-10 min-h-[80vh] flex items-center justify-center px-4 py-20">
        <div className="max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-black mb-2">Crea tu Cuenta</h1>
            <p className="text-white/60">Primer mes gratis. Sube 5 canciones. Sin tarjeta.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Nombre Real</label>
              <input
                type="text"
                name="nombre"
                required
                value={formData.nombre}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                placeholder="Tu nombre completo"
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
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Nombre Artístico</label>
              <input
                type="text"
                name="artistName"
                required
                value={formData.artistName}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
                placeholder="Tu nombre de artista"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Género</label>
              <select
                name="genero"
                required
                value={formData.genero}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400"
              >
                <option value="">Selecciona un género...</option>
                <option value="pop">Pop</option>
                <option value="rock">Rock</option>
                <option value="hip-hop">Hip-Hop/Rap</option>
                <option value="trap">Trap</option>
                <option value="electro">Electrónica</option>
                <option value="reggaeton">Reggaetón</option>
                <option value="regional">Música Regional Mexicana</option>
                <option value="indie">Indie</option>
                <option value="jazz">Jazz</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-purple-500 text-white font-bold hover:bg-purple-600 transition mt-6"
            >
              Crear Cuenta Gratis
            </button>
          </form>

          <p className="text-xs text-white/30 text-center mt-6">
            Al registrarte aceptas nuestros <Link href="/terminos" className="hover:text-white/60">términos de servicio</Link>.
          </p>
        </div>
      </section>
    </div>
  )
}
