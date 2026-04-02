"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface DataPoint {
  time: string;
  value: number;
  predicted?: number;
}

export function ActivityGraph({ data, title }: { data: DataPoint[]; title: string }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl border border-white/10 bg-zinc-950/50 p-6 backdrop-blur-xl"
    >
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <div className="flex gap-4 text-sm">
          <span className="flex items-center gap-2 text-cyan-400">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            Real
          </span>
          <span className="flex items-center gap-2 text-fuchsia-400">
            <span className="h-2 w-2 rounded-full bg-fuchsia-400" />
            Predicción IA
          </span>
        </div>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#e879f9" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#e879f9" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <XAxis 
              dataKey="time" 
              stroke="#52525b" 
              fontSize={12}
              tickLine={false}
            />
            <YAxis 
              stroke="#52525b" 
              fontSize={12}
              tickLine={false}
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
            />
            
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg border border-white/10 bg-zinc-900/95 p-3 shadow-2xl">
                      <p className="text-sm text-zinc-400">{payload[0].payload.time}</p>
                      <p className="text-lg font-bold text-cyan-400">
                        ${payload[0].value?.toLocaleString()}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            
            <Area
              type="monotone"
              dataKey="value"
              stroke="#06b6d4"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorValue)"
              animationDuration={2000}
            />
            
            <Area
              type="monotone"
              dataKey="predicted"
              stroke="#e879f9"
              strokeWidth={2}
              strokeDasharray="5 5"
              fillOpacity={1}
              fill="url(#colorPredicted)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
