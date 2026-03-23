const { Telegraf } = require('telegraf');
const axios = require('axios');

const API_BASE = process.env.API_BASE || 'http://api:8000';
const DEFAULT_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;

const bots = new Map();

class TelegramBot {
  constructor(tenantId, token) {
    this.tenantId = tenantId;
    this.token = token;
    this.bot = new Telegraf(token);
    this.setupHandlers();
  }

  setupHandlers() {
    this.bot.start((ctx) => {
      ctx.reply(
        `🧠 *Bienvenido a Mystic Asistente*\n\n` +
        `Tu contador fiscal inteligente 24/7.\n\n` +
        `¿Qué puedo hacer por ti hoy?\n` +
        `• Generar MVE\n• Consultar CFDI\n• Calcular impuestos\n• Recordatorios SAT\n\n` +
        `Escribe tu consulta o usa /menu`,
        { parse_mode: 'Markdown' }
      );
    });

    this.bot.command('menu', (ctx) => {
      ctx.reply('⚡ *Acciones rápidas:*', {
        parse_mode: 'Markdown',
        reply_markup: {
          inline_keyboard: [
            [{ text: '📄 Generar MVE',      callback_data: 'action_mve' }],
            [{ text: '🔍 Validar CFDI',     callback_data: 'action_cfdi' }],
            [{ text: '📊 Mi estado fiscal', callback_data: 'action_status' }],
            [{ text: '❓ Ayuda',            callback_data: 'action_help' }],
          ]
        }
      });
    });

    this.bot.on('text', async (ctx) => {
      await ctx.sendChatAction('typing');
      try {
        const response = await axios.post(`${API_BASE}/api/v2/omnichannel/send`, {
          channel: 'telegram',
          user_id: ctx.from.id.toString(),
          message: ctx.message.text,
          metadata: {
            tenant_id: this.tenantId,
            username:   ctx.from.username,
            first_name: ctx.from.first_name,
          }
        });

        const data = response.data;
        const text = data.answer || data.response || 'Procesando tu consulta...';
        const actions = data.suggested_actions || [];

        if (actions.length > 0) {
          const keyboard = actions.map(a => [{ text: a.text, callback_data: `action_${a.action}` }]);
          await ctx.reply(text, { reply_markup: { inline_keyboard: keyboard } });
        } else {
          await ctx.reply(text);
        }
      } catch (err) {
        console.error(`[${this.tenantId}] Error:`, err.message);
        await ctx.reply('Lo siento, hubo un error procesando tu consulta. Intenta de nuevo.');
      }
    });

    this.bot.on('callback_query', async (ctx) => {
      const action = ctx.callbackQuery.data;
      const replies = {
        action_mve:    '📄 Para generar tu MVE necesito:\n1. Valor de la mercancía\n2. País de origen\n3. INCOTERM\n\n¿Tienes esta información?',
        action_cfdi:   '🔍 Envíame el UUID del CFDI (formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)',
        action_status: '📊 Consultando tu estado fiscal...',
        action_help:   '💡 Puedes preguntarme cualquier cosa fiscal: IVA, ISR, IMSS, facturas, importaciones, etc.',
      };
      if (replies[action]) await ctx.reply(replies[action]);
      await ctx.answerCbQuery();
    });

    this.bot.launch();
    console.log(`[${this.tenantId}] Telegram bot iniciado`);
  }

  stop() { this.bot.stop('SIGTERM'); }
}

// ── API REST ──────────────────────────────────────────────────────────────────

const express = require('express');
const app = express();
app.use(express.json());

app.post('/:tenantId/start', (req, res) => {
  const { tenantId } = req.params;
  const token = req.body.token || DEFAULT_BOT_TOKEN;

  if (!token) return res.status(400).json({ success: false, error: 'Token requerido' });
  if (bots.has(tenantId)) return res.json({ success: true, message: 'Bot ya activo' });

  const bot = new TelegramBot(tenantId, token);
  bots.set(tenantId, bot);
  res.json({ success: true, message: 'Bot iniciado' });
});

app.post('/:tenantId/stop', (req, res) => {
  const bot = bots.get(req.params.tenantId);
  if (bot) { bot.stop(); bots.delete(req.params.tenantId); }
  res.json({ success: true });
});

app.get('/:tenantId/status', (req, res) => {
  res.json({ tenantId: req.params.tenantId, active: bots.has(req.params.tenantId) });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', activeBots: bots.size });
});

// Auto-iniciar el bot por defecto al arrancar
if (DEFAULT_BOT_TOKEN) {
  new TelegramBot('default', DEFAULT_BOT_TOKEN);
  bots.set('default', bots.get('default'));
  console.log('[default] Bot iniciado con TELEGRAM_BOT_TOKEN');
}

const PORT = process.env.PORT || 3003;
app.listen(PORT, () => console.log(`🤖 Telegram Bot Manager en puerto ${PORT}`));
