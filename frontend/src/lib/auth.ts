'use client'

import { api, LoginResponse } from './api'

export async function login(email: string, password: string): Promise<LoginResponse> {
  const data = await api.post<LoginResponse>('/auth/login', { email, password })
  localStorage.setItem('hermes_token', data.access_token)
  localStorage.setItem('hermes_user', JSON.stringify(data.usuario))
  return data
}

export function logout() {
  localStorage.removeItem('hermes_token')
  localStorage.removeItem('hermes_user')
  window.location.href = '/login'
}

export function getUser() {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem('hermes_user')
  return raw ? JSON.parse(raw) : null
}

export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  return !!localStorage.getItem('hermes_token')
}
