import clsx from 'clsx'
import { DashboardCard } from './Card'

interface StatProps {
  label: string
  value: string | number
  sub?: string
  color?: 'green' | 'red' | 'blue' | 'gray' | 'gold'
  icon?: React.ReactNode
  trend?: { direction: 'up' | 'down'; value: number }
}

const colorMap = {
  green: 'text-emerald-400',
  red: 'text-red-400',
  blue: 'text-sky-400',
  gray: 'text-sovereign-text',
  gold: 'text-sovereign-gold',
}

export function Stat({ label, value, sub, color = 'gray', icon, trend }: StatProps) {
  return (
    <DashboardCard>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium text-sovereign-muted uppercase tracking-wide">{label}</p>
          <p className={clsx('text-2xl font-bold mt-1', colorMap[color])}>{value}</p>
          {sub && <p className="text-xs text-sovereign-muted mt-0.5">{sub}</p>}
          {trend && (
            <p className={clsx('text-xs font-semibold mt-2', trend.direction === 'up' ? 'text-emerald-400' : 'text-red-400')}>
              {trend.direction === 'up' ? '↑' : '↓'} {trend.value}%
            </p>
          )}
        </div>
        {icon && <div className="text-sovereign-muted/40 text-3xl">{icon}</div>}
      </div>
    </DashboardCard>
  )
}
