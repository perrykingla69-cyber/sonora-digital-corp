const BASE = process.env.NEXT_PUBLIC_API_URL || 'https://sonoradigitalcorp.com/api'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('mystic_token')
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mystic_token')
      window.location.href = '/panel/login'
    }
    throw new Error('No autorizado')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Error ${res.status}`)
  }

  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body: unknown) => request<T>('POST', path, body),
  patch: <T>(path: string, body?: unknown) => request<T>('PATCH', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
}

// ── Types ─────────────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: {
    id: string
    email: string
    nombre: string
    tenant_id: string
    rol: string
    activo: boolean
  }
}

export interface DashboardData {
  mes_actual: string
  ingresos_mes: number
  egresos_mes: number
  utilidad_neta: number
  facturas_pendientes: number
  total_empleados: number
  tipo_cambio: number
}

export interface Factura {
  id: string
  folio: string
  fecha: string
  emisor_nombre: string
  receptor_nombre: string
  total: number
  moneda: string
  estado: 'pendiente' | 'pagada' | 'cancelada'
  tipo: 'ingreso' | 'egreso'
}

export interface Empleado {
  id: string
  nombre: string
  salario_diario: number
  departamento: string
  activo: boolean
}

export interface Nomina {
  empleado_id: string
  empleado_nombre: string
  periodo_inicio: string
  periodo_fin: string
  dias_trabajados: number
  salario_bruto: number
  isr: number
  imss: number
  salario_neto: number
}

export interface CierreData {
  ingresos: number
  egresos: number
  utilidad_bruta: number
  utilidad_neta: number
  isr_estimado: number
  iva_a_pagar: number
  total_facturas: number
  total_nomina: number
}

export interface MVE {
  id: string
  numero_pedimento: string
  fecha: string
  descripcion_mercancia: string
  valor_factura: number
  incoterm: string
  moneda: string
  valor_aduana: number
  estado: 'pendiente' | 'presentada' | 'pagada'
}

export interface GSDTask {
  id: string
  titulo: string
  descripcion: string
  prioridad: 'alta' | 'media' | 'baja'
  completada: boolean
  fecha_limite?: string
  created_at: string
}

export interface StatusData {
  api: string
  db: string
  redis: string
  status: string
  timestamp: string
}
