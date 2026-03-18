# CLAUDE.md — MYSTIC AI OS
## Sonora Digital Corp

> Este archivo carga automáticamente en cada sesión. No modificar sin razón.

---

## IDENTIDAD DEL PROYECTO

**MYSTIC** es un AI Orchestrator SaaS para PYMEs mexicanas.
Automatiza contabilidad, nómina, facturas, CRM y Brain IA por WhatsApp/Telegram.

- **Dueño:** Marco (CEO) — sonoradigitalcorp@gmail.com
- **VPS:** 187.124.85.191 (Hostinger, Ubuntu)
- **Repo:** github.com/perrykingla69-cyber/sonora-digital-corp
- **Rama principal:** `main` — CI/CD activo (push → deploy automático al VPS)
- **Idioma siempre:** español

---

## STACK TÉCNICO

| Capa | Tecnología |
|---|---|
| Backend API | FastAPI (Python 3.11), SQLAlchemy, Alembic |
| Base de datos | PostgreSQL 15 (mystic_postgres :5432) |
| Caché | Redis (mystic_redis :6379) |
| Frontend | Next.js 14 (App Router, TypeScript) |
| Brain IA | DeepSeek-R1:1.5b vía Ollama |
| Vector DB | Qdrant (:6333) |
| WhatsApp | Baileys 6.7.21 (mystic_wa :3001) |
| Automatización | N8N (:5679) |
| Bot | Telegram (mystic_bot) |
| Infra | Docker Compose v2, Nginx reverse proxy |

---

## ESTRUCTURA DEL PROYECTO

```
sonora-digital-corp/
├── backend/
│   ├── main.py          ← TODO el API en un solo archivo (FastAPI)
│   ├── models.py        ← Modelos SQLAlchemy
│   ├── schemas.py       ← Pydantic schemas
│   ├── database.py      ← Conexión PostgreSQL
│   ├── security.py      ← JWT auth
│   └── app/ai/          ← AI OS (agentes, skills, swarm, memoria)
├── frontend/            ← Next.js 14 App Router
├── whatsapp/            ← mystic-wa (Baileys)
├── bot/                 ← Telegram bot
├── infra/
│   ├── docker-compose.vps.yml   ← USAR EN VPS (producción)
│   └── docker-compose.yml       ← desarrollo local
├── n8n_workflows/
└── scripts/
```

---

## REGLAS CRÍTICAS DE OPERACIÓN

### Docker
- Usar `docker compose` (v2), NUNCA `docker-compose` (v1)
- Rebuild API (cambios rápidos sin rebuild): `docker cp main.py mystic_api:/app/main.py && docker restart mystic_api`
- Frontend SIEMPRE necesita rebuild completo (código baked en imagen):
  ```bash
  cd /home/mystic/sonora-digital-corp/infra
  NEXT_PUBLIC_API_URL=https://sonoradigitalcorp.com/api docker compose -f docker-compose.vps.yml build frontend --no-cache
  ```
- Passwords con `!` en bash → usar Python subprocess o comillas simples

### Git en VPS
```bash
git -C /home/mystic/sonora-digital-corp <comando>
```

### Auth / JWT
- Login devuelve `usuario` (no `user`) — campo crítico, no cambiar
- Frontend y tipos TS deben usar `usuario` consistentemente

### Brain IA (RAG 4 capas — todo $0)
1. Determinístico (lógica directa)
2. Redis caché (TTL 1h)
3. Qdrant (búsqueda vectorial)
4. Ollama DeepSeek-R1:1.5b (num_ctx=2048)
5. Claude API (solo 5% de casos como fallback)

### WhatsApp
- Whitelist activa: `6622681111` (Nathaly/Fourgea), `6623538272` (Marco)
- Ignorar grupos `@g.us` y notificaciones `@lid`
- Fallback activo si DeepSeek retorna respuesta vacía

---

## CLIENTES ACTIVOS

### Fourgea Mexico SA de CV
- RFC: E080820LC2 | Filtración fluidos industriales
- Contacto: **Nathaly** — cp.nathalyhermosillo@gmail.com / Nathaly2026!
- WhatsApp: 6622681111
- tenant_id: fourgea

### Triple R Oil México
- RFC: O150504GE3
- admin@tripler.mx / TripleR2026!
- tenant_id: tripler

---

## ENDPOINTS PRINCIPALES

```
POST /auth/login              → { usuario, access_token }
GET  /auth/me                 → perfil del usuario
GET  /dashboard               → métricas del tenant
POST /facturas/xml            → parsear CFDI XML
GET  /cierre/{ano}/{mes}      → cierre contable mensual
POST /api/brain/ask           → RAG + Ollama
POST /api/brain/swarm         → Queen-Worker paralelo
POST /api/brain/feedback      → auto-aprendizaje (+1/-1)
POST /api/wa/webhook          → WhatsApp entrante
GET  /status                  → health del sistema
```

---

## URLS EN PRODUCCIÓN

- API: https://sonoradigitalcorp.com/api/status
- Dashboard: https://sonoradigitalcorp.com/panel/login
- Docs: https://sonoradigitalcorp.com/docs
- WhatsApp QR: https://sonoradigitalcorp.com/whatsapp/qr?apikey=MysticWA2026%21

---

## CREDENCIALES (solo VPS/local, nunca en código)

- PostgreSQL: `mystic_user` / `MysticSecure2026!`
- Redis: `MysticRedis2026!`
- WA API Key: `MysticWA2026!`
- N8N API Key: `mystic_n8n_0a581672f5e34a88a74ab054b9f1242e`
- SMTP: sonoradigitalcorp@gmail.com (App Password en docker-compose.vps.yml)

---

## PENDIENTES ACTIVOS

1. Chip prepago Telcel para número Mystic dedicado (~$50 MXN)
2. Cargar XMLs/CFDIs reales de Fourgea → cierre de mes real
3. Seed Qdrant con más docs de Fourgea
4. Widget WhatsApp en dashboard (ver conversaciones desde panel)

---

## MEMORIA RAM — REGLAS (VPS tiene 3.2GB)

- Ollama se puede pausar cuando no se usa: `docker pause mystic-ollama`
- Reanudar: `docker unpause mystic-ollama`
- Cerrar Chrome innecesario libera ~600MB
- No correr contenedores en restart-loop (revisar y detener si no son necesarios)
