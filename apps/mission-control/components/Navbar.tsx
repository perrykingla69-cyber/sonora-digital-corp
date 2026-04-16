'use client'

import { useEffect, useState } from 'react'
import { RefreshCw, Clock } from 'lucide-react'
import { motion } from 'framer-motion'

interface NavbarProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export function Navbar({ onRefresh, isRefreshing }: NavbarProps) {
  const [time, setTime] = useState<string>('')

  useEffect(() => {
    setTime(new Date().toLocaleTimeString('es-MX'))
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString('es-MX'))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <nav className="sticky top-0 z-50 border-b border-accent/10 bg-primary/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-accent to-secondary flex items-center justify-center">
            <span className="text-primary font-bold text-lg">MC</span>
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xl font-display font-bold gradient-text">
              Mission Control
            </h1>
            <p className="text-xs text-light/50">HERMES OS Monitor</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-light/60">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-mono">{time}</span>
          </div>

          <motion.button
            onClick={onRefresh}
            disabled={isRefreshing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 rounded-lg border border-accent/20 hover:border-accent/50 hover:bg-accent/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw
              className={`w-5 h-5 text-accent ${isRefreshing ? 'animate-spin' : ''}`}
            />
          </motion.button>
        </div>
      </div>
    </nav>
  )
}
