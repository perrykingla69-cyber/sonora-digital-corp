'use client';

import React, { useState } from 'react';
import { Calculator } from 'lucide-react';

interface CalcResult {
  isr: number;
  iva: number;
  iee?: number;
  base_gravable: number;
  fuente: string;
}

export default function CalculadoraRapida() {
  const [ingresos, setIngresos] = useState<number>(0);
  const [gastos, setGastos] = useState<number>(0);
  const [período, setPeriodo] = useState<string>('mes');
  const [régimen, setRegimen] = useState<string>('contribuyente');
  const [resultado, setResultado] = useState<CalcResult | null>(null);
  const [loading, setLoading] = useState(false);

  const calcular = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const res = await fetch('/api/v1/agents/fiscal/calculate_taxes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          ingresos,
          gastos,
          período,
          régimen
        })
      });

      if (!res.ok) throw new Error('Error en cálculo');
      const data = await res.json();
      setResultado(data.resultado);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-lg bg-slate-800 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <Calculator className="w-5 h-5 text-amber-400" />
        <h2 className="text-xl font-bold text-white">Calculadora Rápida</h2>
      </div>

      <div className="space-y-3">
        {/* Ingresos */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">Ingresos</label>
          <input
            type="number"
            value={ingresos}
            onChange={e => setIngresos(Number(e.target.value))}
            placeholder="0.00"
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white placeholder-slate-500"
          />
        </div>

        {/* Gastos */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">Gastos Deducibles</label>
          <input
            type="number"
            value={gastos}
            onChange={e => setGastos(Number(e.target.value))}
            placeholder="0.00"
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white placeholder-slate-500"
          />
        </div>

        {/* Período */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">Período</label>
          <select
            value={período}
            onChange={e => setPeriodo(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white"
          >
            <option>mes</option>
            <option>trimestre</option>
            <option>año</option>
          </select>
        </div>

        {/* Régimen */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">Régimen</label>
          <select
            value={régimen}
            onChange={e => setRegimen(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white"
          >
            <option value="contribuyente">Contribuyente ordinario</option>
            <option value="rif">RIF</option>
            <option value="rii">RII</option>
          </select>
        </div>

        {/* Botón */}
        <button
          onClick={calcular}
          disabled={loading}
          className="w-full px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-600 text-black font-semibold rounded-lg transition"
        >
          {loading ? 'Calculando...' : 'Calcular'}
        </button>

        {/* Resultado */}
        {resultado && (
          <div className="mt-4 p-3 rounded-lg bg-slate-700 border border-amber-500/30 space-y-2">
            <p className="text-sm text-slate-300">Base gravable:</p>
            <p className="text-xl font-bold text-amber-400">
              ${(resultado.base_gravable || 0).toLocaleString('es-MX', { maximumFractionDigits: 2 })}
            </p>
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-600">
              <div>
                <p className="text-xs text-slate-400">ISR</p>
                <p className="text-lg font-semibold text-red-400">
                  ${resultado.isr.toLocaleString('es-MX', { maximumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">IVA</p>
                <p className="text-lg font-semibold text-blue-400">
                  ${resultado.iva.toLocaleString('es-MX', { maximumFractionDigits: 2 })}
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2">Fuente: {resultado.fuente}</p>
          </div>
        )}
      </div>
    </div>
  );
}
