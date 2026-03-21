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

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/login')
      return
    }

    if (allowedRoles && allowedRoles.length > 0 && !hasRole(allowedRoles)) {
      router.replace(fallbackPath)
    }
  }, [allowedRoles, fallbackPath, router])

  if (!isAuthenticated()) return null

  if (allowedRoles && allowedRoles.length > 0) {
    const user = getUser()
    if (!user || !hasRole(allowedRoles)) return null
  }

  return <>{children}</>
}
