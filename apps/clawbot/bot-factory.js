/**
 * Bot Factory — Endpoints REST para crear/gestionar bots
 * Se integra al servidor express de ClawBot (index.js)
 *
 * Uso: importar y registrar en el app express de index.js:
 *   import { registerBotFactoryRoutes } from './bot-factory.js'
 *   registerBotFactoryRoutes(app, redis)
 */

import axios from 'axios'
import crypto from 'crypto'

const API_URL = process.env.API_URL || 'http://hermes-api:8000'

/**
 * Middleware simple de auth — verifica Bearer JWT contra hermes-api
 */
async function requireAuth(req, res, next) {
  const auth = req.headers.authorization
  if (!auth?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token requerido' })
  }
  const token = auth.split(' ')[1]
  try {
    const r = await axios.get(`${API_URL}/api/v1/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 5000,
    })
    req.currentUser = r.data.user
    req.jwtToken = token
    next()
  } catch {
    return res.status(401).json({ error: 'Token inválido o expirado' })
  }
}

/**
 * Registra todos los endpoints de Bot Factory en el app express existente
 */
export function registerBotFactoryRoutes(app, redis) {
  // ── POST /api/v1/bots/register ────────────────────────────────
  // Endpoint interno: hermes-api llama esto para registrar un bot
  app.post('/api/v1/bots/register', async (req, res) => {
    const secret = req.headers['x-internal-secret']
    if (secret !== process.env.INTERNAL_SECRET) {
      return res.status(401).json({ error: 'No autorizado' })
    }
    const { bot_id, agent_id, tenant_id, channel, webhook_url, config } = req.body

    try {
      // Guardar mapeo bot_id → agent_id en Redis
      const key = `bot:${bot_id}`
      await redis.setex(key, 86400 * 365, JSON.stringify({
        bot_id,
        agent_id,
        tenant_id,
        channel,
        webhook_url,
        config: config || {},
        registered_at: new Date().toISOString(),
      }))

      // Si es Telegram, generar webhook path
      if (channel === 'telegram') {
        const webhookPath = `/webhook/telegram/${bot_id}`
        await redis.set(`webhook:path:${webhookPath}`, bot_id)
      }

      console.log(`[BotFactory] Bot ${bot_id} registrado (${channel}) → agent ${agent_id}`)
      res.json({ ok: true, bot_id, channel })
    } catch (err) {
      console.error('[BotFactory] Error registrando bot:', err.message)
      res.status(500).json({ error: err.message })
    }
  })

  // ── POST /api/v1/bots/:bot_id/set-token ───────────────────────
  // El usuario configura el token de Telegram de su bot
  app.post('/api/v1/bots/:bot_id/set-token', requireAuth, async (req, res) => {
    const { bot_id } = req.params
    const { token: telegramToken } = req.body

    if (!telegramToken || telegramToken.length < 20) {
      return res.status(400).json({ error: 'Token inválido' })
    }

    try {
      // Verificar el token con Telegram
      const tgRes = await axios.get(
        `https://api.telegram.org/bot${telegramToken}/getMe`,
        { timeout: 10000 }
      )
      const botInfo = tgRes.data.result

      // Registrar webhook en Telegram
      const webhookUrl = `https://sonoradigitalcorp.com/webhook/telegram/${bot_id}`
      await axios.post(
        `https://api.telegram.org/bot${telegramToken}/setWebhook`,
        { url: webhookUrl },
        { timeout: 10000 }
      )

      // Guardar token en Redis (encriptado)
      const key = `bot:${bot_id}`
      const existing = await redis.get(key)
      if (existing) {
        const data = JSON.parse(existing)
        data.telegram_token = _encryptToken(telegramToken)
        data.bot_username = botInfo.username
        data.status = 'active'
        await redis.set(key, JSON.stringify(data))
      }

      // Notificar a hermes-api para actualizar DB
      await axios.post(`${API_URL}/api/v1/bots/${bot_id}/activate`, {
        channel_id: String(botInfo.id),
        bot_username: botInfo.username,
        webhook_url: webhookUrl,
      }, {
        headers: { 'X-Internal-Secret': process.env.INTERNAL_SECRET },
        timeout: 5000,
      }).catch(() => {}) // No crítico si falla

      res.json({
        ok: true,
        bot_username: `@${botInfo.username}`,
        webhook_url: webhookUrl,
        message: `Bot @${botInfo.username} activado. ¡Ya está recibiendo mensajes!`,
      })
    } catch (err) {
      if (err.response?.status === 401) {
        return res.status(400).json({ error: 'Token de Telegram inválido' })
      }
      console.error('[BotFactory] Error activando token:', err.message)
      res.status(500).json({ error: err.message })
    }
  })

  // ── POST /webhook/telegram/:bot_id ────────────────────────────
  // Recibe mensajes Telegram para bots creados por usuarios
  app.post('/webhook/telegram/:bot_id', async (req, res) => {
    res.sendStatus(200) // Responder rápido a Telegram

    const { bot_id } = req.params
    const update = req.body

    try {
      const key = `bot:${bot_id}`
      const botDataRaw = await redis.get(key)
      if (!botDataRaw) {
        console.warn(`[BotFactory] Bot ${bot_id} no encontrado en Redis`)
        return
      }
      const botData = JSON.parse(botDataRaw)
      const { agent_id, tenant_id, telegram_token } = botData

      // Extraer mensaje
      const message = update.message
      if (!message?.text || !telegram_token) return

      const chatId = message.chat.id
      const text = message.text

      // Dedup
      const dedupKey = `dedup:tg:${bot_id}:${message.message_id}`
      const exists = await redis.get(dedupKey)
      if (exists) return
      await redis.setex(dedupKey, 60, '1')

      // Llamar al agente
      const convKey = `conv:bot:${bot_id}:${chatId}`
      const convId = await redis.get(convKey)

      // Obtener token del tenant para llamar a la API del agente
      const agentRes = await axios.post(
        `${API_URL}/api/v1/agents/${agent_id}/chat-public`,
        {
          message: text,
          user_id: String(chatId),
          tenant_id,
          ...(convId && { conversation_id: convId }),
        },
        { timeout: 30000 }
      )

      const reply = agentRes.data.reply || agentRes.data.response || 'Lo siento, no pude procesar tu mensaje.'
      if (agentRes.data.conversation_id) {
        await redis.setex(convKey, 3600 * 4, agentRes.data.conversation_id)
      }

      // Enviar respuesta a Telegram
      const decryptedToken = _decryptToken(telegram_token)
      await axios.post(
        `https://api.telegram.org/bot${decryptedToken}/sendMessage`,
        { chat_id: chatId, text: reply },
        { timeout: 10000 }
      )

    } catch (err) {
      console.error(`[BotFactory] Error procesando webhook ${bot_id}:`, err.message)
    }
  })

  // ── GET /api/v1/bots/:bot_id/health (interno) ─────────────────
  app.get('/api/v1/bots/:bot_id/clawbot-health', async (req, res) => {
    const { bot_id } = req.params
    const key = `bot:${bot_id}`
    const raw = await redis.get(key)
    if (!raw) return res.status(404).json({ error: 'Bot no encontrado' })
    const data = JSON.parse(raw)
    res.json({
      bot_id,
      channel: data.channel,
      status: data.status || 'created',
      bot_username: data.bot_username,
      registered_at: data.registered_at,
    })
  })

  console.log('[BotFactory] Rutas registradas: /api/v1/bots/*, /webhook/telegram/:id')
}

// ── Crypto helpers ────────────────────────────────────────────
const CIPHER_KEY = Buffer.from(
  (process.env.ENCRYPTION_KEY || 'sonora-default-key-32chars-padded!!').padEnd(32).slice(0, 32)
)

function _encryptToken(token) {
  const iv = crypto.randomBytes(16)
  const cipher = crypto.createCipheriv('aes-256-cbc', CIPHER_KEY, iv)
  const encrypted = Buffer.concat([cipher.update(token, 'utf8'), cipher.final()])
  return iv.toString('hex') + ':' + encrypted.toString('hex')
}

function _decryptToken(encrypted) {
  const [ivHex, dataHex] = encrypted.split(':')
  const iv = Buffer.from(ivHex, 'hex')
  const decipher = crypto.createDecipheriv('aes-256-cbc', CIPHER_KEY, iv)
  return Buffer.concat([decipher.update(Buffer.from(dataHex, 'hex')), decipher.final()]).toString('utf8')
}
