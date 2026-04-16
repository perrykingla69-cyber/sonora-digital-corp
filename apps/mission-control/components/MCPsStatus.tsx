'use client'

import { MCP } from '@/lib/types'
import { generateMockMCPs } from '@/lib/mockdata'
import { motion } from 'framer-motion'
import { Check, X, AlertCircle } from 'lucide-react'

interface MCPsStatusProps {
  mcps: MCP[] | null
}

export function MCPsStatus({ mcps: initialMCPs }: MCPsStatusProps) {
  const mockMCPs = generateMockMCPs()
  const data = initialMCPs || mockMCPs

  const getStatusIcon = (status: MCP['status']) => {
    switch (status) {
      case 'active':
        return <Check className="w-4 h-4 text-green-400" />
      case 'inactive':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      case 'error':
        return <X className="w-4 h-4 text-red-400" />
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
    }
  }

  const statusColor = {
    active: 'border-green-500/30 bg-green-500/10',
    inactive: 'border-yellow-500/30 bg-yellow-500/10',
    error: 'border-red-500/30 bg-red-500/10',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base"
    >
      <h2 className="text-xl font-display font-bold text-light mb-4">
        MCP Servers
      </h2>

      <div className="grid grid-cols-2 gap-3">
        {data.map((mcp, idx) => (
          <motion.div
            key={mcp.name}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-3 rounded-lg border ${statusColor[mcp.status]}`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2 flex-1">
                {getStatusIcon(mcp.status)}
                <h3 className="text-sm font-semibold text-light">
                  {mcp.name}
                </h3>
              </div>
            </div>

            <div className="text-xs text-light/60">
              {mcp.lastCheck}
            </div>

            <div className="mt-2 pt-2 border-t border-current/10">
              <span
                className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded ${
                  mcp.status === 'active'
                    ? 'bg-green-500/20 text-green-400'
                    : mcp.status === 'inactive'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-red-500/20 text-red-400'
                }`}
              >
                {getStatusIcon(mcp.status)}
                {mcp.status.toUpperCase()}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10">
        <div className="flex justify-between text-xs text-light/60">
          <span>Active: {data.filter((m) => m.status === 'active').length}</span>
          <span>Total: {data.length}</span>
        </div>
      </div>
    </motion.div>
  )
}
