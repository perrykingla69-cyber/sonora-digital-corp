const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.sonoradigitalcorp.com'
const USE_MOCK = !process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_USE_MOCK === 'true'

export async function fetchSystemStatus() {
  try {
    const response = await fetch(`${API_URL}/api/v1/status`, {
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(5000),
    })
    if (!response.ok) throw new Error('API error')
    return await response.json()
  } catch (error) {
    console.warn('Failed to fetch system status, using mock data:', error)
    return {
      docker: { total: 11, healthy: 11 },
      api: { requests_per_minute: 1250, health: 'healthy' },
      postgres: { connections: 28, max: 100, health: 'healthy' },
      redis: { keys: 4832, memory_mb: 145, health: 'healthy' },
      timestamp: new Date().toISOString(),
    }
  }
}

export async function fetchAgentStatus() {
  try {
    const response = await fetch(`${API_URL}/api/v1/agents/status`, {
      signal: AbortSignal.timeout(5000),
    })
    if (!response.ok) throw new Error('API error')
    return await response.json()
  } catch (error) {
    console.warn('Failed to fetch agent status, using mock:', error)
    return [
      { id: 'hermes', status: 'idle', uptime_seconds: 0, ram_mb: 0 },
      { id: 'mystic', status: 'scheduled', next_run: '06:00', ram_mb: 0 },
      { id: 'clawbot', status: 'listening', channels: 4, ram_mb: 250 },
      { id: 'code-agent', status: 'idle', tasks_completed: 3, ram_mb: 0 },
    ]
  }
}

export async function fetchMCPStatus() {
  try {
    const response = await fetch(`${API_URL}/api/v1/mcps/status`, {
      signal: AbortSignal.timeout(5000),
    })
    if (!response.ok) throw new Error('API error')
    return await response.json()
  } catch (error) {
    console.warn('Failed to fetch MCP status, using mock:', error)
    return [
      { name: 'GitHub', status: 'healthy', requests: 1200 },
      { name: 'HuggingFace', status: 'healthy', models_loaded: 2 },
      { name: 'OpenRouter', status: 'healthy', usage_tokens: 124536 },
      { name: 'Qdrant', status: 'healthy', collections: 5 },
      { name: 'Engram', status: 'healthy', observations: 131 },
      { name: 'Evolution API', status: 'healthy', whatsapp_instances: 1 },
    ]
  }
}

export async function fetchTasks() {
  try {
    const response = await fetch(`${API_URL}/api/v1/tasks`, {
      signal: AbortSignal.timeout(5000),
    })
    if (!response.ok) throw new Error('API error')
    return await response.json()
  } catch (error) {
    console.warn('Failed to fetch tasks, using mock:', error)
    return [
      { id: '1', subject: 'Mission Control Dashboard', status: 'completed', progress: 100 },
      { id: '2', subject: 'API Endpoints', status: 'in_progress', progress: 85 },
      { id: '3', subject: 'GitHub CI/CD', status: 'in_progress', progress: 75 },
    ]
  }
}

export async function streamLogs(
  service: string,
  onMessage: (log: any) => void,
  onError: (error: any) => void
) {
  try {
    const eventSource = new EventSource(
      `${API_URL}/api/v1/logs/stream?service=${service}`
    )

    eventSource.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data)
        onMessage(log)
      } catch (e) {
        onError(e)
      }
    }

    eventSource.onerror = (error) => {
      eventSource.close()
      onError(error)
    }

    return () => eventSource.close()
  } catch (error) {
    onError(error)
    return () => {}
  }
}
