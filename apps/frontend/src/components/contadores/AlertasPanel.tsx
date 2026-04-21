'use client';

import React, { useState } from 'react';
import { AlertCircle, Bell, CheckCircle } from 'lucide-react';

interface Alerta {
  id: string;
  tipo: 'crítico' | 'advertencia' | 'información';
  titulo: string;
  descripción: string;
  vencimiento: string;
  monto?: number;
  leído: boolean;
}

export default function AlertasPanel({ alertas: initAlertas }: { alertas: Alerta[] }) {
  const [alertas, setAlertas] = useState<Alerta[]>(initAlertas);

  const marcarLeído = (id: string) => {
    setAlertas(alertas.map(a => a.id === id ? { ...a, leído: true } : a));
  };

  const críticas = alertas.filter(a => a.tipo === 'crítico' && !a.leído);
  const advertencias = alertas.filter(a => a.tipo === 'advertencia' && !a.leído);

  return (
    <div className="p-6 rounded-lg bg-slate-800 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <Bell className="w-5 h-5 text-amber-400" />
        <h2 className="text-xl font-bold text-white">Alertas (5 días)</h2>
      </div>

      {alertas.length === 0 ? (
        <p className="text-slate-500 text-sm">Sin alertas pendientes</p>
      ) : (
        <div className="space-y-2">
          {alertas.slice(0, 5).map(alerta => (
            <div
              key={alerta.id}
              className={`p-3 rounded-lg border transition cursor-pointer ${
                alerta.leído
                  ? 'bg-slate-700 border-slate-600 opacity-60'
                  : alerta.tipo === 'crítico'
                  ? 'bg-red-950 border-red-700'
                  : 'bg-amber-950 border-amber-700'
              }`}
              onClick={() => marcarLeído(alerta.id)}
            >
              <div className="flex items-start gap-2">
                {alerta.leído ? (
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className={`text-sm font-semibold ${alerta.leído ? 'text-slate-400' : 'text-white'}`}>
                    {alerta.titulo}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">{alerta.descripción}</p>
                  <div className="flex items-center gap-2 mt-1 text-xs">
                    <span className="text-slate-500">
                      Vence: {new Date(alerta.vencimiento).toLocaleDateString('es-MX')}
                    </span>
                    {alerta.monto && (
                      <span className="text-amber-400 font-semibold">
                        ${alerta.monto.toLocaleString('es-MX')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {críticas.length > 0 && (
        <div className="mt-4 p-2 rounded bg-red-950 border border-red-700">
          <p className="text-xs text-red-400">
            ⚠️ {críticas.length} alerta(s) crítica(s) sin leer
          </p>
        </div>
      )}

      {advertencias.length > 0 && (
        <div className="mt-2 p-2 rounded bg-amber-950 border border-amber-700">
          <p className="text-xs text-amber-400">
            📌 {advertencias.length} advertencia(s) sin leer
          </p>
        </div>
      )}
    </div>
  );
}
