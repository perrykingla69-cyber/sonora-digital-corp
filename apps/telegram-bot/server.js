const { Telegraf } = require('telegraf');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const express = require('express');

const API_BASE = process.env.API_BASE || 'http://api:8000';
const DEFAULT_BOT_TOKEN = process.env.DEFAULT_BOT_TOKEN || process.env.TELEGRAM_BOT_TOKEN;

// ── OpenClaw Skills ────────────────────────────────────────────────────────────
const SKILLS_DIR = path.join(__dirname, 'skills');
let skills = [];

function loadSkills() {
  if (!fs.existsSync(SKILLS_DIR)) return;
  skills = fs.readdirSync(SKILLS_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => { try { return JSON.parse(fs.readFileSync(path.join(SKILLS_DIR, f))); } catch { return null; } })
    .filter(Boolean)
    .sort((a, b) => (b.priority || 0) - (a.priority || 0));
  console.log(`[Skills] ${skills.length} cargados: ${skills.map(s => s.name).join(', ')}`);
}

function matchSkill(message) {
  const lower = message.toLowerCase();
  for (const skill of skills) {
    if (!skill.triggers || skill.triggers.includes('*')) continue;
    if (skill.triggers.some(t => lower.includes(t.toLowerCase()))) return skill;
  }
  return skills.find(s => s.triggers?.includes('*')) || null;
}

async function invokeSkill(skill, message, tenantId) {
  const url = skill.endpoint.replace('http://api:8000', API_BASE);
  if (skill.method === 'GET') {
    const res = await axios.get(url, { timeout: 15000 });
    return skill.response_template
      ? skill.response_template.replace(/\{\{(\w+)\}\}/g, (_, k) => res.data[k] ?? '')
      : JSON.stringify(res.data);
  }
  const payload = JSON.parse(
    JSON.stringify(skill.payload || {})
      .replace(/\{\{message\}\}/g, message)
      .replace(/\{\{tenant_id\}\}/g, tenantId)
  );
  const res = await axios.post(url, payload, { timeout: 20000 });
  return res.data[skill.response_field || 'answer'] || 'Procesado.';
}

loadSkills();

// ── Bot Manager (singleton por tenant) ────────────────────────────────────────
const botInstances = new Map(); // tenantId → Telegraf instance

function createTelegrafInstance(tenantId, token) {
  const bot = new Telegraf(token);

  bot.start(ctx => ctx.reply(
    `✨ *Hola, soy Mystic*\n\nTu asistente contable inteligente, disponible las 24 horas.\n\n` +
    `Cuéntame lo que necesitas — facturas, impuestos, nómina, importaciones o cualquier duda fiscal.\n\n` +
    `_Solo escríbeme como le escribirías a un contador de confianza._`,
    { parse_mode: 'Markdown' }
  ));

  bot.command('menu', ctx => ctx.reply('¿Qué necesitas hoy?', {
    parse_mode: 'Markdown',
    reply_markup: { inline_keyboard: [
      [{ text: '📄 Necesito una factura',    callback_data: 'action_mve' }],
      [{ text: '🔍 Verificar comprobante',   callback_data: 'action_cfdi' }],
      [{ text: '📊 ¿Cómo voy con el SAT?',  callback_data: 'action_status' }],
      [{ text: '💵 Precio del dólar hoy',   callback_data: 'action_tc' }],
      [{ text: '💬 Tengo una pregunta',      callback_data: 'action_help' }],
    ]}
  }));

  bot.on('text', async ctx => {
    await ctx.sendChatAction('typing');
    const msg = ctx.message.text;
    try {
      const skill = matchSkill(msg);
      let text, actions = [];
      if (skill) {
        text = await invokeSkill(skill, msg, tenantId);
        actions = skill.actions || [];
      } else {
        const res = await axios.post(`${API_BASE}/api/brain/ask`, {
          question: msg, tenant_id: tenantId, channel: 'telegram'
        }, { timeout: 25000 });
        const d = res.data;
        text = d.answer || d.response || 'Procesando...';
        actions = d.suggested_actions || [];
      }
      if (actions.length > 0) {
        const kb = actions.map(a => [{ text: a.label || a.text, callback_data: a.callback || `action_${a.action}` }]);
        await ctx.reply(text, { parse_mode: 'Markdown', reply_markup: { inline_keyboard: kb } });
      } else {
        await ctx.reply(text, { parse_mode: 'Markdown' });
      }
    } catch (err) {
      console.error(`[${tenantId}] msg error:`, err.message);
      await ctx.reply('Algo salió mal al procesar tu consulta. Por favor intenta de nuevo en un momento.');
    }
  });

  bot.on('callback_query', async ctx => {
    const action = ctx.callbackQuery.data;
    const replies = {
      action_mve:    '📄 Perfecto. Cuéntame:\n• ¿Qué mercancía o servicio vas a facturar?\n• ¿A qué país va destinado?\n• Valor aproximado en pesos o dólares',
      action_cfdi:   '🔍 Compárteme el folio fiscal (UUID) del comprobante y lo verifico de inmediato.',
      action_status: '📊 Un momento, estoy revisando tu situación con el SAT...',
      action_tc:     '💵 Consultando el tipo de cambio oficial de hoy...',
      action_help:   '💬 Pregúntame lo que necesites: impuestos, nómina, facturas, importaciones o cualquier duda contable. Estoy aquí para ayudarte.',
    };
    if (replies[action]) await ctx.reply(replies[action]);
    await ctx.answerCbQuery();
  });

  return bot;
}

