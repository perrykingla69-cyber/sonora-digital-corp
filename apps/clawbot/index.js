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
import { readdirSync, readFileSync } from 'fs'
import { join } from 'path'
import 'dotenv/config'

const redis = new Redis(process.env.REDIS_URL)
const API = process.env.API_URL
const OLLAMA = process.env.OLLAMA_URL || 'http://ollama:11434'
const app = express()
app.use(express.json())

// ── ORCHESTRATOR — Skills + Phi3 Router ───────────────────────

/** Carga todos los skills JSON al startup */
function loadSkills() {
  const skillsPath = process.env.SKILLS_PATH || '/app/skills'
  const skills = []
  try {
    for (const file of readdirSync(skillsPath).filter(f => f.endsWith('.json'))) {
      const skill = JSON.parse(readFileSync(join(skillsPath, file), 'utf8'))
      skills.push(skill)
    }
    // Ordenar por priority DESC (mayor prioridad = match primero), wildcard al final
    skills.sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0))
    console.log(`✅ ${skills.length} skills cargados`)
  } catch (e) {
    console.warn('⚠️ Skills no cargados:', e.message)
  }
  return skills
}

const SKILLS = loadSkills()

/** Busca skill por triggers — O(n) pero n=81 es trivial */
function matchSkill(text) {
  const lower = text.toLowerCase().trim()
  for (const skill of SKILLS) {
    if (!skill.triggers || skill.priority === -1) continue // skip brain-ask wildcard
    for (const trigger of skill.triggers) {
      if (lower.includes(trigger.toLowerCase())) return skill
    }
  }
  return null
}

/** Llama phi3 local para clasificar intent — rápido, sin costo */
async function classifyIntent(text) {
  try {
    const res = await axios.post(`${OLLAMA}/api/generate`, {
      model: 'phi3:latest',
      prompt: `Clasifica esta pregunta en UNA categoría: fiscal|nomina|aduanas|contabilidad|producto|simple|otro\nPregunta: "${text}"\nRespuesta (solo la categoría):`,
      stream: false,
      options: { temperature: 0, num_predict: 10 }
    }, { timeout: 5000 })
    return res.data.response?.trim().toLowerCase().split(/\s/)[0] || 'otro'
  } catch {
    return 'otro' // fallback silencioso si Ollama no responde
  }
}

/** Ejecuta un skill: STATIC → respuesta directa, GET/POST → llama endpoint */
async function executeSkill(skill, message, token, tenantId) {
  if (skill.method === 'STATIC') {
    return skill.response_text
  }
  const method = skill.method?.toLowerCase() || 'get'
  const url = skill.endpoint?.replace('http://api:8000', API)
  const payload = method === 'post'
    ? JSON.parse(JSON.stringify(skill.payload || {}).replace('{{message}}', message).replace('{{tenant_id}}', tenantId || ''))
    : undefined
  const res = await axios({ method, url, data: payload, headers: { Authorization: `Bearer ${token}` }, timeout: 15000 })
  const field = skill.response_field
  const data = field ? res.data[field] : res.data
  if (skill.response_template && typeof data === 'object') {
    return skill.response_template.replace(/\{\{(\w+)\}\}/g, (_, k) => data[k] ?? '')
  }
  return typeof data === 'string' ? data : JSON.stringify(data)
}

/** Orquestador principal: skill match → phi3 classify → API hermes */
async function orchestrate(text, token, convKey, tenantId) {
  // 1. Buscar skill por trigger (sin LLM)
  const skill = matchSkill(text)
  if (skill && skill.method === 'STATIC') {
    return { response: skill.response_text, source: 'skill:static' }
  }

  // 2. Clasificar intent con phi3 local en paralelo con Redis convId
  const [intent, convId] = await Promise.all([
    classifyIntent(text),
    redis.get(convKey)
  ])

  // 3. Si hay skill con endpoint para este intent → ejecutar skill
  if (skill) {
    try {
      const response = await executeSkill(skill, text, token, tenantId)
      return { response, source: `skill:${skill.name}` }
    } catch { /* fallback a hermes */ }
  }

  // 4. Fallback: llamar hermes_api (RAG completo)
  const res = await axios.post(`${API}/api/v1/agents/hermes/chat`, {
    message: text,
    channel: 'telegram',
    intent,
    ...(convId && { conversation_id: convId }),
  }, {
    headers: { Authorization: `Bearer ${token}` },
    timeout: 30000,
  })
  return { response: res.data.response, conversation_id: res.data.conversation_id, source: 'hermes' }
}

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
    const [api, exec] = await Promise.all([
      axios.get(`${API}/health`).catch(() => null),
      axios.get('http://host.docker.internal:9001/health').catch(() => null),
    ])
    const msg =
      `⚡ *HERMES OS — Estado*\n\n` +
      `• API:      ${api?.status === 200 ? '🟢 OK' : '🔴 Caído'}\n` +
      `• Executor: ${exec?.data?.ok ? `🟢 OK (opencode: ${exec.data.opencode ? '✓' : '✗'})` : '🔴 Caído'}\n` +
      `• Hora:     ${new Date().toLocaleString('es-MX')}`
    await ctx.reply(msg, { parse_mode: 'Markdown' })
  } catch {
    await ctx.reply('🔴 Error al obtener estado')
  }
})

