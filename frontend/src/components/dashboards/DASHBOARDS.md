# HERMES Dashboards — Guía de Uso

## Componentes Reutilizables

Todos los componentes están en `/frontend/src/components/dashboards/` y se exportan desde `index.ts`.

### Button.tsx
- Botón con variantes: `primary`, `secondary`, `danger`, `ghost`
- Tamaños: `sm`, `md`, `lg`
- Prop `loading` para estado de carga

```tsx
import { Button } from '@/components/dashboards'

<Button onClick={handleClick} variant="primary" size="md" loading={isLoading}>
  Acción
</Button>
```

### Alert.tsx
- Tipos: `success`, `error`, `warning`, `info`
- Icono automático, cierre opcional

```tsx
<Alert type="error" title="Error" message="Algo salió mal" onClose={() => setError(null)} />
```

### Table.tsx
- Columnas configurables con alineación
- Cargando y estado vacío
- Responsive con scroll horizontal

```tsx
<Table
  columns={[
    { key: 'name', label: 'Nombre', align: 'left' },
    { key: 'status', label: 'Estado', align: 'center' }
  ]}
  rows={[{ name: 'John', status: 'Activo' }]}
  loading={false}
  empty="Sin datos"
/>
```

### Card.tsx (DashboardCard)
- Contenedor con estilos Sovereign
- Título y badge opcionales
- Clickeable

```tsx
<DashboardCard title="Titulo" badge={{ label: 'Gold', color: 'gold' }}>
  Contenido aquí
</DashboardCard>
```

### Stat.tsx
- Métrica con etiqueta, valor, sub-texto
- Colores: `green`, `red`, `blue`, `gray`, `gold`
- Ícono e indicador de tendencia opcionales

```tsx
<Stat
  label="Mensajes Hoy"
  value={142}
  sub="+12% vs ayer"
  color="blue"
  icon="💬"
  trend={{ direction: 'up', value: 12 }}
/>
```

## Dashboards Completos

### CEO Dashboard (`/frontend/src/components/dashboards/CEODashboard.tsx`)

**URL:** `/dashboard/ceo`

**Características:**
- Overview: 6 tenants activos, mensajes hoy, alertas críticas
- Tabla de tenants con niche, usuarios activos, último mensaje
- Health check de 6 servicios (hermes-api, PostgreSQL, Redis, Qdrant, Evolution, Ollama)
- Feed de 10 alertas MYSTIC (crítico/advertencia/info)
- Chat directo con HERMES (input + history)
- Datos simulados (en producción: API calls a `/api/v1/admin/dashboard`)

**Estados y datos:**
- Servicios con status (healthy/degraded/down), uptime%, latencia
- Tenants con estado (activo/inactivo)
- Alerts filtradas por tipo

### Client Dashboard (`/frontend/src/components/dashboards/ClientDashboard.tsx`)

**URL:** `/dashboard/[tenantId]`

**Características:**
- Info del tenant: nombre, nicho, fecha unión, plan
- Estadísticas de uso: mensajes hoy, docs seeded, búsquedas RAG, vectores
- Chat HERMES con RAG (input + history, contador de tokens)
- 3 tabs:
  - Overview: stats + chat
  - Documentos: tabla de docs seeded, opción borrar
  - Configuración: API keys, zona roja (peligro)
- Acciones rápidas: subir doc, gestionar keys, settings
- Plan info: límites y upgrade

**Datos simulados:**
- 4 documentos de ejemplo (PDF, texto, imágenes)
- 2 API keys (una activa, una inactiva)
- Stats de uso

## Integración de API

### En desarrollo (datos simulados)
Los dashboards funcionan con datos mock, no requieren backend.

### En producción
Reemplazar llamadas simuladas con `api.get()` y `api.post()`:

```tsx
// CEO Dashboard
const data = await api.get('/api/v1/admin/dashboard')
const services = await api.get('/api/v1/admin/health')
const alerts = await api.get('/api/v1/agents/mystic/alerts?limit=10')

// Chat
const response = await api.post('/api/v1/agents/hermes/chat', {
  tenant_id: tenantId,
  mensaje: chatMessage,
  history: chatHistory
})

// Client Dashboard
const tenant = await api.get(`/api/v1/tenants/${tenantId}`)
const docs = await api.get(`/api/v1/tenants/${tenantId}/documents`)
const keys = await api.get(`/api/v1/tenants/${tenantId}/api-keys`)
```

## Seguridad — Auth

### Layout (`/frontend/src/app/dashboard/layout.tsx`)
- Verifica JWT en `localStorage.hermes_token`
- Si no existe, redirige a `/login`
- Decodifica usuario desde `localStorage.hermes_user`
- Logout limpia ambas claves

### Endpoint requerido en backend
```
GET /auth/me
Headers: Authorization: Bearer {token}
Response: { id, email, nombre, tenant_id, rol, activo }
```

## Rutas

```
/dashboard/ceo                  → CEO Dashboard
/dashboard/[tenantId]           → Client Dashboard (dinámico)
/dashboard/layout.tsx           → Shared layout (auth + nav + footer)
```

## Estilos

Usa las clases Sovereign del tailwind.config.js existente:
- `bg-sovereign-bg` — fondo principal
- `bg-sovereign-card` — fondo de cards
- `border-sovereign-border` — bordes
- `text-sovereign-text` — texto
- `text-sovereign-muted` — texto secundario
- `text-sovereign-gold` — acentos (D4AF37)

## Mobile-First

- Grid responsive: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- Padding adaptable: `p-4 sm:p-8`
- Texto escalable: `text-sm sm:text-base`
- Todos los componentes son mobile-friendly

## Testing

Para verificar que todo compila:
```bash
cd frontend
npm run build
```

Para desarrollo:
```bash
npm run dev
# http://localhost:3000/dashboard/ceo
# http://localhost:3000/dashboard/test-tenant-id
```

## Notas Importantes

1. **Sin backend real:** Los dashboards no hacen llamadas reales a `/api/v1/...` por defecto. Son completamente autónomos con datos mock.
2. **JWT siempre en localStorage:** El layout verifica `hermes_token` y redirige a login si falta.
3. **TypeScript strict:** Todos los componentes tienen tipos explícitos. Agrega `"strict": true` en tsconfig.json si es necesario.
4. **Clsx + Tailwind:** Usa `clsx()` para clases condicionales (ya instalado).
5. **Next.js 14 App Router:** Los dashboards usan nuevas features como `useParams()` y layouts anidados.

## Próximos Pasos

1. Conectar JWT decoding real en el layout
2. Implementar endpoints `/api/v1/admin/dashboard` en FastAPI
3. Reemplazar datos mock con llamadas a API
4. Agregar error handling de API
5. Implementar WebSocket para chat en tiempo real
6. Agregar paginación en tablas grandes
