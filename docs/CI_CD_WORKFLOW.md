# GitHub Actions CI/CD Workflow — HERMES OS Deploy

Documento técnico que explica el workflow de auto-deploy configurado en `.github/workflows/deploy.yml`.

---

## 🎯 Objetivo

Automatizar los deploys a **Vercel (frontend)**, **VPS (backend)** y **Telegram (notificaciones)** cada vez que se haga push a `main`.

```
┌─────────────────┐
│   Push a main   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Trigger  │
    └────┬─────┘
         │
    ┌────▼──────────────────────────────┐
    │  Job 1: deploy-vercel (paralelo)  │
    │  Job 2: deploy-vps (paralelo)     │
    └──┬──────────────────────────────┬─┘
       │                              │
       ▼                              ▼
    Vercel                          VPS
    (nextjs-frontend)              (FastAPI + Docker)
       │                              │
       └──────────────┬───────────────┘
                      │
              ┌───────▼────────┐
              │ Job 3: notify  │
              │  (siempre)     │
              └────────────────┘
                      │
                      ▼
                   Telegram
                  (CEO bot)
```

---

## 📋 Estructura del Workflow

### Trigger
```yaml
on:
  push:
    branches: [main]    # Automático cuando pusheamos a main
  workflow_dispatch:    # Manual: Actions → Run workflow
```

### Concurrency
```yaml
concurrency:
  group: deploy-${{ github.ref }}  # Solo un deploy por rama a la vez
  cancel-in-progress: false        # No cancela runs en progreso
```

---

## 🔄 Jobs en Paralelo

### Job 1: `deploy-vercel`
**Qué hace**: Deploy la app Next.js a Vercel (mission-control).

**Pasos**:
1. **Checkout** — descarga el código del repo
2. **Deploy to Vercel** — usa `vercel/action@v8`
   - Tokens: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
   - Flag `production: true` → deploy a URL final (no preview)
3. **Test Vercel deployment** — verifica que la URL responda con HTTP 200/301/302
   - Reintentos: espera 5 segundos antes de testear
   - Si falla, todo el job falla (exit 1)

**Outputs**:
- `vercel_url` — URL final del deploy
- `vercel_status` — `success` o `failure`

**Timeout**: 15 minutos

---

### Job 2: `deploy-vps`
**Qué hace**: Deploy FastAPI + servicios Docker en el VPS.

**Pasos**:

#### 1. Detect Changed Services
Compara commits para saber qué servicios rebuildar:
```
apps/api/       → rebuild hermes-api
apps/clawbot/   → rebuild clawbot
apps/hermes/    → rebuild hermes-agent
apps/mystic/    → rebuild mystic-agent
apps/content-agent/ → rebuild content-agent
docker-compose.yml → rebuild todos
```

Outputs: flags `api`, `clawbot`, `hermes`, `mystic`, `content`.

#### 2. Deploy to VPS
SSH al VPS y ejecuta:
```bash
cd /home/mystic/hermes-os

# 1. Fetch latest
git fetch origin main
git reset --hard origin/main

# 2. Show commit info
git rev-parse --short HEAD  # SHA corto
git log -1 --pretty=format:"%s"  # Mensaje

# 3. Rebuild servicios detectados
docker compose --env-file infra/.env up -d --build

# 4. Health checks (retry 3 veces)
curl -f http://hermes-api:8000/health
```

**Retry Logic**:
- Intenta health check **hasta 3 veces**
- Espera 5 segundos entre intentos
- Si fallan los 3, termina con exit 1

**Output**: `vps_status` — `success` o `failure`

**Timeout**: 20 minutos

---

#### 3. VPS Health Check
Si el deploy fue exitoso, ejecuta health checks finales:
```bash
curl http://hermes-api:8000/health  # Verifica API
docker ps -q | wc -l                # Cuenta containers
```

**Output**: `vps_health` — `HEALTHY` o `UNHEALTHY`

---

### Job 3: `notify`
**Qué hace**: Envía notificación a Telegram con los resultados.

**Depende de**: `deploy-vercel` y `deploy-vps` (incluso si fallan).

**Pasos**:

#### 1. Prepare Notification
Lee los outputs de los jobs anteriores:
- `vercel_status` → ✅ o ❌
- `vps_status` → ✅ o ❌
- `vps_health` → HEALTHY o UNHEALTHY

Construye el mensaje Markdown:
```
✅ HERMES OS Deploy

Resultado: ✅ SUCCESS

Vercel: ✅ success
VPS: ✅ success (HEALTHY)

Detalles:
Commit: abc123de
Rama: main
Actor: @perrykingla69
Timestamp: 2026-04-16 14:23 UTC

[Ver en GitHub](https://github.com/...)
```

#### 2. Send Telegram Notification
Usa `appleboy/telegram-action@v0.1.1` para enviar el mensaje.

**Fallback**: Si falla, intenta con cURL directo (POST a Telegram API).

