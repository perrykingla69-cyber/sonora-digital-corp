/**
 * Health Check — Bots Musicos
 * Verifica el estado de todos los bots activos cada 5 minutos.
 * Envia alerta al CEO si algun bot queda en estado "unhealthy".
 *
 * Uso:
 *   import { startHealthCheck, stopHealthCheck } from './health-check.js'
 *   startHealthCheck(redis, notifyFn)
 *
 * notifyFn(message) — funcion para enviar alerta (ej: Telegram CEO)
 */

import axios from 'axios'
import crypto from 'crypto'
import { createLogger } from './logger.js'

const log = createLogger('HealthCheck')
const INTERVAL_MS = 5 * 60 * 1000  // 5 minutos
const PING_TIMEOUT = 8000           // 8 segundos por ping

// Cipher (igual que bot-factory.js)
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

// ── Ping individual a un bot ──────────────────────────────────
/**
 * Llama getMe en la Bot API para verificar que el token sigue activo.
 * Retorna true si el bot responde, false si no.
 */
async function pingBot(telegramToken) {
  try {
    const r = await axios.get(
      `https://api.telegram.org/bot${telegramToken}/getMe`,
      { timeout: PING_TIMEOUT }
    )
    return r.data?.ok === true
  } catch {
    return false
  }
}

// ── Escanear todos los bots musicos en Redis ──────────────────
/**
 * Obtiene las keys del patron bot:musico:* y retorna los datos.
 * Usa SCAN para no bloquear Redis.
 */
async function getAllMusicoBots(redis) {
  const bots = []
  let cursor = '0'
  do {
    const [nextCursor, keys] = await redis.scan(cursor, 'MATCH', 'bot:musico:*', 'COUNT', 100)
    cursor = nextCursor
    for (const key of keys) {
      // Excluir keys de owner (bot:musico:owner:*)
      if (key.includes(':owner:')) continue
      const raw = await redis.get(key)
      if (raw) {
        try {
          bots.push(JSON.parse(raw))
        } catch {
          // JSON corrupto — ignorar
        }
      }
    }
  } while (cursor !== '0')
  return bots
}

// ── Health check principal ────────────────────────────────────
/**
 * @param {object} redis      - ioredis instance
 * @param {function} notifyFn - async fn(message: string) para alertar
 */
export async function checkBotHealth(redis, notifyFn) {
  let bots
  try {
    bots = await getAllMusicoBots(redis)
  } catch (err) {
    log.error('Error obteniendo bots de Redis:', err.message)
    return
  }

  if (bots.length === 0) return

  log.info(`Verificando ${bots.length} bots musicos...`)

  const now      = new Date().toISOString()
  const failures = []

  for (const bot of bots) {
    // Solo verificar bots que tienen token configurado
    if (bot.status !== 'active' || !bot.telegram_token) continue

    const rawToken = decryptToken(bot.telegram_token)
    if (!rawToken) {
      log.warn(`No se pudo desencriptar token del bot ${bot.bot_id}`)
      continue
    }

    const healthy = await pingBot(rawToken)
    const newStatus = healthy ? 'healthy' : 'unhealthy'

    // Actualizar status en Redis solo si cambio
    if (newStatus !== bot.health_status) {
      const updated = { ...bot, health_status: newStatus, last_health_check: now }
      await redis.set(
        `bot:musico:${bot.bot_id}`,
        JSON.stringify(updated),
        'KEEPTTL'
      ).catch(e => log.warn('No se pudo actualizar health en Redis:', e.message))

      log.info(`Bot ${bot.bot_id} (${bot.bot_username}): ${bot.health_status} -> ${newStatus}`)
    } else {
      // Solo actualizar timestamp
      bot.last_health_check = now
      await redis.set(
        `bot:musico:${bot.bot_id}`,
        JSON.stringify(bot),
        'KEEPTTL'
      ).catch(() => {})
    }

    if (!healthy) {
      failures.push({ bot_id: bot.bot_id, username: bot.bot_username, artist: bot.artist_name })
    }
  }

  // Notificar si hay bots caidos
  if (failures.length > 0 && typeof notifyFn === 'function') {
    const list = failures.map(f => `- ${f.username} (artista: ${f.artist})`).join('\n')
    const msg  = `ALERTA Health Check — Bots musicos caidos:\n\n${list}\n\nVerifica tokens en Telegram BotFather.`
    try {
      await notifyFn(msg)
    } catch (notifyErr) {
      log.error('Error enviando notificacion health:', notifyErr.message)
    }
  }

  const ok = bots.filter(b => b.status === 'active').length - failures.length
  log.info(`Health check completo: ${ok} OK, ${failures.length} caidos`)
}

// ── Timer global ─────────────────────────────────────────────
let _timer = null

/**
 * Inicia el ciclo de health check cada INTERVAL_MS.
 * Es seguro llamarlo multiples veces (no duplica timers).
 */
export function startHealthCheck(redis, notifyFn) {
  if (_timer) return // ya corriendo
  log.info(`Health check iniciado (intervalo: ${INTERVAL_MS / 1000}s)`)

  // Ejecutar una vez al inicio para warm-up
  checkBotHealth(redis, notifyFn).catch(e => log.error('Health check inicial fallo:', e.message))

  _timer = setInterval(() => {
    checkBotHealth(redis, notifyFn).catch(e => log.error('Health check error:', e.message))
  }, INTERVAL_MS)

  // Evitar que el timer bloquee el graceful shutdown
  if (_timer.unref) _timer.unref()
}

export function stopHealthCheck() {
  if (_timer) {
    clearInterval(_timer)
    _timer = null
    log.info('Health check detenido.')
  }
}
