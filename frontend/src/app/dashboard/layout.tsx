'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import clsx from 'clsx'

interface User {
  id: string
  email: string
  nombre: string
  tenant_id: string
  rol: 'admin' | 'user' | 'ceo'
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Verificar autenticación
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('hermes_token')
        if (!token) {
          router.push('/login')
          return
        }

        // En producción: verificar token con backend
        const userData = localStorage.getItem('hermes_user')
        if (userData) {
          setUser(JSON.parse(userData))
        }
      } catch (err) {
        console.error('Auth check failed:', err)
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('hermes_token')
    localStorage.removeItem('hermes_user')
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-sovereign-bg flex items-center justify-center">
        <div className="text-center">
          <p className="text-sovereign-muted">Verificando autenticación...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-sovereign-bg">
      {/* Header Navigation */}
      <nav className="border-b border-sovereign-border bg-sovereign-card sticky top-0 z-50">
        <div className="max-w-full px-4 sm:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            <div>
              <h1 className="text-lg font-bold text-sovereign-gold">HERMES</h1>
              <p className="text-xs text-sovereign-muted">Orquestador IA</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <div className="text-right text-sm">
                <p className="text-sovereign-text font-medium">{user.nombre}</p>
                <p className="text-xs text-sovereign-muted">{user.rol}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-lg bg-sovereign-border/40 hover:bg-sovereign-border/60 text-sovereign-text transition-colors text-sm font-medium"
            >
              Salir
            </button>
          </div>
        </div>
      </nav>

      {/* Breadcrumb */}
      <div className="border-b border-sovereign-border/40 bg-sovereign-card/50">
        <div className="max-w-full px-4 sm:px-8 py-3">
          <nav className="flex items-center gap-2 text-xs text-sovereign-muted">
            <a href="/" className="hover:text-sovereign-text">
              Inicio
            </a>
            <span>/</span>
            <span className="text-sovereign-text font-medium">Dashboard</span>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main>{children}</main>

      {/* Footer */}
      <footer className="border-t border-sovereign-border bg-sovereign-card mt-12 py-6">
        <div className="max-w-full px-4 sm:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-sovereign-muted">
            <p>HERMES © 2026 — Sonora Digital Corp</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-sovereign-text">
                Soporte
              </a>
              <a href="#" className="hover:text-sovereign-text">
                Documentación
              </a>
              <a href="#" className="hover:text-sovereign-text">
                Status
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