// /code [tarea] → delega a Claude Code via executor en host
ceoBot.command('code', async (ctx) => {
  const task = ctx.message.text.replace(/^\/code\s*/i, '').trim()
  if (!task) {
    await ctx.reply(
      `⚡ *Claude Code — Uso:*\n\n` +
      `/code [descripción de la tarea]\n\n` +
      `Ejemplos:\n` +
      `• \`/code fix Bad Gateway en hermes_agent\`\n` +
      `• \`/code analiza logs de hermes_api y dime qué falla\`\n` +
      `• \`/code agrega endpoint /api/v1/stats\``,
      { parse_mode: 'Markdown' }
    )
    return
  }
  await ctx.reply(`⚡ *Delegando a Claude Code:*\n\n\`${task.slice(0, 120)}\`\n\n_Te aviso cuando termine_ 🤖`, { parse_mode: 'Markdown' })
  try {
    await axios.post('http://host.docker.internal:9001/run', { task }, { timeout: 5000 })
  } catch {
    await ctx.reply('⚠️ Executor offline. Instálalo:\n`systemctl start hermes-executor`', { parse_mode: 'Markdown' })
  }
})

// /deploy → trigger manual de GitHub Actions (push vacío)
ceoBot.command('deploy', async (ctx) => {
  await ctx.reply('🚀 *Deploy manual*\n\nUsa GitHub Actions directamente:\ngithub.com/perrykingla69-cyber/sonora-digital-corp/actions', { parse_mode: 'Markdown' })
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
    const convKey = `conv:ceo:${mode}`

    if (mode === 'mystic') {
      // MYSTIC: llamada directa (análisis profundo, sin skill routing)
      const convId = await redis.get(convKey)
      const res = await axios.post(`${API}/api/v1/agents/mystic/analyze`, {
        message: text, channel: 'telegram',
        ...(convId && { conversation_id: convId }),
      }, { headers: { Authorization: `Bearer ${ceoToken}` }, timeout: 30000 })
      if (res.data.conversation_id) await redis.setex(convKey, 3600 * 24, res.data.conversation_id)
      await ctx.reply('🌑 *MYSTIC:*\n\n' + res.data.response, { parse_mode: 'Markdown' })
    } else {
      // HERMES: pasar por orchestrator (skill match → phi3 → api)
      const result = await orchestrate(text, ceoToken, convKey, null)
      if (result.conversation_id) await redis.setex(convKey, 3600 * 24, result.conversation_id)
      await ctx.reply('☀️ *HERMES:*\n\n' + result.response, { parse_mode: 'Markdown' })
    }
  } catch (err) {
    console.error('CEO bot error:', err.message)
    await ctx.reply('⚠️ Error procesando tu mensaje. Reintentando...')
  }
})


// ── BOT PÚBLICO (clientes) ────────────────────────────────────
const publicBot = new Telegraf(process.env.TELEGRAM_TOKEN_PUBLIC)

// Tipos de negocio disponibles
const BUSINESS_TYPES = [
  { label: '🍽️ Restaurante / Pastelería', value: 'restaurante' },
  { label: '📊 Contador / Fiscal', value: 'contador' },
  { label: '🎵 Músico / Artista', value: 'musico' },
  { label: '🏗️ Constructor / Obra', value: 'constructor' },
  { label: '⚕️ Médico / Salud', value: 'medico' },
  { label: '⚖️ Abogado / Legal', value: 'abogado' },
  { label: '🏪 Otro negocio', value: 'general' },
]

// /start — iniciar onboarding o bienvenida de regreso
publicBot.command('start', async (ctx) => {
  const chatId = String(ctx.chat.id)

  // ¿Ya está registrado?
  const tokenKey = `token:telegram:${chatId}`
  const token = await redis.get(tokenKey)
  const slugKey = `slug:telegram:${chatId}`
  const slug = await redis.get(slugKey)

  if (token && slug) {
    const url = `https://sonoradigitalcorp.com/user/${slug}`
    await ctx.reply(
      `☀️ *¡Bienvenido de regreso!*\n\n` +
      `Tu panel está en:\n${url}\n\n` +
      `Escríbeme cualquier pregunta sobre tu negocio.`,
      { parse_mode: 'Markdown' }
    )
    return
  }

  // Iniciar onboarding — pedir nombre
  await redis.setex(`onboard:${chatId}:step`, 600, 'name')
  await ctx.reply(
    `¡Hola! 👋 Soy *HERMES*, tu asistente de negocios.\n\n` +
    `En 2 pasos creo tu espacio personalizado en *Sonora Digital Corp*.\n\n` +
    `*Paso 1:* ¿Cuál es tu nombre completo?`,
    { parse_mode: 'Markdown' }
  )
})

