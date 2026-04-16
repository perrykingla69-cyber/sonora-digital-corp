/**
 * MusicosBotHandler
 * Maneja actualizaciones de Telegram para bots de artistas/musicos.
 * Soporta tanto modo webhook (produccion) como polling (desarrollo).
 *
 * Uso:
 *   const handler = new MusicosBotHandler(token, agentId, artistName, config, redis)
 *   // Webhook: handler.handleUpdate(req.body)
 *   // Polling: handler.startPolling()
 */

import axios from 'axios'
import { createLogger } from '../logger.js'

const log = createLogger('MusicosBotHandler')
const API_URL = process.env.API_URL || 'http://hermes-api:8000'

// Rate limit: max mensajes por minuto por chat
const RATE_LIMIT_MAX = 100
const RATE_LIMIT_WINDOW = 60 // segundos

// ── Sanitizacion de input ─────────────────────────────────────
/**
 * Elimina posibles injecciones de Markdown/HTML y limita longitud.
 * Telegram text no ejecuta codigo, pero prevenimos log injection.
 */
function sanitizeText(text) {
  if (typeof text !== 'string') return ''
  return text
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '') // control chars
    .slice(0, 4096) // limite de Telegram
}

// ── Helpers de Telegram Bot API (sin polling lib para bajo footprint) ──
class TelegramClient {
  constructor(token) {
    this.token = token
    this.base  = `https://api.telegram.org/bot${token}`
  }

  async sendMessage(chat_id, text, extra = {}) {
    // Truncar si excede limite de Telegram
    const safeText = String(text).slice(0, 4096)
    return axios.post(`${this.base}/sendMessage`, {
      chat_id,
      text: safeText,
      ...extra,
    }, { timeout: 10000 })
  }

  async sendChatAction(chat_id, action = 'typing') {
    return axios.post(`${this.base}/sendChatAction`, { chat_id, action }, { timeout: 5000 })
      .catch(() => {}) // no critico
  }

  async answerCallbackQuery(callback_query_id, text = '') {
    return axios.post(`${this.base}/answerCallbackQuery`, { callback_query_id, text }, { timeout: 5000 })
      .catch(() => {})
  }

  async getUpdates(offset = 0) {
    const r = await axios.get(`${this.base}/getUpdates`, {
      params: { offset, timeout: 30, limit: 100 },
      timeout: 35000,
    })
    return r.data.result || []
  }

  async deleteWebhook() {
    return axios.post(`${this.base}/deleteWebhook`, {}, { timeout: 5000 }).catch(() => {})
  }
}

// ── Handler principal ─────────────────────────────────────────
export class MusicosBotHandler {
  /**
   * @param {string} botToken    - Token de Telegram
   * @param {string} agentId     - UUID del agente en hermes-api
   * @param {string} artistName  - Nombre del artista (para contexto IA)
   * @param {object} config      - { tone, language, autoRespond, spotifyId }
   * @param {object} redis       - ioredis instance (para rate limit + conv IDs)
   * @param {string} botId       - UUID del bot (para logging + Redis keys)
   */
  constructor(botToken, agentId, artistName, config = {}, redis = null, botId = null) {
    this.tg         = new TelegramClient(botToken)
    this.agentId    = agentId
    this.artistName = artistName
    this.botId      = botId || agentId
    this.redis      = redis
    this.config = {
      tone:        config.tone        || 'professional',
      language:    config.language    || 'es',
      autoRespond: config.autoRespond !== false,
      spotifyId:   config.spotifyId   || config.spotify_id || null,
    }
    this._pollingOffset = 0
    this._polling       = false
  }

  // ── Rate limit ──────────────────────────────────────────────
  async _checkRateLimit(chatId) {
    if (!this.redis) return true // sin Redis no limitamos
    const key   = `rl:musico:${this.botId}:${chatId}`
    const count = await this.redis.incr(key)
    if (count === 1) await this.redis.expire(key, RATE_LIMIT_WINDOW)
    return count <= RATE_LIMIT_MAX
  }

  // ── Dedup ───────────────────────────────────────────────────
  async _isDuplicate(messageId) {
    if (!this.redis) return false
    const key    = `dedup:musico:${this.botId}:${messageId}`
    const exists = await this.redis.get(key)
    if (exists) return true
    await this.redis.setex(key, 60, '1')
    return false
  }

