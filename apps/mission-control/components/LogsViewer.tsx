'use client'

import { useEffect, useRef, useState } from 'react'
import { LogEntry } from '@/lib/types'
import { generateMockLogs } from '@/lib/mockdata'
import { motion } from 'framer-motion'
import { AlertCircle, AlertTriangle, Info, Bug } from 'lucide-react'

interface LogsViewerProps {
  logs: LogEntry[] | null
}

export function LogsViewer({ logs: initialLogs }: LogsViewerProps) {
  const [logs, setLogs] = useState<LogEntry[]>(initialLogs || generateMockLogs())
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  useEffect(() => {
    const interval = setInterval(() => {
      setLogs((prev) => {
        const newLog: LogEntry = {
          timestamp: new Date().toISOString(),
          service: [
            'hermes-api',
            'postgres',
            'redis',
            'qdrant',
            'ollama',
          ][Math.floor(Math.random() * 5)],
          level: ['info', 'warn', 'error', 'debug'][
            Math.floor(Math.random() * 4)
          ] as any,
          message: [
            'Request completed successfully',
            'Cache hit',
            'Vector embedding computed',
            'Query executed',
          ][Math.floor(Math.random() * 4)],
        }
        return [newLog, ...prev.slice(0, 49)]
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getLogIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'warn':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'debug':
        return <Bug className="w-4 h-4 text-blue-400" />
      default:
        return <Info className="w-4 h-4 text-accent" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base flex flex-col"
    >
      <h2 className="text-xl font-display font-bold text-light mb-4">
        Live Logs
      </h2>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-2 font-mono text-sm"
      >
        {logs.map((log, idx) => (
          <motion.div
            key={`${log.timestamp}-${idx}`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            className="flex items-start gap-3 p-2 rounded hover:bg-dark-bg/50 transition-colors border border-transparent hover:border-accent/10"
          >
            {getLogIcon(log.level)}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-light/50 text-xs">
                  {new Date(log.timestamp).toLocaleTimeString('es-MX')}
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-semibold ${
                    log.level === 'error'
                      ? 'bg-red-500/20 text-red-400'
                      : log.level === 'warn'
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : log.level === 'debug'
                          ? 'bg-blue-500/20 text-blue-400'
                          : 'bg-accent/20 text-accent'
                  }`}
                >
                  {log.level.toUpperCase()}
                </span>
                <span className="text-light/60">{log.service}</span>
              </div>
              <p className="text-light/70 text-xs mt-1 break-words">
                {log.message}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10 text-xs text-light/50">
        Showing {logs.length} recent logs
      </div>
    </motion.div>
  )
}