**Timeout**: 5 minutos

---

## 📊 Estados Finales

| Escenario | Vercel | VPS | Notif | Mensaje |
|-----------|--------|-----|-------|---------|
| Todo OK | ✅ | ✅ | ✅ | "✅ SUCCESS" |
| Vercel falla | ❌ | ✅ | ✅ | "❌ FAILED — Vercel error" |
| VPS falla | ✅ | ❌ | ✅ | "❌ FAILED — VPS error" |
| Ambos fallan | ❌ | ❌ | ✅ | "❌ FAILED — Multiple errors" |
| Telegram falla | ✅ | ✅ | ❌ | (No notif, pero log en Actions) |

---

## 🔐 Secrets Utilizados

| Secret | Job | Uso |
|--------|-----|-----|
| `VERCEL_TOKEN` | deploy-vercel | Auth a Vercel API |
| `VERCEL_ORG_ID` | deploy-vercel | ID de organización (opcional) |
| `VERCEL_PROJECT_ID` | deploy-vercel | ID de proyecto mission-control |
| `VPS_HOST` | deploy-vps | IP o hostname del VPS |
| `VPS_SSH_USER` | deploy-vps | Usuario SSH (root) |
| `VPS_SSH_KEY` | deploy-vps | Private key SSH (base64) |
| `TELEGRAM_TOKEN_CEO` | notify | Bot token Telegram |
| `CEO_CHAT_ID` | notify | Chat ID del CEO |

---

## 📝 Logs y Debugging

### Ver logs del workflow

1. GitHub → **Actions**
2. Selecciona **Deploy — Vercel + VPS + Notify**
3. Haz clic en la run (ej: "test: trigger deploy workflow")
4. Expande cada job para ver los pasos

### Logs detallados por job

**deploy-vercel**:
- Logs de Vercel
- URL final del deploy
- Resultado del health check

**deploy-vps**:
- Git fetch y reset
- Commit SHA y mensaje
- Servicios detectados como changed
- Output de `docker compose up -d --build`
- Resultado de health checks (3 intentos)

**notify**:
- Mensaje Telegram preparado
- Resultado del envío

---

## 🚀 Triggerear Manualmente

Si quieres deployer sin hacer push:

1. GitHub → **Actions**
2. Sidebar → **Deploy — Vercel + VPS + Notify**
3. **Run workflow** (botón azul)
4. Branch: `main`
5. **Run workflow**

Esto ejecutará todo aunque no haya cambios en el código.

---

## ⏱️ Duración Típica

| Job | Duración |
|-----|----------|
| deploy-vercel | 3-5 min |
| deploy-vps | 5-10 min (rebuild service) o 1-2 min (sin cambios) |
| notify | <1 min |
| **Total** | **8-15 minutos** |

---

## ⚠️ Error Handling

### Si `deploy-vercel` falla
- ❌ Notificación de error a Telegram
- ✅ VPS sigue adelante (jobs paralelos)
- Mensaje incluye "Vercel: ❌ failure"

### Si `deploy-vps` falla
- ❌ Notificación de error a Telegram
- ✅ Vercel ya está deployado (no se revierte)
- Mensaje incluye "VPS: ❌ failure"

### Si `notify` falla
- ✅ Los deploys siguen siendo exitosos
- ⚠️ Solo falta la notificación Telegram
- Fallback cURL intenta reenviar

---

## 🔄 Rollback Manual

Si algo sale mal después del deploy:

**En el VPS**:
```bash
cd /home/mystic/hermes-os

# Ver últimos commits
git log --oneline -n 5

# Revertir a commit anterior
git reset --hard <SHA_COMMIT_ESTABLE>

# Rereconstruir containers
docker compose --env-file infra/.env up -d --build

# Verificar
docker ps
curl http://hermes-api:8000/health
```

**En Vercel**:
1. Ve a [vercel.com](https://vercel.com)
2. Selecciona proyecto **mission-control**
3. **Deployments** → Busca el deployment anterior
4. Haz clic en **Promote to Production**

---

## 📌 Notas Importantes

1. **Concurrency**: Solo un deploy a la vez en main. Si haces 3 pushes seguidos, el tercero esperará a que terminen los anteriores.

2. **Timeout**: Cada job tiene un timeout. Si se pasa, se cancela automáticamente.

3. **SSH Key**: Debe ser una private key válida sin passphrase, en base64.

4. **Health Check**: Verifica que hermes-api responda. Si hay otros servicios críticos, se puede extender.

5. **Telegram**: El mensaje usa Markdown. Si el envío falla, cURL intenta de nuevo.

---

## 🎓 Próximos Pasos

1. **Configurar secrets** → ver `docs/GITHUB_SECRETS_SETUP.md`
2. **Test manual** → Actions → Run workflow
3. **Monitorear primeros deploys** → revisar logs en detail
4. **Opcional**: Agregar más health checks (frontend, n8n, etc.)
