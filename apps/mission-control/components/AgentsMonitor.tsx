'use client'

import { Agent } from '@/lib/types'
import { generateMockAgents } from '@/lib/mockdata'
import { motion } from 'framer-motion'
import { CircleCheck, CircleDot, AlertCircle, Zap } from 'lucide-react'

interface AgentsMonitorProps {
  agents: Agent[] | null
}

export function AgentsMonitor({ agents: initialAgents }: AgentsMonitorProps) {
  const mockAgents = generateMockAgents()
  const data = initialAgents || mockAgents

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'idle':
        return <CircleDot className="w-5 h-5 text-blue-400" />
      case 'running':
        return <Zap className="w-5 h-5 text-accent animate-pulse" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />
      default:
        return <CircleCheck className="w-5 h-5 text-green-400" />
    }
  }

  const statusBg = {
    idle: 'from-blue-500/20 to-blue-500/10',
    running: 'from-accent/20 to-accent/10',
    error: 'from-red-500/20 to-red-500/10',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base"
    >
      <h2 className="text-xl font-display font-bold text-light mb-4">
        Agents Status
      </h2>

      <div className="space-y-3">
        {data.map((agent, idx) => (
          <motion.div
            key={agent.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-4 rounded-lg border border-accent/10 bg-gradient-to-r ${
              statusBg[agent.status]
            }`}
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex items-start gap-3 flex-1">
                {getStatusIcon(agent.status)}
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-light">
                    {agent.name}
                  </h3>
                  <p className="text-xs text-light/50 font-mono">
                    {agent.model}
                  </p>
                </div>
              </div>
              <span
                className={`text-xs font-semibold px-2 py-1 rounded ${
                  agent.status === 'idle'
                    ? 'bg-blue-500/30 text-blue-400'
                    : agent.status === 'running'
                      ? 'bg-accent/30 text-accent'
                      : 'bg-red-500/30 text-red-400'
                }`}
              >
                {agent.status.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex justify-between">
                <span className="text-light/60">Tasks:</span>
                <span className="text-light font-semibold">
                  {agent.tasksCompleted.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-light/60">Last:</span>
                <span className="text-light/70">{agent.lastActivity}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10 text-xs text-light/50">
        <p>
          Active: {data.filter((a) => a.status !== 'error').length} /{' '}
          {data.length}
        </p>
      </div>
    </motion.div>
  )
}