// Registrar señales una sola vez al inicio del proceso
let _activeBot = null;
process.on('SIGINT',  () => { if (_activeBot) _activeBot.stop('SIGINT');  process.exit(0); });
process.on('SIGTERM', () => { if (_activeBot) _activeBot.stop('SIGTERM'); process.exit(0); });

const MAX_RETRIES = 20; // máximo 20 intentos antes de rendirse

async function launchBot(tenantId, token, attempt = 1) {
  if (attempt > MAX_RETRIES) {
    console.error(`[${tenantId}] Max reintentos (${MAX_RETRIES}) alcanzado. Bot detenido.`);
    return;
  }

  // Detener instancia anterior y esperar a que cierre su conexión HTTP con Telegram
  const prev = botInstances.get(tenantId);
  if (prev) {
    try { await prev.stop(); } catch {}
    botInstances.delete(tenantId);
    // Esperar 35s para que Telegram libere la sesión de polling
    await new Promise(r => setTimeout(r, 35000));
  }

  const bot = createTelegrafInstance(tenantId, token);
  botInstances.set(tenantId, bot);
  _activeBot = bot;

  bot.launch().then(() => {
    console.log(`[${tenantId}] Bot conectado a Telegram ✅`);
  }).catch(async err => {
    const is409 = err.response?.error_code === 409;
    const isNet = err.code === 'ETIMEDOUT' || err.code === 'ECONNREFUSED' || err.type === 'system';
    if (is409 || isNet) {
      // En 409 esperar 35s extra para asegurar que Telegram libere la sesión
      const wait = is409 ? 35000 : Math.min(60000, attempt * 8000);
      console.warn(`[${tenantId}] ${is409 ? '409 Conflict' : 'Red timeout'} → retry en ${wait/1000}s (intento ${attempt}/${MAX_RETRIES})`);
      setTimeout(() => launchBot(tenantId, token, attempt + 1), wait);
    } else {
      console.error(`[${tenantId}] Error fatal:`, err.message);
    }
  });
}

// ── REST API ───────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

app.post('/:tenantId/start', (req, res) => {
  const { tenantId } = req.params;
  const token = req.body.token || DEFAULT_BOT_TOKEN;
  if (!token) return res.status(400).json({ error: 'Token requerido' });
  launchBot(tenantId, token);
  res.json({ success: true, message: `Bot ${tenantId} iniciando` });
});

app.post('/:tenantId/stop', (req, res) => {
  const bot = botInstances.get(req.params.tenantId);
  if (bot) { try { bot.stop(); } catch {} botInstances.delete(req.params.tenantId); }
  res.json({ success: true });
});

app.get('/:tenantId/status', (req, res) => {
  res.json({ tenantId: req.params.tenantId, active: botInstances.has(req.params.tenantId) });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', activeBots: botInstances.size, skills: skills.length });
});

// Auto-start
if (DEFAULT_BOT_TOKEN) {
  launchBot('default', DEFAULT_BOT_TOKEN);
  console.log('[default] Bot iniciando...');
}

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => console.log(`🤖 Telegram Bot Manager en puerto ${PORT}`));
