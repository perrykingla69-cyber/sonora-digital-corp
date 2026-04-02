/**
 * CLAWBOT — Gateway Multi-canal
 * Conecta Telegram CEO + Telegram Público + WhatsApp
 * con HERMES (orquestador) y MYSTIC (sombra)
 *
 * Inspirado en OpenClaw/ClawdBot skill architecture
 */

import { Telegraf, session } from 'telegraf'
import axios from 'axios'
import Redis from 'ioredis'
import express from 'express'
import { createHmac } from 'crypto'
import 'dotenv/config'

const redis = new Redis(process.env.REDIS_URL)
const API = process.env.API_URL
const app = express()
app.use(express.json())

// ── BOT CEO (Luis Daniel — privado) ───────────────────────────
const ceoBot = new Telegraf(process.env.TELEGRAM_TOKEN_CEO)

ceoBot.use(session())

// Middleware: solo el CEO puede usar este bot
ceoBot.use(async (ctx, next) => {
  const chatId = String(ctx.from?.id)
  if (chatId !== process.env.CEO_CHAT_ID) {
    await ctx.reply('🚫 Acceso denegado.')
    return
  }
  return next()
})

ceoBot.command('start', async (ctx) => {
  await ctx.reply(
    `☀️ *HERMES OS — Control Centro*\n\n` +
    `Bienvenido, Luis Daniel.\n\n` +
    `Comandos disponibles:\n` +
    `/hermes — Hablar con HERMES\n` +
    `/mystic — Análisis estratégico MYSTIC\n` +
    `/status — Estado del sistema\n` +
    `/tenants — Ver tenants activos`,
    { parse_mode: 'Markdown' }
  )
})

ceoBot.command('status', async (ctx) => {
  try {
    const res = await axios.get(`${API}/health`)
    const msg = `✅ *Sistema operativo*\n\n` +
      `• API: ${res.status === 200 ? '🟢' : '🔴'}\n` +
      `• Tiempo: ${new Date().toLocaleString('es-MX')}`
    await ctx.reply(msg, { parse_mode: 'Markdown' })
  } catch {
    await ctx.reply('🔴 API no responde')
  }
})

ceoBot.command('mystic', async (ctx) => {
  ctx.session = ctx.session || {}
  ctx.session.mode = 'mystic'
  await ctx.reply(
    `🌑 *MYSTIC activo*\n\nAnalizo en la sombra. ¿Qué necesitas que vea?`,
    { parse_mode: 'Markdown' }
  )
})

ceoBot.command('hermes', async (ctx) => {
  ctx.session = ctx.session || {}
  ctx.session.mode = 'hermes'
  await ctx.reply(
    `☀️ *HERMES activo*\n\nListo para coordinar. ¿Qué necesitas?`,
    { parse_mode: 'Markdown' }
  )
})

// Procesar mensajes del CEO
ceoBot.on('text', async (ctx) => {
  const mode = ctx.session?.mode || 'hermes'
  const text = ctx.message.text
  const msgId = ctx.message.message_id

  await ctx.sendChatAction('typing')

  try {
    // Cache: evitar procesar el mismo mensaje dos veces
    const cacheKey = `msg:ceo:${msgId}`
    if (await redis.get(cacheKey)) return
    await redis.setex(cacheKey, 60, '1')

    // Obtener token CEO del sistema (tenant especial)
    const ceoToken = await getCeoToken()
    const endpoint = mode === 'mystic' ? '/api/v1/agents/mystic/analyze' : '/api/v1/agents/hermes/chat'

    const convKey = `conv:ceo:${mode}`
    const convId = await redis.get(convKey)

    const payload = {
      message: text,
      channel: 'telegram',
      ...(convId && { conversation_id: convId }),
    }

    const res = await axios.post(`${API}${endpoint}`, payload, {
      headers: { Authorization: `Bearer ${ceoToken}` },
      timeout: 30000,
    })

    // Guardar conversation_id para continuidad
    if (res.data.conversation_id) {
      await redis.setex(convKey, 3600 * 24, res.data.conversation_id)
    }

    const prefix = mode === 'mystic' ? '🌑 *MYSTIC:*\n\n' : '☀️ *HERMES:*\n\n'
    await ctx.reply(prefix + res.data.response, { parse_mode: 'Markdown' })
  } catch (err) {
    console.error('CEO bot error:', err.message)
    await ctx.reply('⚠️ Error procesando tu mensaje. Reintentando...')
  }
})


// ── BOT PÚBLICO (clientes) ────────────────────────────────────
const publicBot = new Telegraf(process.env.TELEGRAM_TOKEN_PUBLIC)

publicBot.command('start', async (ctx) => {
  await ctx.reply(
    `Hola 👋 Soy el asistente de *Sonora Digital Corp*.\n\n` +
    `Te ayudo con contabilidad, fiscal y tu empresa. ¿En qué puedo ayudarte hoy?`,
    { parse_mode: 'Markdown' }
  )
})

