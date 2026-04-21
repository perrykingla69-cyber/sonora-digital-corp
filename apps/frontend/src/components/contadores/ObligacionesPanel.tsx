'use client';

import React, { useState } from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

interface Obligacion {
  id: string;
  nombre: string;
  vencimiento: string;
  régimen: string;
  completada: boolean;
  monto?: number;
}

export default function ObligacionesPanel({ obligaciones }: { obligaciones: Obligacion[] }) {
  const [filtro, setFiltro] = useState<string>('todos');

  const filtered = filtro === 'todos'
    ? obligaciones
    : obligaciones.filter(o => o.régimen === filtro);

  const regímenes = [...new Set(obligaciones.map(o => o.régimen))];

  return (
    <div className="p-6 rounded-lg bg-slate-800 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">Obligaciones</h2>

      {/* Filter */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        <button
          onClick={() => setFiltro('todos')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition ${
            filtro === 'todos'
              ? 'bg-amber-500 text-black font-semibold'
              : 'bg-slate-700 text-slate-300'
          }`}
        >
          Todos
        </button>
        {regímenes.map(r => (
          <button
            key={r}
            onClick={() => setFiltro(r)}
            className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition ${
              filtro === r
                ? 'bg-amber-500 text-black font-semibold'
                : 'bg-slate-700 text-slate-300'
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <p className="text-slate-500 text-sm">Sin obligaciones para este filtro</p>
        ) : (
          filtered.map((obl, idx) => {
            const daysLeft = Math.ceil(
              (new Date(obl.vencimiento).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
            );
            const isUrgent = daysLeft <= 3 && daysLeft > 0;
            const isOverdue = daysLeft < 0;

            return (
              <div
                key={obl.id}
                className={`flex items-start gap-3 p-3 rounded-lg border transition ${
                  obl.completada
                    ? 'bg-slate-700 border-slate-600'
                    : isOverdue
                    ? 'bg-red-950 border-red-700'
                    : isUrgent
                    ? 'bg-amber-950 border-amber-700'
                    : 'bg-slate-700 border-slate-600'
                }`}
              >
                {obl.completada ? (
                  <CheckCircle2 className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-500 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className={`font-medium ${obl.completada ? 'text-slate-400 line-through' : 'text-white'}`}>
                    {obl.nombre}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Vence: {new Date(obl.vencimiento).toLocaleDateString('es-MX')}
                    {daysLeft > 0 && ` (${daysLeft}d)`}
                    {daysLeft <= 0 && ' (VENCIDA)'}
                  </p>
                  {obl.monto && (
                    <p className="text-xs text-amber-400 mt-0.5">${obl.monto.toLocaleString('es-MX')}</p>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
