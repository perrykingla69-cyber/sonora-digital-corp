'use client'

import { useEffect, useState } from 'react'
import { SystemStatus } from '@/lib/types'
import { generateMockSystemStatus } from '@/lib/mockdata'
import { motion } from 'framer-motion'
import { Server, Database, Zap, Activity } from 'lucide-react'

interface StatusBoardProps {
  status: SystemStatus | null
}

export function StatusBoard({ status }: StatusBoardProps) {
  const mockStatus = generateMockSystemStatus()
  const data = status || mockStatus

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base space-y-6"
    >
      <h2 className="text-xl font-display font-bold text-light">
        System Status
      </h2>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {/* Docker */}
        <div className="p-4 rounded-lg bg-dark-bg/50 border border-accent/10 hover:border-accent/30 transition-colors">
          <div className="flex items-start justify-between mb-3">
            <Server className="w-5 h-5 text-accent" />
            <span className="text-xs font-semibold bg-green-500/20 text-green-400 px-2 py-1 rounded">
              OK
            </span>
          </div>
          <p className="text-xs text-light/60 mb-1">Docker</p>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-light">
              {data.docker.healthy}
            </span>
            <span className="text-xs text-light/50">/ {data.docker.total}</span>
          </div>
          <div className="w-full bg-dark-bg/50 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-accent to-secondary h-full"
              style={{
                width: `${(data.docker.healthy / data.docker.total) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* API */}
        <div className="p-4 rounded-lg bg-dark-bg/50 border border-accent/10 hover:border-accent/30 transition-colors">
          <div className="flex items-start justify-between mb-3">
            <Zap className="w-5 h-5 text-accent" />
            <span className="text-xs font-semibold bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
              {data.api.responseTime}ms
            </span>
          </div>
          <p className="text-xs text-light/60 mb-1">API</p>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-light">
              {(data.api.requestsPerMinute / 1000).toFixed(1)}k
            </span>
            <span className="text-xs text-light/50">req/min</span>
          </div>
          <div className="text-xs text-green-400 mt-2">Online</div>
        </div>

        {/* PostgreSQL */}
        <div className="p-4 rounded-lg bg-dark-bg/50 border border-accent/10 hover:border-accent/30 transition-colors">
          <div className="flex items-start justify-between mb-3">
            <Database className="w-5 h-5 text-accent" />
            <span className="text-xs font-semibold bg-green-500/20 text-green-400 px-2 py-1 rounded">
              {data.postgresql.queryTime}ms
            </span>
          </div>
          <p className="text-xs text-light/60 mb-1">PostgreSQL</p>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-light">
              {data.postgresql.connections}
            </span>
            <span className="text-xs text-light/50">
              / {data.postgresql.maxConnections}
            </span>
          </div>
          <div className="w-full bg-dark-bg/50 rounded-full h-1.5 mt-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-secondary to-accent h-full"
              style={{
                width: `${(data.postgresql.connections / data.postgresql.maxConnections) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Redis */}
        <div className="p-4 rounded-lg bg-dark-bg/50 border border-accent/10 hover:border-accent/30 transition-colors">
          <div className="flex items-start justify-between mb-3">
            <Activity className="w-5 h-5 text-accent" />
            <span className="text-xs font-semibold bg-purple-500/20 text-purple-400 px-2 py-1 rounded">
              {data.redis.keys}
            </span>
          </div>
          <p className="text-xs text-light/60 mb-1">Redis</p>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-light">
              {(data.redis.memory / 1024).toFixed(1)}
            </span>
            <span className="text-xs text-light/50">GB</span>
          </div>
          <div className="text-xs text-light/40 mt-2">
            Keys: {data.redis.keys.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Services Detail */}
      <div className="space-y-2">
        <h3 className="text-xs font-semibold text-light/60 uppercase tracking-wider">
          Service Health
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-32 overflow-y-auto">
          {data.docker.services.map((service) => (
            <div
              key={service.name}
              className="flex items-center gap-2 px-3 py-2 rounded bg-dark-bg/50 border border-accent/5"
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  service.status === 'healthy'
                    ? 'bg-green-500'
                    : service.status === 'starting'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                }`}
              />
              <span className="text-xs text-light/70">{service.name}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
