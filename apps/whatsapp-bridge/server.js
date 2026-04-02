'use strict';

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const axios = require('axios');

const PORT = process.env.PORT || 3002;
const API_BASE = process.env.API_BASE || 'http://api:8000';

const app = express();
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

/** @type {Map<string, { client: Client, status: string, qr: string|null }>} */
const sessions = new Map();

// ─── Helpers ────────────────────────────────────────────────────────────────

function broadcast(tenantId, event, data) {
  io.emit(event, { tenantId, ...data });
}

async function createSession(tenantId) {
  if (sessions.has(tenantId)) return sessions.get(tenantId);

  const state = { client: null, status: 'initializing', qr: null };
  sessions.set(tenantId, state);

  const client = new Client({
    authStrategy: new LocalAuth({ clientId: tenantId, dataPath: './sessions' }),
    puppeteer: {
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium-browser',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
      ],
      headless: true,
    },
  });

  client.on('qr', async (raw) => {
    try {
      state.qr = await qrcode.toDataURL(raw);
      state.status = 'qr';
      broadcast(tenantId, 'whatsapp-status', { status: 'qr', qr: state.qr });
    } catch (err) {
      console.error(`[${tenantId}] QR generation error:`, err.message);
    }
  });

  client.on('authenticated', () => {
    state.status = 'authenticated';
    state.qr = null;
    broadcast(tenantId, 'whatsapp-status', { status: 'authenticated' });
  });

  client.on('ready', () => {
    state.status = 'ready';
    broadcast(tenantId, 'whatsapp-status', { status: 'ready' });
    console.log(`[${tenantId}] WhatsApp ready`);
  });

  client.on('disconnected', (reason) => {
    state.status = 'disconnected';
    broadcast(tenantId, 'whatsapp-status', { status: 'disconnected', reason });
    console.log(`[${tenantId}] Disconnected:`, reason);
    sessions.delete(tenantId);
  });

  client.on('message', async (msg) => {
    if (msg.isStatus || msg.from === 'status@broadcast') return;
    try {
      const res = await axios.post(`${API_BASE}/api/v2/omnichannel/send`, {
        tenant_id: tenantId,
        channel: 'whatsapp',
        from: msg.from,
        message: msg.body,
        media_url: msg.hasMedia ? msg.mediaUrl : null,
      });
      if (res.data?.reply) {
        await msg.reply(res.data.reply);
      }
    } catch (err) {
      console.error(`[${tenantId}] Omnichannel error:`, err.message);
    }
  });

  state.client = client;
  await client.initialize();
  return state;
}

// ─── REST API ────────────────────────────────────────────────────────────────

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', sessions: sessions.size });
});

app.get('/:tenantId/status', (req, res) => {
  const s = sessions.get(req.params.tenantId);
  if (!s) return res.json({ status: 'disconnected', qr: null });
  res.json({ status: s.status, qr: s.qr });
});

app.post('/:tenantId/connect', async (req, res) => {
  try {
    const s = await createSession(req.params.tenantId);
    res.json({ status: s.status });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/:tenantId/disconnect', async (req, res) => {
  const s = sessions.get(req.params.tenantId);
  if (!s) return res.json({ status: 'not_connected' });
  try {
    await s.client.destroy();
    sessions.delete(req.params.tenantId);
    res.json({ status: 'disconnected' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/:tenantId/send', async (req, res) => {
  const s = sessions.get(req.params.tenantId);
  if (!s || s.status !== 'ready') {
    return res.status(400).json({ error: 'session_not_ready' });
  }
  const { to, message } = req.body;
  if (!to || !message) return res.status(400).json({ error: 'to and message required' });
  try {
    await s.client.sendMessage(to.includes('@') ? to : `${to}@c.us`, message);
    res.json({ status: 'sent' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── Socket.IO ───────────────────────────────────────────────────────────────

io.on('connection', (socket) => {
  socket.on('join', ({ tenantId }) => {
    socket.join(tenantId);
    const s = sessions.get(tenantId);
    socket.emit('whatsapp-status', {
      tenantId,
      status: s ? s.status : 'disconnected',
      qr: s ? s.qr : null,
    });
  });
});

// ─── Start ───────────────────────────────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`WhatsApp Bridge listening on port ${PORT}`);
});
