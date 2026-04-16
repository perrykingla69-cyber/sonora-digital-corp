const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://vps.hermes.local:8000'

export async function fetchSystemStatus() {
  try {
    const response = await fetch(`${API_URL}/api/v1/status`, {
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(5000),
    })
    if (!response.ok) throw new Error('API error')
    return await response.json()
  } catch (error) {
    console.warn('Failed to fetch system status:', error)
    return null
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
    console.warn('Failed to fetch agent status:', error)
    return null
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
    console.warn('Failed to fetch MCP status:', error)
    return null
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
    console.warn('Failed to fetch tasks:', error)
    return null
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
