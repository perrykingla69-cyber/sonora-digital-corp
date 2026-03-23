"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  prefix?: string;
  suffix?: string;
  icon: React.ReactNode;
  color: "cyan" | "magenta" | "emerald" | "amber";
  delay?: number;
}

const colorMap = {
  cyan: "from-cyan-500/20 to-cyan-600/5 border-cyan-500/30 text-cyan-400",
  magenta: "from-fuchsia-500/20 to-fuchsia-600/5 border-fuchsia-500/30 text-fuchsia-400",
  emerald: "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 text-emerald-400",
  amber: "from-amber-500/20 to-amber-600/5 border-amber-500/30 text-amber-400"
};

export function MetricCard({ title, value, change, prefix = "", suffix = "", icon, color, delay = 0 }: MetricCardProps) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br ${colorMap[color]} p-6 backdrop-blur-xl`}
    >
      {/* Glow effect */}
      <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-white/5 blur-3xl" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div className={`rounded-xl bg-gradient-to-br ${colorMap[color]} p-2.5 bg-opacity-20`}>
            {icon}
          </div>
          {change !== undefined && (
            <div className={`flex items-center gap-1 text-sm font-medium ${isPositive ? 'text-emerald-400' : isNegative ? 'text-rose-400' : 'text-zinc-400'}`}>
              {isPositive && <TrendingUp className="h-4 w-4" />}
              {isNegative && <TrendingDown className="h-4 w-4" />}
              <span>{Math.abs(change).toFixed(1)}%</span>
            </div>
          )}
        </div>
        
        <div className="mt-4">
          <p className="text-sm font-medium text-zinc-400">{title}</p>
          <motion.h3 
            className="mt-1 text-3xl font-bold tracking-tight text-white"
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: delay + 0.2 }}
          >
            {prefix}{value}{suffix}
          </motion.h3>
        </div>
        
        {/* Animated bar */}
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div 
            className={`h-full rounded-full bg-gradient-to-r ${colorMap[color].split(' ')[0].replace('/20', '')}`}
            initial={{ width: 0 }}
            animate={{ width: "70%" }}
            transition={{ duration: 1, delay: delay + 0.5 }}
          />
        </div>
      </div>
    </motion.div>
  );
}
