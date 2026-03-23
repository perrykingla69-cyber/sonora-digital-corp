"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, CheckCircle, Info, X } from "lucide-react";
import { useState } from "react";

interface Alert {
  id: string;
  type: "critical" | "warning" | "info";
  title: string;
  message: string;
  action?: string;
  autoFix?: boolean;
}

export function SmartAlerts({ alerts }: { alerts: Alert[] }) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const icons = {
    critical: <AlertTriangle className="h-5 w-5 text-rose-500" />,
    warning: <AlertTriangle className="h-5 w-5 text-amber-500" />,
    info: <Info className="h-5 w-5 text-cyan-500" />
  };

  const colors = {
    critical: "border-rose-500/30 bg-rose-500/10",
    warning: "border-amber-500/30 bg-amber-500/10",
    info: "border-cyan-500/30 bg-cyan-500/10"
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Alertas Inteligentes
      </h3>
      
      <AnimatePresence>
        {alerts.filter(a => !dismissed.has(a.id)).map((alert) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className={`group relative flex items-start gap-4 rounded-xl border p-4 ${colors[alert.type]}`}
          >
            <div className="mt-0.5">{icons[alert.type]}</div>
            
            <div className="flex-1">
              <h4 className="font-medium text-white">{alert.title}</h4>
              <p className="mt-1 text-sm text-zinc-400">{alert.message}</p>
              
              {alert.action && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`mt-3 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    alert.autoFix 
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30" 
                      : "bg-white/10 text-white hover:bg-white/20"
                  }`}
                >
                  {alert.autoFix ? "⚡ Corregir automáticamente" : alert.action}
                </motion.button>
              )}
            </div>
            
            <button 
              onClick={() => setDismissed(prev => new Set([...prev, alert.id]))}
              className="opacity-0 transition-opacity group-hover:opacity-100"
            >
              <X className="h-4 w-4 text-zinc-500 hover:text-white" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
