'use client'

import { api, LoginResponse } from './api'

export type AppRole = 'admin' | 'ceo' | 'contador' | 'rh' | string

export interface AuthUser {
  id: string
  email: string
  nombre?: string
  tenant_id?: string
  rol?: AppRole
  activo?: boolean
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const data = await api.post<LoginResponse>('/auth/login', { email, password })
  localStorage.setItem('mystic_token', data.access_token)
  localStorage.setItem('mystic_user', JSON.stringify(data.usuario))
  return data
}

export function logout() {
  localStorage.removeItem('mystic_token')
  localStorage.removeItem('mystic_user')
  window.location.href = '/login'
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('mystic_token')
}

export function getUser(): AuthUser | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem('mystic_user')
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthUser
  } catch {
    return null
  }
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  return !!localStorage.getItem('mystic_token')
}

export function hasRole(allowed: AppRole[]): boolean {
  const user = getUser()
  const role = user?.rol || ''
  return allowed.includes(role)
}
