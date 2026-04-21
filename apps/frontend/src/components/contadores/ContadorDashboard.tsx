'use client';

import React, { useState, useEffect } from 'react';
import ObligacionesPanel from './ObligacionesPanel';
import CalculadoraRapida from './CalculadoraRapida';
import AlertasPanel from './AlertasPanel';
import ChatFiscal from './ChatFiscal';

export default function ContadorDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [obligaciones, setObligaciones] = useState<any[]>([]);
  const [alertas, setAlertas] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');

        // Fetch gamification stats
        const statsRes = await fetch('/api/v1/gamification/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!statsRes.ok) throw new Error('Failed to fetch stats');
        const statsData = await statsRes.json();
        setStats(statsData.user_stats);

        // Fetch compliance (obligaciones)
        const complianceRes = await fetch('/api/v1/agents/fiscal/check_compliance', {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!complianceRes.ok) throw new Error('Failed to fetch compliance');
        const complianceData = await complianceRes.json();
        setObligaciones(complianceData.obligaciones || []);
        setAlertas(complianceData.alertas || []);

        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
    const interval = setInterval(fetchDashboard, 5000); // 5s refresh
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="animate-pulse h-40 bg-slate-700 rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-bold text-white">Tablero Contador</h1>
        <p className="text-slate-400 mt-1">Gestiona obligaciones fiscales y cumplimiento</p>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
          <p className="text-slate-400 text-sm">Obligaciones</p>
          <p className="text-2xl font-bold text-white mt-1">{obligaciones.length}</p>
        </div>
        <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
          <p className="text-slate-400 text-sm">Cumplidas</p>
          <p className="text-2xl font-bold text-green-400 mt-1">
            {obligaciones.filter((o: any) => o.completada).length}
          </p>
        </div>
        <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
          <p className="text-slate-400 text-sm">Próximas 5 días</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">
            {alertas.length}
          </p>
        </div>
      </div>

      {/* 4 Paneles principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ObligacionesPanel obligaciones={obligaciones} />
        <CalculadoraRapida />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertasPanel alertas={alertas} />
        <ChatFiscal />
      </div>
    </div>
  );
}
