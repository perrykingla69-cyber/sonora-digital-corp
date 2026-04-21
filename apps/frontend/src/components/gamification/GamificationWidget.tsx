'use client';

import React, { useState, useEffect } from 'react';

export default function GamificationWidget() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/v1/gamification/stats', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setStats(data.user_stats);
      } catch (error) {
        console.error('Error loading gamification stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div className="animate-pulse h-48 bg-slate-700 rounded-lg" />;

  return (
    <div className="space-y-4">
      {/* Level & XP */}
      <div className="p-6 rounded-lg bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-slate-400">Nivel</p>
            <h3 className="text-3xl font-black text-amber-400">{stats?.level || 1}</h3>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-400">Experiencia</p>
            <p className="text-2xl font-bold text-white">{stats?.total_xp || 0} XP</p>
          </div>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-amber-400 to-orange-500 h-3 rounded-full transition-all"
            style={{ width: `${((stats?.total_xp || 0) % 100) * 10}%` }}
          />
        </div>
        <p className="text-xs text-slate-400 mt-2">
          {(stats?.total_xp || 0) % 100} / 100 XP para siguiente nivel
        </p>
      </div>

      {/* Badges */}
      <div>
        <h4 className="font-bold text-white mb-3">Insignias Desbloqueadas ({stats?.badges_earned || 0})</h4>
        <div className="flex gap-2 flex-wrap">
          {stats?.achievements?.map((badge: any) => (
            <div
              key={badge.id}
              className="p-3 rounded-lg bg-slate-800 border border-slate-700 hover:border-amber-500/50 transition text-center cursor-pointer"
              title={badge.title}
            >
              <div className="text-2xl">{badge.icon_emoji}</div>
              <p className="text-xs text-slate-300 mt-1">{badge.title}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Bonus */}
      <div className="p-4 rounded-lg bg-slate-800/50 border border-green-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-400">Bono Diario</p>
            <p className="text-lg font-bold text-green-400">+100 XP disponible</p>
          </div>
          <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-bold transition">
            Reclamar
          </button>
        </div>
      </div>

      {/* Leaderboard Preview */}
      <div>
        <h4 className="font-bold text-white mb-3">Ranking Este Mes</h4>
        <div className="space-y-2">
          {[
            { rank: 1, user: 'contador_pro', xp: 8900, emoji: '👑' },
            { rank: 2, user: 'contador_gold', xp: 7200, emoji: '🥈' },
            { rank: 3, user: 'Tu', xp: stats?.total_xp || 0, emoji: '🥉' }
          ].map((entry) => (
            <div key={entry.rank} className="flex items-center justify-between p-3 bg-slate-800 rounded">
              <div className="flex items-center gap-3">
                <span className="text-lg">{entry.emoji}</span>
                <span className="text-white font-medium">{entry.user}</span>
              </div>
              <span className="text-amber-400 font-bold">{entry.xp} XP</span>
            </div>
          ))}
        </div>
      </div>

      {/* Streaks */}
      {stats?.streaks_active > 0 && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
          <p className="text-sm text-slate-400">Racha Activa 🔥</p>
          <p className="text-2xl font-black text-red-400">{stats?.streaks_active} días</p>
        </div>
      )}
    </div>
  );
}
