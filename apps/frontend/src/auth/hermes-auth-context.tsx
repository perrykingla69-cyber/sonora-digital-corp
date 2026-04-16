import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { hermes } from '../api/hermes'

export interface AuthUser {
  id: string
  email: string
  name: string
  tenant_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  plan?: string
  avatar_url?: string
}

interface AuthContextType {
  user: AuthUser | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Cargar usuario al montar
  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('hermes_access_token')
        if (!token) {
          setIsLoading(false)
          return
        }

        const profile = await hermes.users.getProfile()
        setUser({
          id: profile.id,
          email: profile.email,
          name: profile.name || profile.email,
          tenant_id: localStorage.getItem('hermes_tenant_id') || '',
          role: profile.role || 'member',
          plan: profile.plan,
          avatar_url: profile.avatar_url,
        })
      } catch (error) {
        console.error('Failed to load user profile:', error)
        localStorage.removeItem('hermes_access_token')
        localStorage.removeItem('hermes_refresh_token')
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const data = await hermes.auth.login(email, password)
      setUser({
        id: data.user_id,
        email: data.email,
        name: data.name || email,
        tenant_id: data.tenant_id,
        role: data.role || 'member',
        plan: data.plan,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await hermes.auth.logout()
      setUser(null)
    } catch (error) {
      console.error('Logout error:', error)
      // Even if API call fails, clear local state
      setUser(null)
      localStorage.removeItem('hermes_access_token')
      localStorage.removeItem('hermes_refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  const refresh = async () => {
    try {
      await hermes.auth.refresh()
      // Recargar perfil
      const profile = await hermes.users.getProfile()
      setUser((prev) =>
        prev ? { ...prev, plan: profile.plan } : null
      )
    } catch (error) {
      console.error('Refresh error:', error)
      logout()
    }
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: user !== null,
    login,
    logout,
    refresh,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Hook para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// HOC para proteger rutas
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return (props: P) => {
    const { isAuthenticated, isLoading } = useAuth()

    if (isLoading) {
      return <div>Cargando...</div>
    }

    if (!isAuthenticated) {
      window.location.href = '/login'
      return null
    }

    return <Component {...props} />
  }
}
