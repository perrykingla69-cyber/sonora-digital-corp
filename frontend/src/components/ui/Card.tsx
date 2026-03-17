import clsx from 'clsx'

interface CardProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={clsx('bg-white rounded-xl border border-gray-200 shadow-sm', className)}>
      {children}
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  sub?: string
  color?: 'green' | 'red' | 'blue' | 'gray'
  icon?: React.ReactNode
}

const colorMap = {
  green: 'text-emerald-600',
  red:   'text-red-500',
  blue:  'text-brand-600',
  gray:  'text-gray-700',
}

export function StatCard({ label, value, sub, color = 'gray', icon }: StatCardProps) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
          <p className={clsx('text-2xl font-bold mt-1', colorMap[color])}>{value}</p>
          {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        </div>
        {icon && <div className="text-gray-300">{icon}</div>}
      </div>
    </Card>
  )
}
