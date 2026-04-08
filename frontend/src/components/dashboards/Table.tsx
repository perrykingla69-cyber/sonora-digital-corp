import clsx from 'clsx'

interface TableProps {
  columns: { key: string; label: string; align?: 'left' | 'center' | 'right' }[]
  rows: Record<string, React.ReactNode>[]
  loading?: boolean
  empty?: string
}

export function Table({ columns, rows, loading = false, empty = 'Sin datos' }: TableProps) {
  if (loading) {
    return <div className="text-center py-8 text-sovereign-muted">Cargando...</div>
  }

  if (!rows.length) {
    return <div className="text-center py-8 text-sovereign-muted">{empty}</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-sovereign-border">
            {columns.map((col) => (
              <th
                key={col.key}
                className={clsx(
                  'px-4 py-3 text-xs font-semibold uppercase tracking-wide text-sovereign-muted text-left',
                  col.align === 'center' && 'text-center',
                  col.align === 'right' && 'text-right'
                )}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className="border-b border-sovereign-border/40 hover:bg-sovereign-border/10 transition">
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={clsx(
                    'px-4 py-3 text-sovereign-text',
                    col.align === 'center' && 'text-center',
                    col.align === 'right' && 'text-right'
                  )}
                >
                  {row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
