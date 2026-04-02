import clsx from 'clsx'

interface CardProps {
  children: React.ReactNode
  className?: string
  gold?: boolean
}

export function Card({ children, className, gold }: CardProps) {
  return (
    <div className={clsx(
      'rounded-xl border shadow-sm',
      gold
        ? 'bg-sovereign-card border-sovereign-gold/20 glass'
        : 'bg-sovereign-card border-sovereign-border',
      className
    )}>
      {children}
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  sub?: string
  color?: 'green' | 'red' | 'blue' | 'gray' | 'gold'
  icon?: React.ReactNode
}

const colorMap = {
  green: 'text-emerald-400',
  red:   'text-red-400',
  blue:  'text-sky-400',
  gray:  'text-sovereign-text',
  gold:  'text-sovereign-gold',
}

export function StatCard({ label, value, sub, color = 'gray', icon }: StatCardProps) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-sovereign-muted uppercase tracking-wide">{label}</p>
          <p className={clsx('text-2xl font-bold mt-1', colorMap[color])}>{value}</p>
          {sub && <p className="text-xs text-sovereign-muted mt-0.5">{sub}</p>}
        </div>
        {icon && <div className="text-sovereign-muted/40">{icon}</div>}
      </div>
    </Card>
  )
}
