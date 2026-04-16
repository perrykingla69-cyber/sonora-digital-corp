'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { clearToken } from '@/lib/api'
import clsx from 'clsx'

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Inicio', icon: '⚡' },
  { href: '/dashboard/automation', label: 'Nueva Automatización', icon: '🤖' },
  { href: '/dashboard/bots', label: 'Mis Bots', icon: '📡' },
  { href: '/dashboard/settings', label: 'Configuración', icon: '⚙️' },
]

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userName, setUserName] = useState('')

  useEffect(() => {
    const raw = typeof window !== 'undefined' ? localStorage.getItem('user_data') : null
    if (raw) {
      try {
        const d = JSON.parse(raw)
        setUserName(d.full_name || d.email || 'Usuario')
      } catch {}
    }
  }, [])

  function handleLogout() {
    clearToken()
    router.push('/auth/login')
  }

  const Sidebar = () => (
    <aside className="flex flex-col h-full bg-dark-800 border-r border-white/5 w-64">
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold">S</span>
          </div>
          <div>
            <div className="text-sm font-semibold text-white">Sonora Digital</div>
            <div className="text-xs text-white/40">Dashboard</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(item => (
          <Link
            key={item.href}
            href={item.href}
            onClick={() => setSidebarOpen(false)}
            className={clsx(
              'flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all duration-200',
              pathname === item.href
                ? 'bg-brand-500/20 text-brand-400 font-medium'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            )}
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      {/* User + logout */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-full bg-brand-500/30 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-brand-400">
                {userName.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="text-xs text-white/60 truncate">{userName}</span>
          </div>
          <button
            onClick={handleLogout}
            className="text-xs text-white/30 hover:text-red-400 transition-colors ml-2"
            title="Cerrar sesión"
          >
            Salir
          </button>
        </div>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen bg-dark-950 overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: -264 }}
              animate={{ x: 0 }}
              exit={{ x: -264 }}
              transition={{ type: 'tween', duration: 0.2 }}
              className="fixed left-0 top-0 h-full z-50 lg:hidden"
            >
              <Sidebar />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="flex-shrink-0 flex items-center justify-between h-16 px-6 border-b border-white/5 bg-dark-900/50">
          <button
            className="lg:hidden text-white/60 hover:text-white"
            onClick={() => setSidebarOpen(true)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="text-sm text-white/40 lg:hidden">Sonora Digital</div>
          <div />
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}
