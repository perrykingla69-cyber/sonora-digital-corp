/**
 * Webhook Telegram — Musicos
 * Recibe actualizaciones de Telegram para bots de artistas.
 *
 * Registro en express:
 *   import { registerMusicosWebhook } from './webhooks/telegram-webhook.js'
 *   registerMusicosWebhook(app, redis)
 *
 * Endpoint: POST /webhook/telegram/:bot_id
 *
 * NOTA: Este archivo gestiona SOLO los bots tipo "musico".
 * Los bots CEO/Publico/HERMES/MYSTIC siguen en index.js.
 */

import axios from 'axios'
import crypto from 'crypto'
import { MusicosBotHandler } from '../handlers/musicos-bot-handler.js'
import { createLogger } from '../logger.js'

const log = createLogger('TelegramWebhook')
const API_URL = process.env.API_URL || 'http://hermes-api:8000'

// Cache en memoria de handlers activos: bot_id → MusicosBotHandler
// Evita reinstanciar el handler en cada request
const handlerCache = new Map()
const HANDLER_TTL_MS = 5 * 60 * 1000 // 5 minutos sin uso → evictar

// ── Validacion de firma Telegram (X-Telegram-Bot-Api-Secret-Token) ───────────
/**
 * Verifica el header de firma si el bot tiene secretWebhookToken configurado.
 * Si no hay token configurado, se omite la verificacion (backward compat).
 */
function verifyTelegramSignature(req, secretWebhookToken) {
  if (!secretWebhookToken) return true // no configurado → permitir
  const receivedToken = req.headers['x-telegram-bot-api-secret-token']
  if (!receivedToken) return false
  // Comparacion en tiempo constante para evitar timing attacks
  const a = Buffer.from(receivedToken)
  const b = Buffer.from(secretWebhookToken)
  if (a.length !== b.length) return false
  return crypto.timingSafeEqual(a, b)
}

// ── Cipher helpers (mismos que bot-factory.js / routes) ──────────────────────
const CIPHER_KEY = Buffer.from(
  (process.env.ENCRYPTION_KEY || 'sonora-default-key-32chars-padded!!').padEnd(32).slice(0, 32)
)

function decryptToken(encrypted) {
  try {
    const [ivHex, dataHex] = encrypted.split(':')
    const iv = Buffer.from(ivHex, 'hex')
    const decipher = crypto.createDecipheriv('aes-256-cbc', CIPHER_KEY, iv)
    return Buffer.concat([
      decipher.update(Buffer.from(dataHex, 'hex')),
      decipher.final(),
    ]).toString('utf8')
  } catch {
    return null
  }
}

// ── Handler cache helpers ─────────────────────────────────────────────────────
function getCachedHandler(bot_id) {
  const entry = handlerCache.get(bot_id)
  if (!entry) return null
  // Actualizar timestamp de ultimo uso
  entry.lastUsed = Date.now()
  return entry.handler
}

function cacheHandler(bot_id, handler) {
  handlerCache.set(bot_id, { handler, lastUsed: Date.now() })
}

// Evictar handlers no usados cada 10 minutos
setInterval(() => {
  const now = Date.now()
  for (const [id, entry] of handlerCache) {
    if (now - entry.lastUsed > HANDLER_TTL_MS) {
      handlerCache.delete(id)
      log.info(`Handler evictado: ${id}`)
    }
  }
}, 10 * 60 * 1000)

// ── Registro de ruta ──────────────────────────────────────────────────────────
export function registerMusicosWebhook(app, redis) {

  /**
   * POST /webhook/telegram/:bot_id
   *
   * 1. Responde 200 a Telegram INMEDIATAMENTE (Telegram reintenta si demoras >5s)
   * 2. Valida firma opcional
   * 3. Obtiene bot data desde Redis
   * 4. Instancia (o recupera del cache) el MusicosBotHandler
   * 5. Despacha el update de forma asincrona
   */
  app.post('/webhook/musico/telegram/:bot_id', async (req, res) => {
    // Responder a Telegram lo antes posible
    res.sendStatus(200)

    const { bot_id } = req.params
    const update     = req.body

    // Ignorar pings vacios de Telegram
    if (!update || typeof update !== 'object') return

    try {
      // Obtener datos del bot desde Redis
      const raw = await redis.get(`bot:musico:${bot_id}`)
      if (!raw) {
        log.warn(`Bot musico no encontrado en Redis: ${bot_id}`)
        return
      }
      const botData = JSON.parse(raw)

      // Verificar firma webhook (si esta configurada)
      if (!verifyTelegramSignature(req, botData.webhook_secret)) {
        log.warn(`Firma Telegram invalida para bot ${bot_id}`)
        return
      }

      // El bot debe estar activo (no en pending_token)
      if (botData.status !== 'active') {
        log.warn(`Bot ${bot_id} no esta activo (status: ${botData.status})`)
        return
      }

      // Obtener o crear el handler cacheado
      let handler = getCachedHandler(bot_id)
      if (!handler) {
        if (!botData.telegram_token) {
          log.warn(`Bot ${bot_id} sin token configurado`)
          return
        }
        const rawToken = decryptToken(botData.telegram_token)
        if (!rawToken) {
          log.error(`No se pudo desencriptar token del bot ${bot_id}`)
          return
        }

        handler = new MusicosBotHandler(
          rawToken,
          botData.agent_id,
          botData.artist_name,
          botData.config,
          redis,
          bot_id
        )
        cacheHandler(bot_id, handler)
        log.info(`Handler creado para bot ${bot_id} (${botData.bot_username})`)
      }

      // Actualizar timestamp de ultimo webhook en Redis (fuego y olvida)
      redis.set(
        `bot:musico:${bot_id}`,
        JSON.stringify({ ...botData, last_webhook_at: new Date().toISOString() }),
        'KEEPTTL'
      ).catch(() => {})

      // Despachar update
      await handler.handleUpdate(update)

    } catch (err) {
      // No exponer detalles del error hacia fuera; ya respondimos 200
      log.error(`Error procesando webhook bot=${bot_id}:`, err.message)
    }
  })

  // ── Alias legacy por compatibilidad con set-token que usa /webhook/telegram/:id ──
  // (bot-factory.js registra /webhook/telegram/:bot_id para bots genericos)
  // Los bots musico tambien aceptan su path canonico
  app.post('/webhook/telegram/musico/:bot_id', (req, res, next) => {
    req.params.bot_id = req.params.bot_id
    // Redirigir internamente al handler principal
    req.url = `/webhook/musico/telegram/${req.params.bot_id}`
    next()
  })

  log.info('Webhook musicos registrado: POST /webhook/musico/telegram/:bot_id')
}
