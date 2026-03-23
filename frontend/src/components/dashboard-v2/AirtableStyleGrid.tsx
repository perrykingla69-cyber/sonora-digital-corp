'use client';

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface Column {
  id: string;
  name: string;
  type: 'text' | 'number' | 'date' | 'select' | 'user' | 'checkbox';
  width?: number;
  options?: { value: string; label: string; color?: string }[];
}

export interface Row {
  id: string;
  [key: string]: unknown;
}

export interface AirtableGridProps {
  title?: string;
  columns: Column[];
  rows: Row[];
  theme?: 'cyan' | 'magenta' | 'emerald' | 'amber';
  onAddRow?: () => void;
  onRowClick?: (row: Row) => void;
  pageSize?: number;
}

// ─── Theme ───────────────────────────────────────────────────────────────────

const themeColors = {
  cyan:    { accent: 'text-cyan-400',   border: 'border-cyan-500/30', badge: 'bg-cyan-500/20 text-cyan-300',   btn: 'bg-cyan-500 hover:bg-cyan-400'   },
  magenta: { accent: 'text-pink-400',   border: 'border-pink-500/30', badge: 'bg-pink-500/20 text-pink-300',   btn: 'bg-pink-500 hover:bg-pink-400'   },
  emerald: { accent: 'text-emerald-400',border: 'border-emerald-500/30',badge:'bg-emerald-500/20 text-emerald-300',btn:'bg-emerald-500 hover:bg-emerald-400'},
  amber:   { accent: 'text-amber-400',  border: 'border-amber-500/30', badge: 'bg-amber-500/20 text-amber-300', btn: 'bg-amber-500 hover:bg-amber-400'  },
} as const;

// ─── Cell Renderers ──────────────────────────────────────────────────────────

function CellValue({ col, value, theme }: { col: Column; value: unknown; theme: keyof typeof themeColors }) {
  const t = themeColors[theme];

  if (col.type === 'checkbox') {
    return (
      <span className={`inline-flex items-center justify-center w-4 h-4 rounded border ${value ? 'bg-current border-transparent' : 'border-white/20'} ${t.accent}`}>
        {value ? '✓' : ''}
      </span>
    );
  }

  if (col.type === 'select') {
    if (!value) return <span className="text-white/30">—</span>;
    const opt = col.options?.find(o => o.value === value);
    const label = opt?.label ?? String(value);
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${t.badge}`}>
        {label}
      </span>
    );
  }

  if (col.type === 'user') {
    if (!value) return <span className="text-white/30">—</span>;
    const name = String(value);
    const initials = name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
    return (
      <span className="flex items-center gap-2">
        <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${t.badge}`}>
          {initials}
        </span>
        <span className="text-white/80 text-sm">{name}</span>
      </span>
    );
  }

  if (col.type === 'date' && value) {
    try {
      return <span className="text-white/70 text-sm">{new Date(String(value)).toLocaleDateString('es-MX')}</span>;
    } catch { /* fall through */ }
  }

  if (col.type === 'number') {
    return <span className={`font-mono text-sm ${t.accent}`}>{value != null ? Number(value).toLocaleString('es-MX') : '—'}</span>;
  }

  return <span className="text-white/80 text-sm truncate">{value != null ? String(value) : '—'}</span>;
}

// ─── Component ───────────────────────────────────────────────────────────────

