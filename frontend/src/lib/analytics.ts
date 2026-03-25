/**
 * analytics.ts — Telemetría de uso MYSTIC
 * Recolecta datos de comportamiento con consentimiento (LFPDPPP)
 */

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type EventType =
  | 'page_view'
  | 'module_open'
  | 'brain_query'
  | 'feature_click'
  | 'error_ui'
  | 'session_start'
  | 'session_end'
  | 'time_on_module'

interface AnalyticsEvent {
  event: EventType
  module?: string
  detail?: string
  duration_sec?: number
  error_msg?: string
  metadata?: Record<string, unknown>
}

function hasConsent(): boolean {
  try {
    const c = localStorage.getItem('mystic_consent_v1')
    if (!c) return false
    return JSON.parse(c)?.analytics === true
  } catch { return false }
}

function getSessionMeta() {
  return {
    url: window.location.pathname,
    referrer: document.referrer || null,
    screen: `${window.screen.width}x${window.screen.height}`,
    viewport: `${window.innerWidth}x${window.innerHeight}`,
    device: /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
    browser: navigator.userAgent.slice(0, 80),
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    lang: navigator.language,
    ts: Date.now(),
  }
}

export async function track(event: AnalyticsEvent) {
  if (!hasConsent()) return
  try {
    const token = localStorage.getItem('mystic_token')
    await fetch(`${API}/api/analytics/event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        ...event,
        ...getSessionMeta(),
      }),
      keepalive: true,
    })
  } catch { /* silencioso — no afecta la app */ }
}

/** Hook para medir tiempo en un módulo */
export function trackModuleTime(module: string) {
  const start = Date.now()
  track({ event: 'module_open', module })
  return () => {
    const sec = Math.round((Date.now() - start) / 1000)
    if (sec > 3) track({ event: 'time_on_module', module, duration_sec: sec })
  }
}

/** Trackear error UI */
export function trackError(module: string, error_msg: string) {
  track({ event: 'error_ui', module, error_msg: error_msg.slice(0, 200) })
}

/** Trackear pregunta al Brain */
export function trackBrainQuery(query: string) {
  track({ event: 'brain_query', detail: query.slice(0, 150) })
}
