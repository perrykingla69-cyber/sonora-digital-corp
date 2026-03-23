'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { WhatsAppConnector } from '@/components/dashboard-v2/WhatsAppConnector';
import { TelegramConnector } from '@/components/dashboard-v2/TelegramConnector';

const TENANTS = [
  { id: 'contador',       label: 'Contabilidad',   icon: '📊' },
  { id: 'administradores',label: 'Administración', icon: '🏢' },
  { id: 'rh',             label: 'Recursos Humanos',icon: '👥' },
  { id: 'logistica',      label: 'Logística',      icon: '🚛' },
  { id: 'ceo',            label: 'CEO / Dirección', icon: '🎯' },
];

export default function WhatsAppPage() {
  const [tenantId, setTenantId] = useState('contador');

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-6">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-8">
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-pink-400 bg-clip-text text-transparent">
              Canales de Comunicación
            </h1>
            <p className="text-white/50 text-sm mt-1">
              Conecta WhatsApp y Telegram con el Brain IA de Mystic
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Sistema activo
          </div>
        </motion.div>
      </div>

      {/* Tenant selector */}
      <div className="max-w-5xl mx-auto mb-8">
        <p className="text-white/40 text-xs uppercase tracking-widest mb-3">Área de negocio</p>
        <div className="flex flex-wrap gap-2">
          {TENANTS.map(t => (
            <button
              key={t.id}
              onClick={() => setTenantId(t.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all duration-200
                ${tenantId === t.id
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                  : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10 hover:text-white/80'
                }`}
            >
              <span>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Connectors grid */}
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          key={`wa-${tenantId}`}
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <WhatsAppConnector tenantId={tenantId} />
        </motion.div>

        <motion.div
          key={`tg-${tenantId}`}
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2, delay: 0.05 }}
        >
          <TelegramConnector tenantId={tenantId} />
        </motion.div>
      </div>

      {/* Info footer */}
      <div className="max-w-5xl mx-auto mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: '🔒', title: 'Sin costo por mensaje', desc: 'WhatsApp Web.js no usa la API oficial de Meta' },
          { icon: '🤖', title: 'Brain IA integrado',    desc: 'Cada mensaje pasa por el motor fiscal de Mystic' },
          { icon: '🏢', title: 'Multi-tenant',          desc: 'Cada área tiene su sesión y contexto separado' },
        ].map(item => (
          <div key={item.title} className="flex gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
            <span className="text-2xl">{item.icon}</span>
            <div>
              <p className="text-white/80 text-sm font-medium">{item.title}</p>
              <p className="text-white/40 text-xs mt-0.5">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
