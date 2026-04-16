/**
 * API client para hermes-api
 * Maneja JWT automáticamente desde localStorage
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ── Types ─────────────────────────────────────────────────────

export interface SignupPayload {
  email: string
  password: string
  full_name: string
  company_name: string
}

export interface LoginPayload {
  email: string
  password: string
  tenant_slug?: string
}

export interface AuthResponse {
  user_id: string
  email: string
  jwt_token: string
  tenant_id: string
  tenant_slug: string
}

export interface LoginResponse {
  jwt_token: string
  user_id: string
  tenant_id: string
  tenant_slug: string
}

export interface UserProfile {
  user: {
    id: string
    email: string
    full_name: string
    company_name: string
    subscription_plan: string
    role: string
    is_active: boolean
    created_at: string
  }
  subscription: {
    plan: string
    status: string
    current_period_end: string
  } | null
  bots: Bot[]
}

export interface Agent {
  id: string
  name: string
  description: string
  agent_type: string
  model: string
  status: 'creating' | 'active' | 'failed' | 'destroying' | 'stopped'
  progress: number
  deployment_url?: string
  created_at: string
  updated_at: string
}

export interface CreateAgentPayload {
  name: string
  description: string
  verticales: string[]
  agent_type: string
  channel: string
  config: {
    tone?: string
    language?: string
    integrations?: string[]
  }
}

export interface Bot {
  id: string
  name?: string
  channel: string
  status: string
  webhook_url?: string
  agent_name?: string
  messages_today: number
  uptime_pct: number
  created_at: string
}


// ── Core fetch wrapper ────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    // Token expirado → logout
    if (typeof window !== 'undefined') {
      localStorage.removeItem('jwt_token')
      localStorage.removeItem('user_data')
      window.location.href = '/auth/login'
    }
    throw new Error('Sesión expirada')
  }

  const data = await res.json()

  if (!res.ok) {
    throw new Error(data.detail || data.error || `Error ${res.status}`)
  }

  return data as T
}


// ── Auth ──────────────────────────────────────────────────────

export async function signup(payload: SignupPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/v1/users/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  }, false)
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/api/v1/users/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  }, false)
}

export async function getMe(): Promise<UserProfile> {
  return apiFetch<UserProfile>('/api/v1/users/me')
}

export async function getApiKeys() {
  return apiFetch<{ key: string; created_at: string; last_used: string }[]>(
    '/api/v1/users/me/api-keys'
  )
}

export async function regenerateApiKey() {
  return apiFetch<{ key: string }>('/api/v1/users/me/regenerate-api-key', {
    method: 'POST',
  })
}


// ── Agents ────────────────────────────────────────────────────

export async function createAgent(payload: CreateAgentPayload) {
  return apiFetch<{ agent_id: string; status: string; check_status_url: string }>(
    '/api/v1/agents/create',
    { method: 'POST', body: JSON.stringify(payload) }
  )
}

export async function getAgentStatus(agentId: string) {
  return apiFetch<Agent>(`/api/v1/agents/${agentId}/status`)
}

export async function listAgents(): Promise<Agent[]> {
  return apiFetch<Agent[]>('/api/v1/agents/')
}

export async function deleteAgent(agentId: string) {
  return apiFetch<{ detail: string }>(`/api/v1/agents/${agentId}`, {
    method: 'DELETE',
  })
}


// ── Bots ──────────────────────────────────────────────────────

export async function createBot(payload: { agent_id: string; channel: string; config?: object }) {
  return apiFetch<{
    bot_id: string
    channel: string
    status: string
    webhook_url: string
    instructions: string
  }>('/api/v1/bots/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function listBots(): Promise<Bot[]> {
  return apiFetch<Bot[]>('/api/v1/bots/')
}

export async function getBotHealth(botId: string) {
  return apiFetch<{
    id: string
    status: string
    last_check: string
    uptime: string
    messages_processed_today: number
  }>(`/api/v1/bots/${botId}/health`)
}

export async function deleteBot(botId: string) {
  return apiFetch<{ detail: string }>(`/api/v1/bots/${botId}`, {
    method: 'DELETE',
  })
}


// ── JWT helpers ───────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('jwt_token')
}

export function setToken(token: string, userData?: object): void {
  localStorage.setItem('jwt_token', token)
  if (userData) localStorage.setItem('user_data', JSON.stringify(userData))
}

export function clearToken(): void {
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_data')
}

export function isAuthenticated(): boolean {
  return !!getToken()
}