  // ── Actualizar metrica diaria en Redis ──────────────────────
  async _trackMessage() {
    if (!this.redis) return
    const today    = new Date().toISOString().slice(0, 10)
    const countKey = `msgs:musico:${this.botId}:${today}`
    await this.redis.incr(countKey)
    await this.redis.expire(countKey, 86400 * 2) // 2 dias
  }

  // ── Obtener conv_id del chat ─────────────────────────────────
  async _getConvId(chatId) {
    if (!this.redis) return null
    return this.redis.get(`conv:musico:${this.botId}:${chatId}`)
  }

  async _setConvId(chatId, convId) {
    if (!this.redis || !convId) return
    await this.redis.setex(`conv:musico:${this.botId}:${chatId}`, 3600 * 4, convId)
  }

  // ── Dispatcher de actualizaciones ───────────────────────────
  async handleUpdate(update) {
    try {
      if (update.message) {
        await this._handleMessage(update.message)
      } else if (update.callback_query) {
        await this._handleCallback(update.callback_query)
      }
      // channel_post, inline_query, etc. ignorados por ahora
    } catch (err) {
      log.error(`[bot=${this.botId}] Error en handleUpdate:`, err.message)
    }
  }

  // ── Dispatcher de mensajes ───────────────────────────────────
  async _handleMessage(msg) {
    if (!msg?.text) return

    const chatId    = msg.chat.id
    const text      = sanitizeText(msg.text)
    const messageId = msg.message_id

    // Dedup
    if (await this._isDuplicate(messageId)) return

    // Rate limit
    const allowed = await this._checkRateLimit(chatId)
    if (!allowed) {
      await this.tg.sendMessage(chatId, 'Has enviado demasiados mensajes. Espera un momento.')
      return
    }

    // Routing por comando o patron
    if (text.startsWith('/start'))  return this._handleStart(msg)
    if (text.startsWith('/help'))   return this._handleHelp(msg)
    if (text.startsWith('/stats'))  return this._handleStats(msg)
    if (/booking|contrata|presenta|show|concierto/i.test(text)) return this._handleBooking(msg)
    if (/vendo|compra|beat|precio|catalogo/i.test(text))        return this._handleSales(msg)

    // Mensaje generico
    if (this.config.autoRespond) {
      return this._handleGenericMessage(msg)
    }
  }

  // ── Dispatcher de callbacks (inline keyboard) ────────────────
  async _handleCallback(cbq) {
    await this.tg.answerCallbackQuery(cbq.id)
    const chatId = cbq.message?.chat?.id || cbq.from?.id
    if (!chatId) return

    switch (cbq.data) {
      case 'list_beats':
        await this.tg.sendMessage(chatId, 'Enviame tu lista de beats y la publico para ti.')
        break
      case 'upload_beat':
        await this.tg.sendMessage(chatId, 'Sube el archivo de audio o el link de tu beat.')
        break
      case 'set_prices':
        await this.tg.sendMessage(chatId, 'Escribeme los precios de tus beats (ej: "Beat trap $500 MXN").')
        break
      default:
        log.warn(`[bot=${this.botId}] Callback desconocido: ${cbq.data}`)
    }
  }

  // ── /start ───────────────────────────────────────────────────
  async _handleStart(msg) {
    const welcome =
      `Hola! Soy el asistente de ${this.artistName}.\n\n` +
      `Puedo ayudarte con:\n` +
      `/booking - Inquiries de conciertos y presentaciones\n` +
      `/stats   - Estadisticas de Spotify\n` +
      `/help    - Mas opciones\n\n` +
      `O escribeme directo tu pregunta.`
    await this.tg.sendMessage(msg.chat.id, welcome)
  }

  // ── /help ────────────────────────────────────────────────────
  async _handleHelp(msg) {
    const help =
      `Comandos disponibles:\n\n` +
      `/start   - Bienvenida\n` +
      `/booking - Contratar a ${this.artistName}\n` +
      `/stats   - Stats de Spotify\n` +
      `/help    - Este menu\n\n` +
      `Tambien puedo responder preguntas en lenguaje natural.`
    await this.tg.sendMessage(msg.chat.id, help)
  }

