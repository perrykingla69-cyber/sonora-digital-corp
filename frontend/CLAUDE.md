# agent:frontend — Next.js Dashboard
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "frontend nextjs hermes"` en Engram.

## Dominio
Web app: dashboard cliente, landing pages, PWA móvil (iPhone first).
Next.js 14 App Router, TypeScript. Puerto: `3000`.

## Estructura esperada
- `app/` — App Router pages
- `components/` — UI components
- `lib/` — API client, auth helpers
- `public/` — assets estáticos

## Reglas críticas
- **Rebuild completo** siempre al cambiar código (imagen baked en Docker)
- `NEXT_PUBLIC_*` vars → deben ir en `build.args` en docker-compose, NO en environment
- localStorage keys: `hermes_token`, `hermes_user`, `hermes_consent_v1`
- `const`/`let` siempre, nunca `var`
- Interfaces sobre types
- API base URL: `NEXT_PUBLIC_API_URL` → `http://hermes-api:8000`

## Build
```bash
docker compose build frontend
docker compose up -d frontend
```

## Estado actual
Placeholder activo. Pendiente: dashboard real + landing pages por nicho.
99 slots disponibles en Hostinger Premium para landing pages adicionales.
