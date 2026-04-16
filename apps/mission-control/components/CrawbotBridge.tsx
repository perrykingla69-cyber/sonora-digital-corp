'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, MessageCircle, Copy, Check } from 'lucide-react'

interface Command {
  label: string
  command: string
  description: string
}

export function CrawbotBridge() {
  const [selectedCmd, setSelectedCmd] = useState<string>('/status')
  const [copied, setCopied] = useState(false)

  const commands: Command[] = [
    {
      label: 'Status',
      command: '/status',
      description: 'System health check',
    },
    {
      label: 'Tasks',
      command: '/tasks',
      description: 'List active tasks',
    },
    {
      label: 'Logs',
      command: '/logs hermes-api',
      description: 'View API logs',
    },
    {
      label: 'Deploy',
      command: '/deploy',
      description: 'Trigger deploy',
    },
  ]

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-base"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-secondary flex items-center justify-center">
          <MessageCircle className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-display font-bold text-light">
            ClawBot Bridge
          </h2>
          <p className="text-xs text-light/50">Send Telegram commands</p>
        </div>
      </div>

      <div className="space-y-3">
        {commands.map((cmd, idx) => (
          <motion.div
            key={cmd.command}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            onClick={() => setSelectedCmd(cmd.command)}
            className={`p-3 rounded-lg border transition-all cursor-pointer ${
              selectedCmd === cmd.command
                ? 'border-accent/50 bg-accent/10'
                : 'border-accent/10 bg-dark-bg/50 hover:border-accent/30'
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <h3 className="font-semibold text-sm text-light">
                {cmd.label}
              </h3>
              {selectedCmd === cmd.command && (
                <div className="w-2 h-2 rounded-full bg-accent mt-1" />
              )}
            </div>
            <p className="text-xs text-light/50 mb-2">{cmd.description}</p>
            <code className="text-xs text-accent font-mono bg-dark-bg rounded px-2 py-1">
              {cmd.command}
            </code>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10 space-y-3">
        <div className="p-3 rounded-lg bg-dark-bg/50 border border-accent/10">
          <p className="text-xs text-light/60 mb-2">Selected command:</p>
          <div className="flex items-center gap-2">
            <code className="text-sm text-accent font-mono flex-1 break-all">
              {selectedCmd}
            </code>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleCopy(selectedCmd)}
              className="p-2 rounded hover:bg-accent/10 transition-colors"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-400" />
              ) : (
                <Copy className="w-4 h-4 text-accent" />
              )}
            </motion.button>
          </div>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full px-4 py-2 rounded-lg bg-gradient-to-r from-accent to-secondary text-primary font-semibold flex items-center justify-center gap-2 hover:shadow-glow transition-all"
        >
          <Send className="w-4 h-4" />
          Execute in Telegram
        </motion.button>
      </div>

      <div className="mt-4 pt-4 border-t border-accent/10 text-xs text-light/50">
        <p>Connected to ClawBot CEO channel</p>
        <p className="text-light/40">@hermes_os_ceo</p>
      </div>
    </motion.div>
  )
}
