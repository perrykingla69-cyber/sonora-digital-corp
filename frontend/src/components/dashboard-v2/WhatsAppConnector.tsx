"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { QrCode, CheckCircle, XCircle, RefreshCw, Smartphone } from "lucide-react";
import { io, Socket } from "socket.io-client";

interface WhatsAppStatus {
  tenantId: string;
  status: 'disconnected' | 'connecting' | 'connected' | 'ready';
  qrCode: string | null;
  connected: boolean;
}

export function WhatsAppConnector({ tenantId }: { tenantId: string }) {
  const [status, setStatus] = useState<WhatsAppStatus | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [loading, setLoading] = useState(false);

  const BRIDGE = process.env.NEXT_PUBLIC_WHATSAPP_BRIDGE_URL || 'http://localhost:3002';

  useEffect(() => {
    const newSocket = io(BRIDGE);
    setSocket(newSocket);
    newSocket.emit('join-tenant', tenantId);
    newSocket.on('whatsapp-status', (data: WhatsAppStatus) => {
      setStatus(data);
      setLoading(false);
    });
    fetchStatus();
    return () => { newSocket.close(); };
  }, [tenantId]);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${BRIDGE}/${tenantId}/status`);
      setStatus(await res.json());
    } catch {}
  };

  const connect = async () => {
    setLoading(true);
    try {
      await fetch(`${BRIDGE}/${tenantId}/connect`, { method: 'POST' });
    } catch { setLoading(false); }
  };

  const disconnect = async () => {
    await fetch(`${BRIDGE}/${tenantId}/disconnect`, { method: 'POST' }).catch(() => {});
    setStatus(null);
  };

  const statusStyle = {
    ready:       'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    connecting:  'text-amber-400  bg-amber-500/10  border-amber-500/30',
    connected:   'text-cyan-400   bg-cyan-500/10   border-cyan-500/30',
    disconnected:'text-zinc-400   bg-zinc-500/10   border-zinc-500/30',
  };
  const statusText = {
    ready:       'Conectado y listo',
    connecting:  'Esperando escaneo...',
    connected:   'Conectando...',
    disconnected:'Desconectado',
  };
  const s = status?.status ?? 'disconnected';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-white/10 bg-zinc-950/50 p-6 backdrop-blur-xl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl border ${statusStyle[s]}`}>
            <Smartphone className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">WhatsApp Business</h3>
            <p className={`text-sm ${s === 'ready' ? 'text-emerald-400' : 'text-zinc-400'}`}>
              {statusText[s]}
            </p>
          </div>
        </div>

        {s === 'ready' ? (
          <button onClick={disconnect}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors">
            <XCircle className="h-4 w-4" /> Desconectar
          </button>
        ) : (
          <button onClick={connect} disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors disabled:opacity-50">
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
            {loading ? 'Conectando...' : 'Conectar'}
          </button>
        )}
      </div>

      {/* Estado dinámico */}
      <AnimatePresence mode="wait">
        {status?.qrCode && s === 'connecting' && (
          <motion.div key="qr"
            initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}
            className="flex flex-col items-center gap-4 p-6 rounded-xl bg-white/5">
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={status.qrCode} alt="QR WhatsApp" className="w-56 h-56 rounded-lg" />
              <div className="absolute inset-0 animate-pulse bg-emerald-500/5 rounded-lg" />
            </div>
            <div className="text-center">
              <p className="text-white font-medium mb-1">Escanea con WhatsApp</p>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Abre WhatsApp → Dispositivos vinculados → Vincular dispositivo
              </p>
            </div>
          </motion.div>
        )}

        {s === 'ready' && (
          <motion.div key="ready" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex items-center gap-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <CheckCircle className="h-8 w-8 text-emerald-400 shrink-0" />
            <div>
              <p className="text-white font-medium">¡WhatsApp conectado!</p>
              <p className="text-sm text-zinc-400">Los mensajes se responden automáticamente con el Brain IA</p>
            </div>
          </motion.div>
        )}

        {s === 'disconnected' && (
          <motion.div key="disconnected" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="text-center p-8 text-zinc-500">
            <QrCode className="h-14 w-14 mx-auto mb-3 opacity-40" />
            <p className="text-sm">Haz clic en &quot;Conectar&quot; para vincular WhatsApp</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats cuando está listo */}
      {s === 'ready' && (
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/5">
          {[
            { label: 'Mensajes hoy', value: '—' },
            { label: 'Respuestas IA', value: '—' },
            { label: 'Estado', value: 'Activo', color: 'text-emerald-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="text-center">
              <p className={`text-xl font-bold ${color ?? 'text-white'}`}>{value}</p>
              <p className="text-xs text-zinc-500 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
