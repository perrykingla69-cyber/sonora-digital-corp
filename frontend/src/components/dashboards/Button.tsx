import clsx from 'clsx'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  loading?: boolean
}

const variantStyles = {
  primary: 'bg-sovereign-gold text-black hover:bg-yellow-500 font-medium',
  secondary: 'bg-sovereign-border text-sovereign-text hover:bg-sovereign-border/80 border border-sovereign-border',
  danger: 'bg-red-600 text-white hover:bg-red-700 font-medium',
  ghost: 'bg-transparent text-sovereign-text hover:bg-sovereign-border/20',
}

const sizeStyles = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  className,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={loading || disabled}
      className={clsx(
        'rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {loading ? '⏳ Cargando...' : children}
    </button>
  )
}
