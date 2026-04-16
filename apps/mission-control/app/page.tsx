'use client'

import { useEffect, useState } from 'react'
import { Navbar } from '@/components/Navbar'
import { StatusBoard } from '@/components/StatusBoard'
import { LogsViewer } from '@/components/LogsViewer'
import { TasksPanel } from '@/components/TasksPanel'
import { AgentsMonitor } from '@/components/AgentsMonitor'
import { MCPsStatus } from '@/components/MCPsStatus'
import { CrawbotBridge } from '@/components/CrawbotBridge'
import { SystemStatus, Agent, MCP, Task, LogEntry } from '@/lib/types'
import {
  generateMockSystemStatus,
  generateMockAgents,
  generateMockMCPs,
  generateMockTasks,
  generateMockLogs,
} from '@/lib/mockdata'
import { fetchSystemStatus, fetchAgentStatus, fetchMCPStatus, fetchTasks } from '@/lib/api'
import { motion } from 'framer-motion'

export default function Dashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [agents, setAgents] = useState<Agent[] | null>(null)
  const [mcps, setMCPs] = useState<MCP[] | null>(null)
  const [tasks, setTasks] = useState<Task[] | null>(null)
  const [logs, setLogs] = useState<LogEntry[] | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const loadData = async () => {
    try {
      setIsRefreshing(true)

      const [statusData, agentsData, mcpsData, tasksData] = await Promise.all([
        fetchSystemStatus(),
        fetchAgentStatus(),
        fetchMCPStatus(),
        fetchTasks(),
      ])

      if (statusData) setSystemStatus(statusData)
      if (agentsData) setAgents(agentsData)
      if (mcpsData) setMCPs(mcpsData)
      if (tasksData) setTasks(tasksData)

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadData()

    const interval = setInterval(loadData, 30000)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!systemStatus) setSystemStatus(generateMockSystemStatus())
    if (!agents) setAgents(generateMockAgents())
    if (!mcps) setMCPs(generateMockMCPs())
    if (!tasks) setTasks(generateMockTasks())
    if (!logs) setLogs(generateMockLogs())
  }, [])

  return (
    <div className="min-h-screen bg-primary">
      <Navbar onRefresh={loadData} isRefreshing={isRefreshing} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-h2 font-display font-bold gradient-text">
              System Overview
            </h1>
            <p className="text-sm text-light/60">
              Last updated: {lastUpdate.toLocaleTimeString('es-MX')}
            </p>
          </div>
          <p className="text-light/70">
            Real-time monitoring of HERMES OS infrastructure and agents
          </p>
        </motion.div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Status Board - Full Width on Mobile, 2 cols on larger screens */}
          <div className="lg:col-span-2">
            <StatusBoard status={systemStatus} />
          </div>

          {/* Tasks Panel */}
          <div>
            <TasksPanel tasks={tasks} />
          </div>
        </div>

        {/* Second Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Logs Viewer */}
          <div className="lg:col-span-2">
            <LogsViewer logs={logs} />
          </div>

          {/* MCPs Status */}
          <div>
            <MCPsStatus mcps={mcps} />
          </div>
        </div>

        {/* Third Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agents Monitor */}
          <div>
            <AgentsMonitor agents={agents} />
          </div>

          {/* ClawBot Bridge */}
          <div>
            <CrawbotBridge />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-accent/10 mt-12 py-6 bg-dark-bg/50">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-light/50">
          <p>HERMES OS Mission Control &copy; 2026 Sonora Digital Corp</p>
          <p className="text-xs text-light/30 mt-1">
            Powered by AI orchestration technology
          </p>
        </div>
      </footer>
    </div>
  )
}
