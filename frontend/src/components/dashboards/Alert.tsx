import clsx from 'clsx'

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  onClose?: () => void
}

const typeStyles = {
  success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}

const iconMap = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

export function Alert({ type, title, message, onClose }: AlertProps) {
  return (
    <div className={clsx('border rounded-lg p-4 flex items-start gap-3', typeStyles[type])}>
      <span className="text-lg font-bold flex-shrink-0">{iconMap[type]}</span>
      <div className="flex-1">
        {title && <p className="font-semibold">{title}</p>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-lg font-bold hover:opacity-70 flex-shrink-0"
          aria-label="Cerrar alerta"
        >
          ×
        </button>
      )}
    </div>
  )
}