export function AirtableStyleGrid({
  title,
  columns,
  rows,
  theme = 'cyan',
  onAddRow,
  onRowClick,
  pageSize = 20,
}: AirtableGridProps) {
  const t = themeColors[theme];
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState('');
  const [sortCol, setSortCol] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    let r = rows;
    if (search) {
      const q = search.toLowerCase();
      r = r.filter(row =>
        columns.some(col => {
          const v = row[col.id];
          return v != null && String(v).toLowerCase().includes(q);
        })
      );
    }
    if (sortCol) {
      r = [...r].sort((a, b) => {
        const av = a[sortCol] ?? '';
        const bv = b[sortCol] ?? '';
        const cmp = String(av).localeCompare(String(bv), 'es-MX', { numeric: true });
        return sortDir === 'asc' ? cmp : -cmp;
      });
    }
    return r;
  }, [rows, search, sortCol, sortDir, columns]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
  const paginated = filtered.slice(page * pageSize, (page + 1) * pageSize);

  const toggleSort = (colId: string) => {
    if (sortCol === colId) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortCol(colId); setSortDir('asc'); }
    setPage(0);
  };

  const toggleAll = () => {
    if (selected.size === paginated.length) setSelected(new Set());
    else setSelected(new Set(paginated.map(r => r.id)));
  };

  const toggleRow = (id: string) => {
    setSelected(prev => {
      const s = new Set(prev);
      s.has(id) ? s.delete(id) : s.add(id);
      return s;
    });
  };

  return (
    <div className={`rounded-2xl border ${t.border} bg-white/5 backdrop-blur-sm overflow-hidden`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
        <div className="flex items-center gap-3">
          {title && <h3 className={`font-semibold ${t.accent}`}>{title}</h3>}
          <span className="text-white/40 text-xs">{filtered.length} registros</span>
          {selected.size > 0 && (
            <span className={`px-2 py-0.5 rounded-full text-xs ${t.badge}`}>
              {selected.size} seleccionados
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Buscar..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0); }}
            className="px-3 py-1.5 text-sm rounded-lg bg-white/10 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-white/30 w-48"
          />
          {onAddRow && (
            <button
              onClick={onAddRow}
              className={`px-3 py-1.5 text-sm rounded-lg text-white font-medium transition-colors ${t.btn}`}
            >
              + Agregar
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/10">
              <th className="w-10 px-4 py-2">
                <input
                  type="checkbox"
                  checked={selected.size === paginated.length && paginated.length > 0}
                  onChange={toggleAll}
                  className="accent-current"
                />
              </th>
              {columns.map(col => (
                <th
                  key={col.id}
                  style={{ width: col.width }}
                  onClick={() => toggleSort(col.id)}
                  className={`px-3 py-2 text-xs font-medium text-white/50 uppercase tracking-wide cursor-pointer select-none hover:text-white/80 transition-colors`}
                >
                  {col.name}
                  {sortCol === col.id && (
                    <span className="ml-1">{sortDir === 'asc' ? '↑' : '↓'}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <AnimatePresence initial={false}>
              {paginated.map((row) => (
                <motion.tr
                  key={row.id}
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.15 }}
                  onClick={() => onRowClick?.(row)}
                  className={`border-b border-white/5 transition-colors cursor-pointer
                    ${selected.has(row.id) ? 'bg-white/10' : 'hover:bg-white/5'}
                  `}
                >
                  <td className="w-10 px-4 py-2" onClick={e => { e.stopPropagation(); toggleRow(row.id); }}>
                    <input
                      type="checkbox"
                      checked={selected.has(row.id)}
                      onChange={() => toggleRow(row.id)}
                      className="accent-current"
                    />
                  </td>
                  {columns.map(col => (
                    <td key={col.id} className="px-3 py-2">
                      <CellValue col={col} value={row[col.id]} theme={theme} />
                    </td>
                  ))}
                </motion.tr>
              ))}
            </AnimatePresence>
            {paginated.length === 0 && (
              <tr>
                <td colSpan={columns.length + 1} className="px-4 py-8 text-center text-white/30 text-sm">
                  Sin resultados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Footer pagination */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-white/10 text-xs text-white/40">
        <span>Página {page + 1} de {pageCount}</span>
        <div className="flex gap-1">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-2 py-1 rounded hover:bg-white/10 disabled:opacity-30 transition-colors"
          >
            ‹
          </button>
          <button
            onClick={() => setPage(p => Math.min(pageCount - 1, p + 1))}
            disabled={page >= pageCount - 1}
            className="px-2 py-1 rounded hover:bg-white/10 disabled:opacity-30 transition-colors"
          >
            ›
          </button>
        </div>
      </div>
    </div>
  );
}
