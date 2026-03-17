'use client'

import { api, LoginResponse } from './api'

export async function login(email: string, password: string): Promise<LoginResponse> {
  const data = await api.post<LoginResponse>('/auth/login', { email, password })
  localStorage.setItem('mystic_token', data.access_token)
  localStorage.setItem('mystic_user', JSON.stringify(data.user))
  return data
}

export function logout() {
  localStorage.removeItem('mystic_token')
  localStorage.removeItem('mystic_user')
  window.location.href = '/login'
}

export function getUser() {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem('mystic_user')
  return raw ? JSON.parse(raw) : null
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  return !!localStorage.getItem('mystic_token')
}
