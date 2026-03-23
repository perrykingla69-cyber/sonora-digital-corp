'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard, FileText, Users, Calculator,
  Package, CheckSquare, LogOut, Zap,
  MessageCircle, Send, Brain, ShieldCheck, CreditCard, Receipt, BookUser, Building2, Menu, GraduationCap,
} from 'lucide-react'
import { logout, getUser } from '@/lib/auth'
import clsx from 'clsx'

// Navegación por rol
const NAV_CONTADOR = [
  { href: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/facturas',   icon: FileText,         label: 'Facturas' },
  { href: '/nomina',     icon: Users,             label: 'Nómina' },
  { href: '/cierre',     icon: Calculator,        label: 'Cierre' },
  { href: '/mve',        icon: Package,           label: 'MVE' },
  { href: '/tasks',      icon: CheckSquare,       label: 'Tareas' },
]

const NAV_CEO = [
  { href: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/facturas',   icon: FileText,         label: 'Facturas' },
  { href: '/nomina',     icon: Users,             label: 'Nómina' },
  { href: '/directorio', icon: Building2,         label: 'Directorio' },
  { href: '/cierre',     icon: Calculator,        label: 'Cierre' },
  { href: '/mve',        icon: Package,           label: 'MVE' },
  { href: '/resico',     icon: Receipt,           label: 'RESICO' },
  { href: '/tasks',      icon: CheckSquare,       label: 'Tareas' },
]

const NAV_ADMIN_PANEL = [
  { href: '/dashboard',  icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/facturas',   icon: FileText,         label: 'Facturas' },
  { href: '/nomina',     icon: Users,             label: 'Nómina' },
  { href: '/directorio', icon: Building2,         label: 'Directorio' },
  { href: '/cierre',     icon: Calculator,        label: 'Cierre' },
  { href: '/mve',        icon: Package,           label: 'MVE' },
  { href: '/resico',     icon: Receipt,           label: 'RESICO' },
  { href: '/contador',   icon: BookUser,          label: 'Mis Clientes' },
  { href: '/tasks',      icon: CheckSquare,       label: 'Tareas' },
]

const NAV_CANALES = [
  { href: '/brain',      icon: Brain,             label: 'Brain IA' },
  { href: '/whatsapp',   icon: MessageCircle,     label: 'WhatsApp' },
  { href: '/telegram',   icon: Send,              label: 'Telegram' },
  { href: '/academy',    icon: GraduationCap,     label: 'Academy' },
]

// Canales solo para ceo/admin
const NAV_SISTEMA = [
  { href: '/admin',      icon: ShieldCheck,       label: 'Admin' },
  { href: '/billing',    icon: CreditCard,        label: 'Suscripción' },
]

const MOBILE_QUICK = [
  { href: '/dashboard', label: 'CEO' },
  { href: '/admin', label: 'Admin' },
  { href: '/contador', label: 'Contadora' },
]

export default function Sidebar() {
  const path = usePathname()
  const user = getUser()
  const rol = user?.rol || 'contador'

  const identity = `${user?.nombre || ''} ${user?.email || ''}`.toLowerCase()
  const isOliviaFourgea = identity.includes('olivia') || identity.includes('fourgea')

  // CEO panel visible para CEO, Admin y Contadora (según solicitud operativa)
  const canSeeCeoPanel = rol === 'ceo' || rol === 'admin' || rol === 'contador' || isOliviaFourgea

  const navPrincipal = rol === 'admin' || isOliviaFourgea
    ? NAV_ADMIN_PANEL
    : rol === 'ceo'
      ? NAV_CEO
      : NAV_CONTADOR

  const mostrarCanales = canSeeCeoPanel
  const mostrarSistema = canSeeCeoPanel

  return (
    <>
      {/* Mobile quick bar */}
      <div className="md:hidden sticky top-0 z-40 bg-gray-900 border-b border-gray-800 px-3 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Menu size={16} className="text-brand-500" />
            <span>Mystic Mobile</span>
          </div>
          <button onClick={logout} className="text-xs text-gray-300">Salir</button>
        </div>
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
          {MOBILE_QUICK.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'text-xs px-3 py-1.5 rounded-full whitespace-nowrap border',
                path.startsWith(item.href)
                  ? 'bg-brand-600 text-white border-brand-500'
                  : 'bg-gray-800 text-gray-200 border-gray-700'
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>

      <aside className="hidden md:flex fixed inset-y-0 left-0 w-56 bg-gray-900 flex-col">
        {/* Logo */}
        <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-800">
          <Zap className="text-brand-500" size={22} />
          <span className="text-white font-bold text-lg tracking-tight">Mystic</span>
        </div>

        {/* Nav principal */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <p className="px-3 pt-1 pb-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">Operación</p>
          {navPrincipal.map(({ href, icon: Icon, label }) => (
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

          {mostrarCanales && (
            <>
              <p className="px-3 pt-4 pb-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">Panel CEO</p>
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
            </>
          )}

          {mostrarSistema && (
            <>
              <p className="px-3 pt-4 pb-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">Sistema</p>
              {NAV_SISTEMA.map(({ href, icon: Icon, label }) => (
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
            </>
          )}
        </nav>

        {/* User + logout */}
        {user && (
          <div className="px-4 py-4 border-t border-gray-800">
            <p className="text-xs text-gray-500 truncate">{user.nombre || user.email}</p>
            <p className="text-xs text-gray-600 truncate">{user.email}</p>
            <span className={clsx(
              'inline-block mt-1 px-2 py-0.5 rounded text-xs font-semibold',
              rol === 'admin' ? 'bg-purple-900 text-purple-300' :
              rol === 'ceo'   ? 'bg-brand-900 text-brand-300' :
                                'bg-gray-800 text-gray-400'
            )}>
              {rol.toUpperCase()}
            </span>
            <button
              onClick={logout}
              className="mt-3 flex items-center gap-2 text-xs text-gray-500 hover:text-red-400 transition-colors"
            >
              <LogOut size={14} /> Salir
            </button>
          </div>
        )}
      </aside>
    </>
  )
}