  // ── /stats — Spotify ─────────────────────────────────────────
  async _handleStats(msg) {
    await this.tg.sendChatAction(msg.chat.id)

    if (!this.config.spotifyId) {
      await this.tg.sendMessage(msg.chat.id, 'Las estadisticas de Spotify aun no estan configuradas.')
      return
    }

    try {
      const r = await axios.get(
        `${API_URL}/api/v1/integrations/spotify/artist-stats/${this.config.spotifyId}`,
        { timeout: 10000 }
      )
      const s = r.data
      const reply =
        `Estadisticas de Spotify - ${this.artistName}:\n\n` +
        `Oyentes mensuales: ${(s.monthly_listeners || 0).toLocaleString('es-MX')}\n` +
        `Reproducciones totales: ${(s.total_plays || 0).toLocaleString('es-MX')}\n` +
        `Seguidores nuevos: ${s.new_followers ?? 'N/D'}\n` +
        `Tendencia: ${(s.followers_trend || 0) > 0 ? 'Creciendo' : 'Bajando'}`
      await this.tg.sendMessage(msg.chat.id, reply)
    } catch (err) {
      log.error(`[bot=${this.botId}] Error stats Spotify:`, err.message)
      await this.tg.sendMessage(msg.chat.id, 'No pude obtener las estadisticas ahora. Intenta mas tarde.')
    }
  }

  // ── /booking ─────────────────────────────────────────────────
  async _handleBooking(msg) {
    await this.tg.sendChatAction(msg.chat.id)
    await this._trackMessage()

    try {
      const response = await this._callAgentAPI({
        intent:    'booking_inquiry',
        message:   sanitizeText(msg.text),
        chat_id:   String(msg.chat.id),
        artist:    this.artistName,
      }, msg.chat.id)

      await this.tg.sendMessage(msg.chat.id, response)
    } catch (err) {
      log.error(`[bot=${this.botId}] Error booking:`, err.message)
      await this.tg.sendMessage(msg.chat.id, 'Gracias por tu interes en contratar a ' + this.artistName + '. Te respondemos a la brevedad.')
    }
  }

  // ── ventas / beats ───────────────────────────────────────────
  async _handleSales(msg) {
    await this._trackMessage()

    const keyboard = {
      reply_markup: JSON.stringify({
        inline_keyboard: [
          [{ text: 'Ver beats disponibles', callback_data: 'list_beats' }],
          [{ text: 'Subir nuevo beat',       callback_data: 'upload_beat' }],
          [{ text: 'Configurar precios',      callback_data: 'set_prices' }],
        ],
      }),
    }
    await this.tg.sendMessage(msg.chat.id, 'Que quieres hacer?', keyboard)
  }

  // ── Mensaje generico → agente IA ─────────────────────────────
  async _handleGenericMessage(msg) {
    await this.tg.sendChatAction(msg.chat.id)
    await this._trackMessage()

    try {
      const response = await this._callAgentAPI({
        intent:    'generic',
        message:   sanitizeText(msg.text),
        chat_id:   String(msg.chat.id),
        artist:    this.artistName,
      }, msg.chat.id)

      await this.tg.sendMessage(msg.chat.id, response)
    } catch (err) {
      log.error(`[bot=${this.botId}] Error mensaje generico:`, err.message)
      await this.tg.sendMessage(msg.chat.id, 'Disculpa, tuve un problema. Intenta en unos momentos.')
    }
  }

  // ── Llamar al agente hermes-api ──────────────────────────────
  async _callAgentAPI(payload, chatId) {
    const convId = await this._getConvId(chatId)

    const body = {
      ...payload,
      context: {
        artist_name: this.artistName,
        tone:        this.config.tone,
        language:    this.config.language,
        spotify_id:  this.config.spotifyId,
      },
      ...(convId && { conversation_id: convId }),
    }

    const r = await axios.post(
      `${API_URL}/api/v1/agents/${this.agentId}/chat-public`,
      body,
      { timeout: 30000 }
    )

    if (r.data.conversation_id) {
      await this._setConvId(chatId, r.data.conversation_id)
    }

    return r.data.reply || r.data.response || 'Lo siento, no pude procesar tu mensaje.'
  }

  // ── Modo polling (desarrollo) ────────────────────────────────
  async startPolling() {
    if (this._polling) return
    this._polling = true
    await this.tg.deleteWebhook()
    log.info(`[bot=${this.botId}] Iniciando polling...`)

    while (this._polling) {
      try {
        const updates = await this.tg.getUpdates(this._pollingOffset)
        for (const update of updates) {
          this._pollingOffset = update.update_id + 1
          this.handleUpdate(update).catch(e => log.error('handleUpdate error:', e.message))
        }
      } catch (err) {
        if (this._polling) {
          log.warn(`[bot=${this.botId}] Polling error (reintentando):`, err.message)
          await new Promise(r => setTimeout(r, 3000))
        }
      }
    }
  }

  stopPolling() {
    this._polling = false
    log.info(`[bot=${this.botId}] Polling detenido.`)
  }
}
