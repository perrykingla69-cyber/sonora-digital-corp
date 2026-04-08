'use client'

import Link from 'next/link'
import { HermesEyeLogo } from './HermesEyeLogo'

interface NavigationProps {
  showHome?: boolean
}

export function Navigation({ showHome = true }: NavigationProps) {
  return (
    <nav className="relative z-10 flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
      <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
        <HermesEyeLogo size={32} />
        <span className="font-black text-lg tracking-wide text-[#D4AF37]">HERMES</span>
      </Link>
      <div className="flex items-center gap-4">
        {showHome && (
          <Link
            href="/"
            className="text-sm text-white/60 hover:text-white border border-white/20 hover:border-white/40 rounded-lg px-4 py-1.5 transition"
          >
            ← Volver
          </Link>
        )}
        <Link
          href="/login"
          className="text-sm text-white/60 hover:text-white border border-white/20 hover:border-white/40 rounded-lg px-4 py-1.5 transition"
        >
          Iniciar sesión
        </Link>
      </div>
    </nav>
  )
}
