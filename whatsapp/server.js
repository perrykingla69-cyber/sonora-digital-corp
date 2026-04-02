/**
 * mystic-wa — Microservicio WhatsApp para Mystic Platform
 * Usa @whiskeysockets/baileys para conectar WhatsApp via Web Multi-Device
 *
 * Endpoints:
 *   GET  /status          → Estado de la conexión
 *   GET  /qr              → QR en base64 (PNG) para escanear
 *   POST /send            → Enviar mensaje { to, message }
 *   POST /webhook/config  → Configurar webhook de mensajes entrantes
 */

import express from 'express';
import pino from 'pino';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
import qrcode from 'qrcode';

const require = createRequire(import.meta.url);
const {
  default: makeWASocket,
  DisconnectReason,
  useMultiFileAuthState,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
  isJidBroadcast,
} = require('@whiskeysockets/baileys');

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ── Config ──────────────────────────────────────────────────────────────────
const PORT         = parseInt(process.env.PORT || '3001');
const API_KEY      = process.env.WA_API_KEY || 'MysticWA2026!';
const AUTH_DIR     = process.env.AUTH_DIR || '/wa-data/auth';
const WEBHOOK_URL  = process.env.WEBHOOK_URL || '';   // URL a llamar con mensajes entrantes

// ── Estado global ────────────────────────────────────────────────────────────
let sock = null;
let qrBase64 = null;
let connectionState = 'disconnected'; // disconnected | connecting | qr | connected
let reconnectTimer = null;

// ── Logger mínimo ─────────────────────────────────────────────────────────────
const log = (level, msg, extra = {}) => {
  const line = { ts: new Date().toISOString(), level, msg, ...extra };
  console.log(JSON.stringify(line));
};

// ── Auth dir ─────────────────────────────────────────────────────────────────
fs.mkdirSync(AUTH_DIR, { recursive: true });

// ── Baileys connect ───────────────────────────────────────────────────────────
async function connect() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();
  log('info', 'Connecting WA', { version: version.join('.') });

  sock = makeWASocket({
    version,
    auth: {
      creds: state.creds,
      keys: makeCacheableSignalKeyStore(state.keys, pino({ level: 'silent' })),
    },
    printQRInTerminal: false,
    logger: pino({ level: 'silent' }),
    browser: ['Mystic', 'Chrome', '120.0.6099.130'],
    connectTimeoutMs: 60000,
    keepAliveIntervalMs: 10000,
    syncFullHistory: false,
    getMessage: async () => ({ conversation: '' }),
  });

  connectionState = 'connecting';
  qrBase64 = null;

  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      qrBase64 = await qrcode.toDataURL(qr);
      connectionState = 'qr';
      log('info', 'QR generado — escanea en /qr');
    }

    if (connection === 'close') {
      const code = lastDisconnect?.error?.output?.statusCode;
      const reason = DisconnectReason;
      const shouldReconnect = code !== reason.loggedOut;
      log('warn', 'Conexión cerrada', { code, shouldReconnect });
      connectionState = 'disconnected';
      qrBase64 = null;

      if (shouldReconnect) {
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(() => connect(), 5000);
      }
    }

    if (connection === 'open') {
      connectionState = 'connected';
      qrBase64 = null;
      log('info', 'WhatsApp conectado', { jid: sock.user?.id });
    }
  });

  sock.ev.on('creds.update', saveCreds);

  // Reenviar mensajes entrantes al webhook
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return;
    for (const msg of messages) {
      if (msg.key.fromMe) continue;
      if (isJidBroadcast(msg.key.remoteJid)) continue;

      const text = msg.message?.conversation
        || msg.message?.extendedTextMessage?.text
        || '';
      const from = msg.key.remoteJid?.replace('@s.whatsapp.net', '');

      log('info', 'Mensaje entrante', { from, text: text.slice(0, 80) });

      if (WEBHOOK_URL && text) {
        try {
          const body = JSON.stringify({ from, message: text, timestamp: msg.messageTimestamp });
          const resp = await fetch(WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body,
          });
          log('info', 'Webhook OK', { status: resp.status });
        } catch (e) {
          log('error', 'Webhook error', { error: e.message });
        }
      }
    }
  });
}

// ── Express app ───────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

// Auth middleware
const auth = (req, res, next) => {
  const key = req.headers['x-api-key'] || req.query.apikey;
  if (key !== API_KEY) return res.status(401).json({ error: 'Unauthorized' });
  next();
};

// GET /status
app.get('/status', auth, (req, res) => {
  res.json({
    state: connectionState,
    jid: sock?.user?.id || null,
    hasQR: !!qrBase64,
  });
});

// GET /qr — devuelve imagen PNG base64
app.get('/qr', auth, (req, res) => {
  if (!qrBase64) {
    return res.status(404).json({ error: 'QR no disponible. Estado: ' + connectionState });
  }
  // Si quiere JSON
  if (req.headers.accept?.includes('application/json')) {
    return res.json({ qr: qrBase64 });
  }
  // Si quiere HTML (navegador)
  res.send(`
    <html><head><title>Mystic WA — Escanea QR</title>
    <meta http-equiv="refresh" content="30">
    <style>body{font-family:sans-serif;text-align:center;padding:2rem}img{max-width:300px}</style>
    </head><body>
    <h2>Escanea con WhatsApp</h2>
    <p>Estado: <b>${connectionState}</b> | Actualiza en 30s</p>
    <img src="${qrBase64}" alt="QR"/>
    </body></html>
  `);
});

// POST /send
app.post('/send', auth, async (req, res) => {
  if (connectionState !== 'connected') {
    return res.status(503).json({ error: 'No conectado. Estado: ' + connectionState });
  }
  const { to, message } = req.body;
  if (!to || !message) return res.status(400).json({ error: 'Faltan to y message' });

  try {
    const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
    await sock.sendMessage(jid, { text: message });
    log('info', 'Mensaje enviado', { to: jid });
    res.json({ ok: true, to: jid });
  } catch (e) {
    log('error', 'Error al enviar', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

// GET / — health
app.get('/', (req, res) => res.json({ service: 'mystic-wa', state: connectionState }));

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  log('info', `mystic-wa escuchando en :${PORT}`);
  connect().catch(e => log('error', 'connect() error', { error: e.message }));
});
