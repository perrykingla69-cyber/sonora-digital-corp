import clsx from 'clsx'

const variants = {
  pendiente:  'bg-yellow-100 text-yellow-800',
  pagada:     'bg-emerald-100 text-emerald-800',
  cancelada:  'bg-red-100 text-red-800',
  presentada: 'bg-blue-100 text-blue-800',
  alta:       'bg-red-100 text-red-700',
  media:      'bg-yellow-100 text-yellow-700',
  baja:       'bg-gray-100 text-gray-600',
  activo:     'bg-emerald-100 text-emerald-700',
  inactivo:   'bg-gray-100 text-gray-500',
}

type Variant = keyof typeof variants

export function Badge({ variant, label }: { variant: Variant; label?: string }) {
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', variants[variant])}>
      {label ?? variant}
    </span>
  )
}
