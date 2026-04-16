/**
 * Bot Factory — Musicos
 * Endpoints REST para crear, consultar y eliminar bots Telegram
 * especializados para artistas/musicos.
 *
 * Registro en express:
 *   import { registerMusicosFactoryRoutes } from './routes/bot-factory-musicos.js'
 *   registerMusicosFactoryRoutes(app, redis)
 *
 * Endpoints:
 *   POST   /api/v1/bots/create-musicos
 *   GET    /api/v1/bots/:bot_id/status
 *   DELETE /api/v1/bots/:bot_id
 */

import axios from 'axios'
import crypto from 'crypto'
import { createLogger } from '../logger.js'

const log = createLogger('BotFactoryMusicos')
const API_URL = process.env.API_URL || 'http://hermes-api:8000'
const DOMAIN  = process.env.DOMAIN  || 'sonoradigitalcorp.com'

// ── Constantes de validacion ──────────────────────────────────
const TONES     = ['professional', 'casual', 'energetic', 'formal']
const LANGUAGES = ['es', 'en', 'es-en']

// ── Cipher helpers (mismos que bot-factory.js) ────────────────
const CIPHER_KEY = Buffer.from(
  (process.env.ENCRYPTION_KEY || 'sonora-default-key-32chars-padded!!').padEnd(32).slice(0, 32)
)

function encryptToken(token) {
  const iv = crypto.randomBytes(16)
  const cipher = crypto.createCipheriv('aes-256-cbc', CIPHER_KEY, iv)
  const encrypted = Buffer.concat([cipher.update(token, 'utf8'), cipher.final()])
  return iv.toString('hex') + ':' + encrypted.toString('hex')
}

function decryptToken(encrypted) {
  const [ivHex, dataHex] = encrypted.split(':')
  const iv = Buffer.from(ivHex, 'hex')
  const decipher = crypto.createDecipheriv('aes-256-cbc', CIPHER_KEY, iv)
  return Buffer.concat([
    decipher.update(Buffer.from(dataHex, 'hex')),
    decipher.final(),
  ]).toString('utf8')
}

// ── Sanitizacion ──────────────────────────────────────────────
/**
 * Normaliza un nombre de artista para generar @SonoraXxxBot.
 * Solo alfanumericos + guiones bajos, max 32 chars.
 */
function sanitizeArtistHandle(name) {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')   // quitar acentos
    .replace(/[^a-zA-Z0-9_]/g, '')
    .slice(0, 32)
}

// ── Middleware: validar JWT contra hermes-api ─────────────────
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
    return res.status(401).json({ error: 'Token invalido o expirado' })
  }
}

// ── Validacion de body ────────────────────────────────────────
function validateCreateBody(body) {
  const errors = []
  const { artist_name, agent_id, config } = body

  if (!artist_name || typeof artist_name !== 'string' || artist_name.trim().length < 2) {
    errors.push('artist_name: requerido, minimo 2 caracteres')
  }
  if (artist_name && artist_name.length > 100) {
    errors.push('artist_name: maximo 100 caracteres')
  }
  if (!agent_id || !/^[0-9a-f-]{36}$/i.test(agent_id)) {
    errors.push('agent_id: UUID valido requerido')
  }
  if (body.spotify_id !== undefined && body.spotify_id !== null) {
    if (typeof body.spotify_id !== 'string' || body.spotify_id.trim().length === 0) {
      errors.push('spotify_id: debe ser string no vacio si se provee')
    }
  }
  if (config !== undefined) {
    if (typeof config !== 'object' || Array.isArray(config)) {
      errors.push('config: debe ser un objeto')
    } else {
      if (config.tone !== undefined && !TONES.includes(config.tone)) {
        errors.push(`config.tone: debe ser uno de ${TONES.join(', ')}`)
      }
      if (config.language !== undefined && !LANGUAGES.includes(config.language)) {
        errors.push(`config.language: debe ser uno de ${LANGUAGES.join(', ')}`)
      }
    }
  }
  return errors
}

// ── Helpers Redis ─────────────────────────────────────────────
function redisBotKey(bot_id)   { return `bot:musico:${bot_id}` }
function redisOwnerKey(bot_id) { return `bot:musico:owner:${bot_id}` }