// /mi_panel — link al dashboard
publicBot.command('mi_panel', async (ctx) => {
  const chatId = String(ctx.chat.id)
  const slug = await redis.get(`slug:telegram:${chatId}`)
  if (slug) {
    await ctx.reply(`🔗 Tu panel: https://sonoradigitalcorp.com/user/${slug}`)
  } else {
    await ctx.reply('No tienes cuenta aún. Escribe /start para crearla.')
  }
})

// Manejar texto en el flujo de onboarding o chat normal
publicBot.on('text', async (ctx) => {
  const chatId = String(ctx.chat.id)
  const msgText = ctx.message.text
  const msgId = ctx.message.message_id

  // Dedup
  const cacheKey = `msg:pub:${chatId}:${msgId}`
  if (await redis.get(cacheKey)) return
  await redis.setex(cacheKey, 60, '1')

  // ── ONBOARDING step: name ──────────────────────────────────
  const step = await redis.get(`onboard:${chatId}:step`)

  if (step === 'name') {
    const name = msgText.trim()
    if (name.length < 2 || name.length > 80) {
      await ctx.reply('Por favor escribe tu nombre completo (mínimo 2 caracteres).')
      return
    }
    await redis.setex(`onboard:${chatId}:name`, 600, name)
    await redis.setex(`onboard:${chatId}:step`, 600, 'business')

    const keyboard = {
      reply_markup: {
        inline_keyboard: BUSINESS_TYPES.map(bt => ([
          { text: bt.label, callback_data: `biz:${bt.value}` }
        ]))
      }
    }
    await ctx.reply(
      `Perfecto, *${name}* 🙌\n\n*Paso 2:* ¿Qué tipo de negocio tienes?`,
      { parse_mode: 'Markdown', ...keyboard }
    )
    return
  }

  // ── CHAT normal (ya registrado) ────────────────────────────
  await ctx.sendChatAction('typing')

  try {
    const tokenKey = `token:telegram:${chatId}`
    const token = await redis.get(tokenKey)

    if (!token) {
      await ctx.reply(
        '⚠️ No encontré tu cuenta.\n\nEscribe /start para crear tu espacio gratis.'
      )
      return
    }

    const convKey = `conv:pub:${chatId}`
    const result = await orchestrate(msgText, token, convKey, chatId)
    if (result.conversation_id) await redis.setex(convKey, 3600 * 4, result.conversation_id)
    await ctx.reply(result.response)
  } catch (err) {
    console.error('Public bot error:', err.message)
    await ctx.reply('Disculpa, tuve un problema. Intenta en unos momentos.')
  }
})

// Callback: selección de tipo de negocio → completar registro
publicBot.on('callback_query', async (ctx) => {
  const chatId = String(ctx.chat?.id || ctx.callbackQuery.from.id)
  const data = ctx.callbackQuery.data

  if (!data.startsWith('biz:')) return
  await ctx.answerCbQuery()

  const businessType = data.replace('biz:', '')
  const name = await redis.get(`onboard:${chatId}:name`)

  if (!name) {
    await ctx.reply('Ocurrió un error. Por favor escribe /start de nuevo.')
    return
  }

  // Limpiar estado onboarding
  await redis.del(`onboard:${chatId}:step`, `onboard:${chatId}:name`)

  await ctx.sendChatAction('typing')
  await ctx.editMessageText('⚡ Creando tu espacio...')

  try {
    const res = await axios.post(`${API}/api/v1/users/onboard-telegram`, {
      chat_id: chatId,
      full_name: name,
      business_type: businessType,
    })

    const { slug, access_token, dashboard_url } = res.data

    // Guardar token y slug en Redis (24h)
    await redis.setex(`token:telegram:${chatId}`, 82800, access_token)
    await redis.setex(`slug:telegram:${chatId}`, 86400 * 30, slug)

    const btLabel = BUSINESS_TYPES.find(b => b.value === businessType)?.label || businessType

    await ctx.reply(
      `✅ *¡Tu espacio está listo!*\n\n` +
      `👤 *Nombre:* ${name}\n` +
      `💼 *Giro:* ${btLabel}\n` +
      `📊 *Plan:* Starter (7 días gratis)\n\n` +
      `🔗 *Tu página:*\n${dashboard_url}\n\n` +
      `Ahora puedes preguntarme lo que necesites sobre tu negocio. ¡Estoy aquí 24/7! ☀️`,
      { parse_mode: 'Markdown' }
    )
  } catch (err) {
    console.error('Onboarding error:', err.response?.data || err.message)
    if (err.response?.status === 400) {
      // Ya registrado
      const slugKey = `slug:telegram:${chatId}`
      const existingSlug = await redis.get(slugKey)
      if (existingSlug) {
        await ctx.reply(
          `Ya tienes una cuenta activa 🙌\n\n` +
          `Tu panel: https://sonoradigitalcorp.com/user/${existingSlug}`
        )
      } else {
        await ctx.reply('Ya tienes una cuenta registrada. Escribe /start para acceder.')
      }
    } else {
      await ctx.reply('Ocurrió un error al crear tu cuenta. Por favor intenta en unos minutos.')
    }
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
