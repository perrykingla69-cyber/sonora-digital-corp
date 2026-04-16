import { SystemStatus, Agent, MCP, Task, LogEntry } from './types'

export function generateMockSystemStatus(): SystemStatus {
  return {
    docker: {
      healthy: 10,
      total: 11,
      services: [
        { name: 'postgres', status: 'healthy', uptime: 245000, memory: 512, cpu: 12 },
        { name: 'redis', status: 'healthy', uptime: 245000, memory: 128, cpu: 5 },
        { name: 'qdrant', status: 'healthy', uptime: 245000, memory: 2048, cpu: 22 },
        { name: 'ollama', status: 'healthy', uptime: 245000, memory: 4096, cpu: 45 },
        { name: 'evolution', status: 'healthy', uptime: 245000, memory: 512, cpu: 8 },
        { name: 'n8n', status: 'healthy', uptime: 245000, memory: 256, cpu: 15 },
        { name: 'hermes-api', status: 'healthy', uptime: 245000, memory: 512, cpu: 18 },
        { name: 'hermes-agent', status: 'healthy', uptime: 245000, memory: 256, cpu: 10 },
        { name: 'mystic-agent', status: 'healthy', uptime: 245000, memory: 256, cpu: 8 },
        { name: 'clawbot', status: 'healthy', uptime: 245000, memory: 256, cpu: 12 },
        { name: 'nginx', status: 'unhealthy', uptime: 105000, memory: 64, cpu: 2 },
      ],
    },
    api: {
      status: 'online',
      responseTime: 142,
      requestsPerMinute: 1250,
    },
    postgresql: {
      status: 'connected',
      connections: 28,
      maxConnections: 100,
      queryTime: 45,
    },
    redis: {
      status: 'connected',
      memory: 256,
      keys: 4832,
    },
  }
}

export function generateMockAgents(): Agent[] {
  return [
    {
      name: 'HERMES',
      model: 'google/gemini-2.0-flash-001',
      status: 'idle',
      lastActivity: '2 mins ago',
      tasksCompleted: 1248,
    },
    {
      name: 'MYSTIC',
      model: 'thudm/glm-z1-rumination:free',
      status: 'running',
      lastActivity: 'now',
      tasksCompleted: 642,
    },
    {
      name: 'ClawBot',
      model: 'router',
      status: 'idle',
      lastActivity: '30 secs ago',
      tasksCompleted: 3421,
    },
    {
      name: 'Claude Code',
      model: 'haiku-4.5',
      status: 'running',
      lastActivity: 'now',
      tasksCompleted: 127,
    },
  ]
}

export function generateMockMCPs(): MCP[] {
  return [
    { name: 'GitHub', status: 'active', lastCheck: '30s ago' },
    { name: 'HuggingFace', status: 'active', lastCheck: '45s ago' },
    { name: 'OpenRouter', status: 'active', lastCheck: '15s ago' },
    { name: 'Qdrant', status: 'active', lastCheck: '20s ago' },
    { name: 'Engram', status: 'active', lastCheck: '10s ago' },
    { name: 'Filesystem', status: 'active', lastCheck: '5s ago' },
  ]
}

export function generateMockTasks(): Task[] {
  return [
    {
      id: '1',
      title: 'Create Mission Control dashboard',
      progress: 85,
      status: 'in_progress',
      agent: 'Claude Code',
    },
    {
      id: '2',
      title: 'Optimize RAG embeddings',
      progress: 100,
      status: 'completed',
      agent: 'HERMES',
    },
    {
      id: '3',
      title: 'Analyze tenant patterns',
      progress: 60,
      status: 'in_progress',
      agent: 'MYSTIC',
    },
    {
      id: '4',
      title: 'Process WhatsApp queue',
      progress: 100,
      status: 'completed',
      agent: 'ClawBot',
    },
  ]
}

export function generateMockLogs(): LogEntry[] {
  const services = ['hermes-api', 'postgres', 'redis', 'qdrant', 'ollama', 'n8n']
  const messages = [
    'Request completed successfully',
    'Cache hit ratio: 92%',
    'Vector embedding computed (768-dim)',
    'Workflow triggered by webhook',
    'Query execution time: 45ms',
    'JWT token validated',
  ]

  return Array.from({ length: 20 }, (_, i) => ({
    timestamp: new Date(Date.now() - i * 5000).toISOString(),
    service: services[Math.floor(Math.random() * services.length)],
    level: ['info', 'warn', 'error', 'debug'][Math.floor(Math.random() * 4)] as any,
    message: messages[Math.floor(Math.random() * messages.length)],
  }))
}
