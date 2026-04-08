import clsx from 'clsx'

interface DashboardCardProps {
  title?: string
  children: React.ReactNode
  className?: string
  badge?: { label: string; color: 'green' | 'red' | 'yellow' | 'blue' }
  onClick?: () => void
}

const badgeColors = {
  green: 'bg-emerald-100 text-emerald-700',
  red: 'bg-red-100 text-red-700',
  yellow: 'bg-yellow-100 text-yellow-700',
  blue: 'bg-blue-100 text-blue-700',
}

export function DashboardCard({
  title,
  children,
  className,
  badge,
  onClick,
}: DashboardCardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-sovereign-border bg-sovereign-card shadow-sm p-6',
        onClick && 'cursor-pointer hover:border-sovereign-gold/50 transition-colors',
        className
      )}
      onClick={onClick}
    >
      {(title || badge) && (
        <div className="flex items-center justify-between mb-4">
          {title && <h3 className="text-lg font-semibold text-sovereign-text">{title}</h3>}
          {badge && (
            <span className={clsx('px-2.5 py-0.5 rounded-full text-xs font-medium', badgeColors[badge.color])}>
              {badge.label}
            </span>
          )}
        </div>
      )}
      <div>{children}</div>
    </div>
  )
}
