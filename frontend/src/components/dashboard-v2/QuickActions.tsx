"use client";

import { motion } from "framer-motion";
import { FileText, Calculator, MessageSquare, Shield, Zap, BarChart3 } from "lucide-react";

const actions = [
  { id: "mve", label: "Generar MVE", icon: FileText, color: "cyan", shortcut: "⌘M" },
  { id: "cierre", label: "Pre-cierre", icon: Calculator, color: "emerald", shortcut: "⌘C" },
  { id: "brain", label: "Preguntar a Brain", icon: MessageSquare, color: "fuchsia", shortcut: "⌘B" },
  { id: "validar", label: "Validar CFDI", icon: Shield, color: "amber", shortcut: "⌘V" },
  { id: "reporte", label: "Reporte Ejecutivo", icon: BarChart3, color: "indigo", shortcut: "⌘R" },
  { id: "automation", label: "Automatizaciones", icon: Zap, color: "rose", shortcut: "⌘A" }
];

export function QuickActions() {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
      {actions.map((action, i) => (
        <motion.button
          key={action.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
          className="group relative flex flex-col items-center gap-3 rounded-2xl border border-white/5 bg-zinc-900/50 p-4 transition-all hover:border-white/10 hover:bg-zinc-800/50"
        >
          <div className={`rounded-xl bg-${action.color}-500/20 p-3 text-${action.color}-400`}>
            <action.icon className="h-6 w-6" />
          </div>
          <span className="text-sm font-medium text-zinc-300 group-hover:text-white">
            {action.label}
          </span>
          <span className="absolute right-2 top-2 text-xs text-zinc-600 opacity-0 transition-opacity group-hover:opacity-100">
            {action.shortcut}
          </span>
        </motion.button>
      ))}
    </div>
  );
}
