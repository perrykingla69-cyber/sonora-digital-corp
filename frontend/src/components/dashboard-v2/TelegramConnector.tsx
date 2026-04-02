"use client";

import { motion } from "framer-motion";
import { MessageCircle, ExternalLink, Download, CheckCircle } from "lucide-react";

const BOT = process.env.NEXT_PUBLIC_TELEGRAM_BOT || "HermesAsistenteBot";

const STEPS = [
  { icon: Download,      text: "Descarga Telegram (gratis)" },
  { icon: MessageCircle, text: `Busca @${BOT}` },
  { icon: CheckCircle,   text: "Presiona /start y escribe tu RFC" },
];

export function TelegramConnector() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="rounded-2xl border border-white/10 bg-zinc-950/50 p-6 backdrop-blur-xl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl border bg-sky-500/10 border-sky-500/30 text-sky-400">
            <MessageCircle className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Telegram</h3>
            <p className="text-sm text-sky-400">Bot activo · @{BOT}</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-300">
          En línea
        </span>
      </div>

      {/* Pasos para usuario nuevo */}
      <div className="space-y-3 mb-6">
        <p className="text-xs font-medium text-zinc-500 uppercase tracking-widest">
          Para usuarios nuevos
        </p>
        {STEPS.map(({ icon: Icon, text }, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-full bg-sky-500/15 border border-sky-500/20 flex items-center justify-center shrink-0">
              <span className="text-xs font-bold text-sky-400">{i + 1}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-zinc-300">
              <Icon className="h-3.5 w-3.5 text-zinc-500" />
              {text}
            </div>
          </div>
        ))}
      </div>

      {/* Info del bot */}
      <div className="bg-sky-500/5 border border-sky-500/15 rounded-xl p-4 mb-5">
        <p className="text-sm text-zinc-300 leading-relaxed">
          El Brain IA responde automáticamente con el contexto fiscal de tu empresa.
          Pregunta sobre facturas, declaraciones, nómina, o cualquier trámite SAT.
        </p>
      </div>

      {/* Acciones */}
      <div className="flex gap-3">
        <a
          href={`https://t.me/${BOT}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-sky-500/15 hover:bg-sky-500/25 border border-sky-500/20 text-sky-300 text-sm font-medium transition-colors"
        >
          <MessageCircle className="h-4 w-4" />
          Abrir bot
        </a>
        <a
          href="https://telegram.org"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 py-2.5 px-4 rounded-xl bg-zinc-800/50 hover:bg-zinc-700/50 border border-zinc-700/30 text-zinc-400 text-sm transition-colors"
        >
          <ExternalLink className="h-4 w-4" />
          Descargar
        </a>
      </div>
    </motion.div>
  );
}
