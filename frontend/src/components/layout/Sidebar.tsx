'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, FileText, Users, Calculator,
  Package, CheckSquare, LogOut, Zap,
  MessageCircle, Send, Brain,
} from 'lucide-react'
import { logout, getUser } from '@/lib/auth'
import clsx from 'clsx'

const NAV = [
  { href: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/facturas',   icon: FileText,         label: 'Facturas' },
  { href: '/nomina',     icon: Users,             label: 'Nómina' },
  { href: '/cierre',     icon: Calculator,        label: 'Cierre' },
  { href: '/mve',        icon: Package,           label: 'MVE' },
  { href: '/tasks',      icon: CheckSquare,       label: 'Tareas' },
]

const NAV_CANALES = [
  { href: '/brain',      icon: Brain,             label: 'Brain IA' },
  { href: '/whatsapp',   icon: MessageCircle,     label: 'WhatsApp' },
  { href: '/telegram',   icon: Send,              label: 'Telegram' },
]

export default function Sidebar() {
  const path = usePathname()
  const user = getUser()

  return (
    <aside className="fixed inset-y-0 left-0 w-56 bg-gray-900 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-800">
        <Zap className="text-brand-500" size={22} />
        <span className="text-white font-bold text-lg tracking-tight">Mystic</span>
      </div>

      {/* Nav principal */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-3 pt-1 pb-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">Operación</p>
        {NAV.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              path.startsWith(href)
                ? 'bg-brand-600 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}

        <p className="px-3 pt-4 pb-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">Canales</p>
        {NAV_CANALES.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              path.startsWith(href)
                ? 'bg-brand-600 text-white'
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </nav>

      {/* User + logout */}
      {user && (
        <div className="px-4 py-4 border-t border-gray-800">
          <p className="text-xs text-gray-500 truncate">{user.email}</p>
          <p className="text-xs text-gray-400 font-medium truncate">{user.nombre || user.tenant_id}</p>
          <button
            onClick={logout}
            className="mt-3 flex items-center gap-2 text-xs text-gray-500 hover:text-red-400 transition-colors"
          >
            <LogOut size={14} /> Salir
          </button>
        </div>
      )}
    </aside>
  )
}