publicBot.on('text', async (ctx) => {
  const chatId = String(ctx.chat.id)
  const text = ctx.message.text
  const msgId = ctx.message.message_id

  await ctx.sendChatAction('typing')

  try {
    const cacheKey = `msg:pub:${chatId}:${msgId}`
    if (await redis.get(cacheKey)) return
    await redis.setex(cacheKey, 60, '1')

    // Resolver tenant por chat_id (el usuario debe haberse registrado)
    const tokenKey = `token:telegram:${chatId}`
    let token = await redis.get(tokenKey)

    if (!token) {
      await ctx.reply(
        '⚠️ No encontré tu cuenta. Contacta a tu asesor para activar tu acceso.'
      )
      return
    }

    const convKey = `conv:pub:${chatId}`
    const convId = await redis.get(convKey)

    const res = await axios.post(
      `${API}/api/v1/agents/hermes/chat`,
      {
        message: text,
        channel: 'telegram',
        ...(convId && { conversation_id: convId }),
      },
      {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 20000,
      }
    )

    if (res.data.conversation_id) {
      await redis.setex(convKey, 3600 * 4, res.data.conversation_id)
    }

    await ctx.reply(res.data.response)
  } catch (err) {
    console.error('Public bot error:', err.message)
    await ctx.reply('Disculpa, tuve un problema. Intenta en unos momentos.')
  }
})


// ── HERMES AGENT BOT (alertas proactivas) ─────────────────────
const hermesBot = new Telegraf(process.env.TELEGRAM_TOKEN_HERMES)

hermesBot.command('start', async (ctx) => {
  await ctx.reply('☀️ HERMES conectado. Recibirás alertas y reportes aquí.')
})

// API interna para que el backend envíe alertas via HERMES
app.post('/internal/notify', async (req, res) => {
  const { chat_id, message, parse_mode = 'Markdown', bot = 'hermes' } = req.body
  const secret = req.headers['x-internal-secret']

  if (secret !== process.env.INTERNAL_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  try {
    const bot_instance = bot === 'ceo' ? ceoBot : hermesBot
    await bot_instance.telegram.sendMessage(chat_id, message, { parse_mode })
    res.json({ ok: true })
  } catch (err) {
    res.status(500).json({ error: err.message })
  }
})

// ── MYSTIC AGENT BOT (alertas estratégicas) ───────────────────
const mysticBot = new Telegraf(process.env.TELEGRAM_TOKEN_MYSTIC)

mysticBot.command('start', async (ctx) => {
  await ctx.reply('🌑 MYSTIC conectado. Recibirás análisis estratégicos aquí.')
})

// Health
app.get('/health', (_, res) => res.json({ status: 'ok', service: 'clawbot' }))


// ── HELPERS ───────────────────────────────────────────────────
async function getCeoToken() {
  const key = 'ceo:api:token'
  let token = await redis.get(key)
  if (token) return token

  // Login automático con credenciales CEO
  const res = await axios.post(`${API}/api/v1/auth/login`, {
    email: process.env.CEO_EMAIL,
    password: process.env.CEO_PASSWORD,
    tenant_slug: process.env.CEO_TENANT_SLUG,
  })

  token = res.data.access_token
  await redis.setex(key, 3000, token) // cache 50 minutos
  return token
}


// ── ARRANQUE ─────────────────────────────────────────────────
async function main() {
  // Webhooks o polling según entorno
  const IS_PROD = process.env.NODE_ENV === 'production'

  if (IS_PROD) {
    // Webhook mode en producción
    const domain = process.env.DOMAIN || 'sonoradigitalcorp.com'

    await ceoBot.telegram.setWebhook(`https://${domain}/bots/ceo/${process.env.TELEGRAM_TOKEN_CEO}`)
    await publicBot.telegram.setWebhook(`https://${domain}/bots/public/${process.env.TELEGRAM_TOKEN_PUBLIC}`)
    // hermesBot sin webhook — hermes_agent usa polling
    await mysticBot.telegram.setWebhook(`https://${domain}/bots/mystic/${process.env.TELEGRAM_TOKEN_MYSTIC}`)

    app.post(`/bots/ceo/${process.env.TELEGRAM_TOKEN_CEO}`, (req, res) => {
      ceoBot.handleUpdate(req.body)
      res.sendStatus(200)
    })
    app.post(`/bots/public/${process.env.TELEGRAM_TOKEN_PUBLIC}`, (req, res) => {
      publicBot.handleUpdate(req.body)
      res.sendStatus(200)
    })
    // hermesBot: sin ruta webhook, hermes_agent hace polling
    app.post(`/bots/mystic/${process.env.TELEGRAM_TOKEN_MYSTIC}`, (req, res) => {
      mysticBot.handleUpdate(req.body)
      res.sendStatus(200)
    })
  } else {
    // Polling en desarrollo
    ceoBot.launch()
    publicBot.launch()
    hermesBot.launch()
    mysticBot.launch()
    console.log('🤖 Bots en modo polling (desarrollo)')
  }

  app.listen(3003, () => console.log('🌐 ClawBot gateway :3003'))
  console.log('☀️  HERMES | 🌑 MYSTIC | 🤖 ClawBot — Online')
}

main().catch(console.error)

// Graceful shutdown
process.once('SIGINT', () => { ceoBot.stop(); publicBot.stop(); hermesBot.stop(); mysticBot.stop() })
process.once('SIGTERM', () => { ceoBot.stop(); publicBot.stop(); hermesBot.stop(); mysticBot.stop() })
