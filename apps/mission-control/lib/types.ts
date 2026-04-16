export interface DockerService {
  name: string
  status: 'healthy' | 'unhealthy' | 'starting'
  uptime: number
  memory: number
  cpu: number
}

export interface SystemStatus {
  docker: {
    healthy: number
    total: number
    services: DockerService[]
  }
  api: {
    status: 'online' | 'offline' | 'degraded'
    responseTime: number
    requestsPerMinute: number
  }
  postgresql: {
    status: 'connected' | 'disconnected'
    connections: number
    maxConnections: number
    queryTime: number
  }
  redis: {
    status: 'connected' | 'disconnected'
    memory: number
    keys: number
  }
}

export interface Agent {
  name: string
  model: string
  status: 'idle' | 'running' | 'error'
  lastActivity: string
  tasksCompleted: number
}

export interface MCP {
  name: string
  status: 'active' | 'inactive' | 'error'
  lastCheck: string
}

export interface Task {
  id: string
  title: string
  progress: number
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  agent: string
}

export interface LogEntry {
  timestamp: string
  service: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
}