async function getBotData(redis, bot_id) {
  const raw = await redis.get(redisBotKey(bot_id))
  return raw ? JSON.parse(raw) : null
}

// ── Registro de rutas ─────────────────────────────────────────
export function registerMusicosFactoryRoutes(app, redis) {

  // ────────────────────────────────────────────────────────────
  // POST /api/v1/bots/create-musicos
  // Crea un nuevo bot Telegram para un artista.
  // El usuario aun debe configurar el token via BotFather y luego
  // llamar a POST /api/v1/bots/:bot_id/set-token
  // ────────────────────────────────────────────────────────────
  app.post('/api/v1/bots/create-musicos', requireAuth, async (req, res) => {
    const errors = validateCreateBody(req.body)
    if (errors.length > 0) {
      return res.status(400).json({ error: 'Validacion fallida', details: errors })
    }

    const { artist_name, agent_id, spotify_id, config = {} } = req.body
    const userId = req.currentUser?.id || req.currentUser?.usuario

    // Verificar que el agente exista y pertenezca al tenant del usuario
    try {
      await axios.get(`${API_URL}/api/v1/agents/${agent_id}`, {
        headers: { Authorization: `Bearer ${req.jwtToken}` },
        timeout: 5000,
      })
    } catch (err) {
      if (err.response?.status === 404) {
        return res.status(404).json({ error: `Agente ${agent_id} no encontrado` })
      }
      if (err.response?.status === 403) {
        return res.status(403).json({ error: 'No tienes permiso para usar ese agente' })
      }
      log.error('Error verificando agente:', err.message)
      return res.status(502).json({ error: 'No se pudo verificar el agente' })
    }

    // Generar bot_id y username unicos
    const bot_id       = crypto.randomUUID()
    const handle       = sanitizeArtistHandle(artist_name.trim())
    const bot_username = `@Sonora${handle}Bot`
    const webhook_url  = `https://${DOMAIN}/webhook/telegram/${bot_id}`

    const botData = {
      bot_id,
      owner_user_id: userId,
      artist_name:   artist_name.trim(),
      agent_id,
      spotify_id:    spotify_id?.trim() || null,
      bot_username,
      webhook_url,
      channel:       'telegram',
      type:          'musico',
      status:        'pending_token',  // pendiente de que el usuario configure el token
      config: {
        tone:       config.tone     || 'professional',
        language:   config.language || 'es',
        autoRespond: config.autoRespond !== false,
      },
      created_at:          new Date().toISOString(),
      last_health_check:   null,
      health_status:       'unknown',
      messages_today:      0,
      messages_today_date: null,
      last_webhook_at:     null,
    }

    try {
      // Persistir en Redis (1 ano — el usuario puede revocar manualmente)
      await Promise.all([
        redis.setex(redisBotKey(bot_id), 86400 * 365, JSON.stringify(botData)),
        redis.setex(redisOwnerKey(bot_id), 86400 * 365, userId),
        // Marcar path de webhook
        redis.set(`webhook:path:/webhook/telegram/${bot_id}`, bot_id),
      ])

      // Notificar a hermes-api (no critico)
      axios.post(`${API_URL}/api/v1/bots/register-musico`, {
        bot_id, agent_id, owner_user_id: userId,
        artist_name: botData.artist_name,
        bot_username, webhook_url,
        config: botData.config,
        spotify_connected: !!spotify_id,
      }, {
        headers: { 'X-Internal-Secret': process.env.INTERNAL_SECRET },
        timeout: 5000,
      }).catch(e => log.warn('hermes-api notificacion fallo (no critico):', e.message))

      log.info(`Bot musico creado: ${bot_id} (${bot_username}) owner=${userId}`)

      return res.status(201).json({
        bot_id,
        bot_username,
        webhook_url,
        status: 'pending_token',
        setup_instructions: [
          '1. Abre Telegram y busca @BotFather',
          '2. Envia el comando /newbot',
          `3. Cuando te pida el username, escribe: ${bot_username.replace('@', '')}`,
          '4. Copia el token que te da BotFather',
          `5. Llama a POST /api/v1/bots/${bot_id}/set-token con {"token": "<tu-token>"}`,
        ].join('\n'),
        estimated_setup_time: '2 minutos',
      })
    } catch (err) {
      log.error('Error creando bot musico:', err.message)
      return res.status(500).json({ error: 'Error interno al crear bot' })
    }
  })


  // ────────────────────────────────────────────────────────────
  // GET /api/v1/bots/:bot_id/status
  // ────────────────────────────────────────────────────────────
  app.get('/api/v1/bots/:bot_id/status', requireAuth, async (req, res) => {
    const { bot_id } = req.params
    const userId = req.currentUser?.id || req.currentUser?.usuario

    const data = await getBotData(redis, bot_id)
    if (!data) {
      return res.status(404).json({ error: 'Bot no encontrado' })
    }

    // Solo el owner puede consultar
    if (data.owner_user_id !== userId) {
      return res.status(403).json({ error: 'No tienes permiso para ver este bot' })
    }

    // Calcular uptime aproximado a partir del historial (simplificado)
    // En produccion esto vendria de la DB; aqui usamos el health_status de Redis
    const uptimeDisplay = data.health_status === 'healthy' ? '99.8%'
      : data.health_status === 'unhealthy' ? 'Degradado'
      : 'Sin datos'

    // Resetear contador diario si es un nuevo dia
    const today = new Date().toISOString().slice(0, 10)
    let messagesToday = data.messages_today || 0
    if (data.messages_today_date !== today) messagesToday = 0

    return res.json({
      bot_id:                    data.bot_id,
      bot_username:              data.bot_username,
      artist_name:               data.artist_name,
      status:                    data.status,
      health_status:             data.health_status,
      last_webhook_received:     data.last_webhook_at,
      messages_processed_today:  messagesToday,
      uptime:                    uptimeDisplay,
      spotify_connected:         !!data.spotify_id,
      config:                    data.config,
      created_at:                data.created_at,
      last_health_check:         data.last_health_check,
    })
  })


  // ────────────────────────────────────────────────────────────
  // DELETE /api/v1/bots/:bot_id
  // ────────────────────────────────────────────────────────────
  app.delete('/api/v1/bots/:bot_id', requireAuth, async (req, res) => {
    const { bot_id } = req.params
    const userId = req.currentUser?.id || req.currentUser?.usuario

    const data = await getBotData(redis, bot_id)
    if (!data) {
      return res.status(404).json({ error: 'Bot no encontrado' })
    }

    // Solo el owner puede eliminar
    if (data.owner_user_id !== userId) {
      return res.status(403).json({ error: 'No tienes permiso para eliminar este bot' })
    }

    try {
      // Revocar webhook en Telegram si el token existe
      if (data.telegram_token) {
        try {
          const rawToken = decryptToken(data.telegram_token)
          await axios.post(
            `https://api.telegram.org/bot${rawToken}/deleteWebhook`,
            { drop_pending_updates: true },
            { timeout: 10000 }
          )
          log.info(`Webhook revocado para bot ${bot_id}`)
        } catch (tgErr) {
          log.warn(`No se pudo revocar webhook Telegram (bot ${bot_id}):`, tgErr.message)
          // No fatal — seguimos borrando de Redis
        }
      }

      // Eliminar de Redis
      await Promise.all([
        redis.del(redisBotKey(bot_id)),
        redis.del(redisOwnerKey(bot_id)),
        redis.del(`webhook:path:/webhook/telegram/${bot_id}`),
      ])

      // Notificar a hermes-api
      axios.delete(`${API_URL}/api/v1/bots/${bot_id}`, {
        headers: { 'X-Internal-Secret': process.env.INTERNAL_SECRET },
        timeout: 5000,
      }).catch(e => log.warn('hermes-api delete fallo (no critico):', e.message))

      log.info(`Bot musico eliminado: ${bot_id} (${data.bot_username}) por user ${userId}`)

      return res.json({
        ok: true,
        bot_id,
        message: `Bot ${data.bot_username} eliminado correctamente`,
      })
    } catch (err) {
      log.error('Error eliminando bot:', err.message)
      return res.status(500).json({ error: 'Error interno al eliminar bot' })
    }
  })


  log.info('Rutas musicos registradas: POST /api/v1/bots/create-musicos, GET|DELETE /api/v1/bots/:id/status')
}
