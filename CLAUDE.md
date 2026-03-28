# CLAUDE.md — HERMES AI OS
## Sonora Digital Corp

> Este archivo carga automáticamente en cada sesión. Mantén el idioma en español y no pegues secretos reales en prompts, commits o archivos versionados.

## 🔑 PALABRA CLAVE DE ACTIVACIÓN: `.DENIURGO`

Cuando Luis Daniel escribe **.DENIURGO** (con punto adelante, en cualquier parte del mensaje), ejecutar automáticamente:

1. `mem_context` → recuperar sesión anterior (Engram)
2. `mem_search "pendientes"` → tareas críticas abiertas
3. `docker ps --format` → verificar containers activos
4. `curl localhost:8000/status` + `curl localhost:3003/health` → salud del sistema
5. `git status` → cambios pendientes de commit
6. Reportar en 10 líneas: ✅ OK / ⚠️ Atención / 🔴 Caído
7. Mostrar top 3 acciones: las que necesitan credenciales y las que no
8. Preguntar: *"¿por dónde arrancamos?"*

**Sin que Luis Daniel tenga que pedir nada.**

---

## IDENTIDAD DEL PROYECTO

**HERMES** es un AI Orchestrator SaaS para PYMEs mexicanas.
Automatiza contabilidad, nómina, facturas, CRM y Brain IA por WhatsApp/Telegram.

- **Dueño:** Luis Daniel Guerrero Enciso (CEO)
- **VPS:** Hostinger Ubuntu (IP y acceso fuera del repo)
- **Repo:** `github.com/perrykingla69-cyber/sonora-digital-corp`
- **Rama estable:** `main`
- **Idioma siempre:** español

---

## STACK TÉCNICO

| Capa | Tecnología |
|---|---|
| Backend API | FastAPI (Python 3.11), SQLAlchemy, Alembic |
| Base de datos | PostgreSQL 15 |
| Caché | Redis |
| Frontend | Next.js 14 (App Router, TypeScript) |
| Brain IA | Ollama / DeepSeek-R1:1.5b |
| Vector DB | Qdrant |
| WhatsApp | Baileys 6.7.21 |
| Automatización | N8N |
| Bot | Telegram |
| Infra | Docker Compose v2, Nginx reverse proxy |

---

## REGLAS CRÍTICAS DE SEGURIDAD

### Secretos
- **Nunca** guardar credenciales reales, API keys, correos, passwords, tokens o IPs privadas en el repo.
- Usar `infra/.env` en VPS/local y mantener solo `infra/.env.example` en git.
- Si detectas un secreto en código o docs, reemplázalo por placeholders y documenta la rotación necesaria.

### Deploy
- El deploy a VPS debe salir solo desde `main` o desde una etiqueta/release aprobada.
- Antes de hacer push a `main`, validar cambios con tests mínimos y revisar diff de seguridad.
- Exponer públicamente solo Nginx (`80/443`); el resto de puertos deben quedar internos o ligados a `127.0.0.1`.

### Docker
- Usar `docker compose` (v2), nunca `docker-compose` (v1).
- Frontend requiere rebuild completo; backend puede reiniciarse por servicio cuando aplique.
- No dejes valores por defecto inseguros para passwords o API keys en `docker-compose.vps.yml`.

### Git en VPS
```bash
git -C /home/mystic/sonora-digital-corp <comando>
```

---

## PROTOCOLO DE COLABORACIÓN ENTRE AGENTES

Cuando trabajes junto con Codex/Claude Code en el mismo repo:

1. **Leer primero** `docs/secure_deploy_workflow.md`.
2. Confirmar rama actual, `git status` y último commit antes de editar.
3. Declarar en una línea qué archivo tocarás y por qué.
4. Hacer cambios pequeños, verificables y con rollback claro.
5. Reportar siempre:
   - resumen del diff,
   - comandos corridos,
   - riesgos de deploy,
   - siguiente acción recomendada.

Prompt base sugerido para otra IA terminal:

```text
Estamos trabajando sobre el repo sonora-digital-corp.
Objetivo actual: <objetivo>.
Reglas:
1) No expongas secretos ni los pegues en respuestas.
2) Antes de editar, muestra: rama actual, git status corto y archivos que tocarás.
3) Propón la estrategia mínima, compárala contra 1 alternativa y elige la más segura.
4) Si el cambio afecta deploy VPS, valida impacto en docker compose, variables de entorno y puertos expuestos.
5) Al final entrega: resumen, diff lógico, comandos ejecutados, riesgos y rollback.
6) Si ves credenciales en el repo, reemplázalas por placeholders y documenta rotación.
```

---

## ENDPOINTS PRINCIPALES

```text
POST /auth/login
GET  /auth/me
GET  /dashboard
POST /facturas/xml
GET  /cierre/{ano}/{mes}
POST /api/brain/ask
POST /api/brain/swarm
POST /api/brain/feedback
POST /api/wa/webhook
GET  /status
```

---

## MEMORIA OPERATIVA VPS

- Revisar RAM antes de levantar modelos pesados.
- Pausar Ollama si no se está usando.
- Evitar contenedores en restart-loop.
- Toda credencial real vive fuera del repo y debe rotarse si alguna vez se expuso.
- `docker restart hermes_telegram_bot` (no docker compose restart desde raíz — falla sin compose file)
- Container Telegram usa `DEFAULT_BOT_TOKEN` internamente (mapeado desde `TELEGRAM_TOKEN` en infra/.env)

---

## PENDIENTES CRÍTICOS (actualizado 2026-03-27)

### Credenciales faltantes en infra/.env
- 🔴 `MP_ACCESS_TOKEN` — MercadoPago real (generar en developers.mercadopago.com)
- 🔴 `CLAUDE_BOT_TOKEN` — vacío; definir si se activa o se comenta
- 🔴 `ANTHROPIC_API_KEY` — agregar desde console.anthropic.com
- 🟡 Credencial TW — nombre de var pendiente confirmar con Luis Daniel

### Infraestructura
- 🟡 Chip Telcel número WhatsApp dedicado (para Baileys)
- 🟡 Verificar Telegram bot responde con token rotado (2026-03-27)
- 🟢 Rebuild frontend en producción (imagen nueva pendiente deploy)

### Completado esta sesión (2026-03-27)
- ✅ TELEGRAM_TOKEN rotado en BotFather + infra/.env actualizado
- ✅ Rebrand MYSTIC→HERMES: soul.md, n8n_catalog.yaml, mystic_monitor.sh→hermes_monitor.sh
- ✅ Commit 6b9d398 + push a main
