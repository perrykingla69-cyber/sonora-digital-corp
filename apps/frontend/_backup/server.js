const http = require('http')
const fs = require('fs')
const path = require('path')

const landing = fs.readFileSync(path.join(__dirname, 'index.html'))
const dashboardTemplate = fs.readFileSync(path.join(__dirname, 'dashboard.html'), 'utf8')
const API_URL = process.env.API_URL || 'http://hermes-api:8000'

function fetchProfile(slug) {
  return new Promise((resolve, reject) => {
    const url = `${API_URL}/api/v1/users/profile/${slug}`
    const mod = url.startsWith('https') ? require('https') : http
    mod.get(url, { timeout: 5000 }, (res) => {
      let data = ''
      res.on('data', chunk => { data += chunk })
      res.on('end', () => {
        if (res.statusCode === 200) resolve(JSON.parse(data))
        else reject(new Error(String(res.statusCode)))
      })
    }).on('error', reject)
  })
}

const PLAN_LABELS = { starter: 'Starter', pro: 'Pro', enterprise: 'Enterprise' }
const PLAN_COLORS = { starter: '#7c3aed', pro: '#06b6d4', enterprise: '#f59e0b' }
const LEVEL_ICONS = { 1: '🌱', 2: '⚡', 3: '🔥', 4: '💎' }

http.createServer(async (req, res) => {
  const url = req.url.split('?')[0]

  if (url === '/' || url === '') {
    res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' })
    res.end(landing)
    return
  }

  const userMatch = url.match(/^\/user\/([a-z0-9-]{1,80})$/)
  if (userMatch) {
    const slug = userMatch[1]
    try {
      const p = await fetchProfile(slug)
      const planLabel = PLAN_LABELS[p.plan] || p.plan
      const planColor = PLAN_COLORS[p.plan] || '#7c3aed'
      const levelIcon = LEVEL_ICONS[p.level] || '🌱'
      const initials = (p.full_name || 'U').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
      const memberSince = p.created_at
        ? new Date(p.created_at).toLocaleDateString('es-MX', { year: 'numeric', month: 'long' })
        : ''

      const html = dashboardTemplate
        .replace(/\{\{FULL_NAME\}\}/g, p.full_name || slug)
        .replace(/\{\{SLUG\}\}/g, slug)
        .replace(/\{\{PLAN_LABEL\}\}/g, planLabel)
        .replace(/\{\{PLAN_COLOR\}\}/g, planColor)
        .replace(/\{\{LEVEL\}\}/g, p.level || 1)
        .replace(/\{\{LEVEL_NAME\}\}/g, p.level_name || 'Aprendiz')
        .replace(/\{\{LEVEL_ICON\}\}/g, levelIcon)
        .replace(/\{\{SCORE\}\}/g, p.score || 0)
        .replace(/\{\{TOKENS\}\}/g, p.tokens_balance || 0)
        .replace(/\{\{CONVERSATIONS\}\}/g, p.total_conversations || 0)
        .replace(/\{\{ASSETS\}\}/g, p.total_assets || 0)
        .replace(/\{\{INITIALS\}\}/g, initials)
        .replace(/\{\{AVATAR_URL\}\}/g, p.avatar_url || '')
        .replace(/\{\{MEMBER_SINCE\}\}/g, memberSince)

      res.writeHead(200, { 'Content-Type': 'text/html;charset=utf-8' })
      res.end(html)
    } catch (err) {
      const is404 = String(err.message) === '404'
      res.writeHead(is404 ? 404 : 500, { 'Content-Type': 'text/html;charset=utf-8' })
      res.end(`<html><body style="background:#05050f;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0"><div style="text-align:center"><h2 style="color:#7c3aed">${is404 ? '404' : '500'}</h2><p>${is404 ? 'Perfil no encontrado' : 'Error cargando el perfil'}</p><a href="/" style="color:#06b6d4">← Volver al inicio</a></div></body></html>`)
    }
    return
  }

  res.writeHead(301, { Location: '/' })
  res.end()
}).listen(3000, '0.0.0.0', () => console.log('Frontend on :3000'))
