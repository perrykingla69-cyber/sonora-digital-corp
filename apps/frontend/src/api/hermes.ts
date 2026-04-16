/**
 * HERMES API Adapter
 * Mapea endpoints REST de FastAPI a interfaz tRPC-like
 *
 * Usage:
 *   const profile = await hermes.users.getProfile()
 *   const chats = await hermes.conversations.getList()
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Fetch wrapper con autenticación JWT
async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem('hermes_access_token')

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (response.status === 401) {
    // Token expirado - intentar refresh
    await refreshToken()
    return apiFetch(path, options) // Reintentar
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Refresh JWT token
async function refreshToken() {
  const refreshToken = localStorage.getItem('hermes_refresh_token')
  if (!refreshToken) {
    throw new Error('No refresh token available')
  }

  const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })

  if (!response.ok) {
    localStorage.removeItem('hermes_access_token')
    localStorage.removeItem('hermes_refresh_token')
    window.location.href = '/login'
    throw new Error('Refresh failed')
  }

  const data = await response.json()
  localStorage.setItem('hermes_access_token', data.access_token)
  if (data.refresh_token) {
    localStorage.setItem('hermes_refresh_token', data.refresh_token)
  }
}

// API Schema
export const hermes = {
  // Auth
  auth: {
    login: async (email: string, password: string) => {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail)
      }

      const data = await response.json()
      localStorage.setItem('hermes_access_token', data.access_token)
      localStorage.setItem('hermes_refresh_token', data.refresh_token)
      localStorage.setItem('hermes_user_id', data.user_id)
      localStorage.setItem('hermes_tenant_id', data.tenant_id)
      return data
    },

    logout: async () => {
      try {
        await apiFetch('/api/v1/auth/logout', { method: 'POST' })
      } finally {
        localStorage.removeItem('hermes_access_token')
        localStorage.removeItem('hermes_refresh_token')
        localStorage.removeItem('hermes_user_id')
        localStorage.removeItem('hermes_tenant_id')
      }
    },

    refresh: refreshToken,
  },

  // Users
  users: {
    getProfile: async () => {
      return apiFetch('/api/v1/users/profile')
    },

    updateProfile: async (payload: Record<string, any>) => {
      return apiFetch('/api/v1/users/profile', {
        method: 'PUT',
        body: JSON.stringify(payload),
      })
    },

    getPublicProfile: async (slug: string) => {
      return apiFetch(`/api/v1/users/profile/${slug}`)
    },
  },

  // Conversations
  conversations: {
    getList: async (limit = 50, offset = 0) => {
      return apiFetch(`/api/v1/conversations?limit=${limit}&offset=${offset}`)
    },

    getOne: async (conversationId: string) => {
      return apiFetch(`/api/v1/conversations/${conversationId}`)
    },

    create: async (payload: { name: string; agent: 'hermes' | 'mystic' }) => {
      return apiFetch('/api/v1/conversations', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },

    getMessages: async (conversationId: string, limit = 100) => {
      return apiFetch(`/api/v1/conversations/${conversationId}/messages?limit=${limit}`)
    },

    sendMessage: async (conversationId: string, content: string) => {
      return apiFetch(`/api/v1/conversations/${conversationId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content }),
      })
    },
  },

  // Agents (HERMES / MYSTIC chat)
  agents: {
    chat: async (agentType: 'hermes' | 'mystic', message: string, conversationId?: string) => {
      return apiFetch(`/api/v1/agents/${agentType}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message, conversation_id: conversationId }),
      })
    },

    getStatus: async () => {
      return apiFetch('/api/v1/agents/status')
    },
  },

  // Documents
  documents: {
    getList: async (limit = 50) => {
      return apiFetch(`/api/v1/documents?limit=${limit}`)
    },

    upload: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      const token = localStorage.getItem('hermes_access_token')
      const headers: HeadersInit = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
        method: 'POST',
        headers,
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      return response.json()
    },

    delete: async (documentId: string) => {
      return apiFetch(`/api/v1/documents/${documentId}`, {
        method: 'DELETE',
      })
    },
  },

  // Content Generation
  content: {
    generateImage: async (prompt: string, style?: string) => {
      return apiFetch('/api/v1/content/generate-image', {
        method: 'POST',
        body: JSON.stringify({ prompt, style }),
      })
    },

    generateVideo: async (topic: string) => {
      return apiFetch('/api/v1/content/generate-video', {
        method: 'POST',
        body: JSON.stringify({ topic }),
      })
    },

    generateText: async (topic: string, format: string) => {
      return apiFetch('/api/v1/content/generate-text', {
        method: 'POST',
        body: JSON.stringify({ topic, format }),
      })
    },
  },

  // Tenants
  tenants: {
    getCurrent: async () => {
      return apiFetch('/api/v1/tenants/current')
    },

    getMetrics: async () => {
      return apiFetch('/api/v1/tenants/current/metrics')
    },
  },
}

// Type exports para TypeScript
export type HermesAPI = typeof hermes
