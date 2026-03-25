'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getUser, hasRole, isAuthenticated, type AppRole } from '@/lib/auth'

type AuthGuardProps = {
  children: React.ReactNode
  allowedRoles?: AppRole[]
  fallbackPath?: string
}

export default function AuthGuard({ children, allowedRoles, fallbackPath = '/dashboard' }: AuthGuardProps) {
  const router = useRouter()
  const authenticated = isAuthenticated()
  const user = getUser()
  const authorized = !allowedRoles || allowedRoles.length === 0 || (user ? hasRole(allowedRoles) : false)

  useEffect(() => {
    if (!authenticated) {
      router.replace('/login')
      return
    }

    if (!authorized) {
      router.replace(fallbackPath)
    }
  }, [authenticated, authorized, fallbackPath, router])

  if (!authenticated || !authorized) return null

  return <>{children}</>
}
