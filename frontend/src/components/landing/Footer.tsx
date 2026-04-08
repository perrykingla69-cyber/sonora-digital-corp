'use client'

import Link from 'next/link'
import { HermesEyeLogo } from './HermesEyeLogo'

export function Footer() {
  return (
    <footer className="relative z-10 text-center py-12 px-4 border-t border-white/5">
      <div className="flex items-center justify-center gap-2 mb-4">
        <HermesEyeLogo size={24} />
        <span className="font-black text-[#D4AF37]">HERMES</span>
      </div>
      <p className="text-sm text-white/40 mb-6">
        © 2026 Sonora Digital Corp · Hermosillo, Sonora, México
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 text-xs text-white/30">
        <Link href="/privacidad" className="hover:text-white/60 transition">
          Privacidad
        </Link>
        <Link href="/terminos" className="hover:text-white/60 transition">
          Términos
        </Link>
        <Link href="/" className="hover:text-white/60 transition">
          Inicio
        </Link>
        <Link href="/login" className="hover:text-white/60 transition">
          Iniciar sesión
        </Link>
      </div>
    </footer>
  )
}
