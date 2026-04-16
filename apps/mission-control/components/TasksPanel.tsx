'use client'

import { Task } from '@/lib/types'
import { generateMockTasks } from '@/lib/mockdata'
import { motion } from 'framer-motion'
import { CheckCircle2, Clock, AlertCircle, Zap } from 'lucide-react'

interface TasksPanelProps {
  tasks: Task[] | null
}

export function TasksPanel({ tasks: initialTasks }: TasksPanelProps) {
  const mockTasks = generateMockTasks()
  const data = initialTasks || mockTasks

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />
      case 'in_progress':
        return <Zap className="w-5 h-5 text-accent animate-pulse" />
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />
    }
  }

  const statusColors = {
    completed: 'from-green-500/20 to-green-500/10',
    error: 'from-red-500/20 to-red-500/10',
    in_progress: 'from-accent/20 to-accent/10',
    pending: 'from-yellow-500/20 to-yellow-500/10',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base flex flex-col"
    >
      <h2 className="text-xl font-display font-bold text-light mb-4">
        Claude Code Tasks
      </h2>

      <div className="space-y-3 flex-1">
        {data.map((task, idx) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-4 rounded-lg border border-accent/10 bg-gradient-to-r ${
              statusColors[task.status]
            }`}
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex items-start gap-3 flex-1">
                {getStatusIcon(task.status)}
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-light truncate">
                    {task.title}
                  </h3>
                  <p className="text-xs text-light/50">{task.agent}</p>
                </div>
              </div>
              <span
                className={`text-xs font-semibold px-2 py-1 rounded whitespace-nowrap ${
                  task.status === 'completed'
                    ? 'bg-green-500/30 text-green-400'
                    : task.status === 'error'
                      ? 'bg-red-500/30 text-red-400'
                      : task.status === 'in_progress'
                        ? 'bg-accent/30 text-accent'
                        : 'bg-yellow-500/30 text-yellow-400'
                }`}
              >
                {task.progress}%
              </span>
            </div>

            <div className="w-full bg-dark-bg/50 rounded-full h-2 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${task.progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="bg-gradient-to-r from-accent to-secondary h-full"
              />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10">
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div>
            <p className="text-light/60">Total</p>
            <p className="text-lg font-bold text-light">{data.length}</p>
          </div>
          <div>
            <p className="text-light/60">In Progress</p>
            <p className="text-lg font-bold text-accent">
              {data.filter((t) => t.status === 'in_progress').length}
            </p>
          </div>
          <div>
            <p className="text-light/60">Completed</p>
            <p className="text-lg font-bold text-green-400">
              {data.filter((t) => t.status === 'completed').length}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
