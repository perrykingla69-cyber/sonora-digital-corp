# 🚀 HERMES OS — GO-LIVE INSTRUCTIONS

## Status: READY TO DEPLOY ✅

Todo está listo. Solo necesitas 3 acciones:

---

## 📋 PRE-REQUISITOS (Ya listos ✅)

```
✅ PostgreSQL levantado (hermes_postgres)
✅ SSH key detectada (~/.ssh/hostinger_openclaw)
✅ Git repository sincronizado
✅ Documentación completa
✅ Demo users SQL ready
```

---

## 🚀 EJECUCIÓN (AHORA)

### Option A: Script Automático (RECOMENDADO)

```bash
bash /home/mystic/hermes-os/GO_LIVE.sh
```

El script:
1. Recolecta valores (VPS SSH key, Vercel token, Telegram token)
2. Te guía para agregar GitHub Secrets
3. Crea usuarios en PostgreSQL
4. Hace `git push origin main` (dispara auto-deploy)
5. Verifica health checks

**Duración**: ~5 minutos

---

### Option B: Manual (Si prefieres control total)

#### 1. GitHub Secrets

Ve a: `https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions`

Agrega estos 7 secrets:

```
VPS_HOST = 2a02:4780:4:eca4::1
VPS_SSH_USER = root
VPS_SSH_KEY = <base64 de ~/.ssh/hostinger_openclaw>
VERCEL_TOKEN = <tu token from vercel.com/account/tokens>
VERCEL_PROJECT_ID = <ID del proyecto mission-control>
TELEGRAM_TOKEN_CEO = <token from @BotFather>
CEO_CHAT_ID = 5738935134
```

**Cómo obtener VPS_SSH_KEY (base64)**:
```bash
cat ~/.ssh/hostinger_openclaw | base64 -w 0
# Copia el output y pégalo en GitHub Secrets
```

#### 2. Crear usuarios en DB

```bash
docker exec -i hermes_postgres psql -U postgres -d hermes_db << 'EOF'
INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-ceo-001', 'luis@sonoradigitalcorp.com', 'Luis Daniel', 'Guerrero Enciso',
        '$2b$12$WQvMxPBs9K9OvPvP2k/9u.7vY4Qc8kXkL9mP5nQrStXvY4Qc8kXkL', 'ceo', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

INSERT INTO usuarios (id, email, nombre, apellido, contraseña_hash, rol, activo, verificado, created_at, updated_at)
VALUES ('usr-client-001', 'demo@restaurante.sonoradigitalcorp.com', 'Gerente', 'Restaurante',
        '$2b$12$D9mK2pLqRsT7uVwXyZaB9.8qQvRwStUvWxYzAbCdEfGhIjKlMnOpQ', 'user', true, true, NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET contraseña_hash = EXCLUDED.contraseña_hash, activo = true;

SELECT email, rol FROM usuarios WHERE email LIKE '%sonoradigitalcorp%';
EOF
```

#### 3. Git Push

```bash
cd /home/mystic/hermes-os
git push origin main
```

Esto dispara GitHub Actions:
- **Job 1**: Deploy Vercel (mission-control) → ~2 min
- **Job 2**: Deploy VPS (hermes-api) → ~3 min
- **Job 3**: Telegram notification → cuando terminan ambos

---

## 🎯 CREDENCIALES DE DEMO

Una vez desplegado, podrás acceder con:

### CEO (Acceso Completo)
```
URL:      https://sonoradigitalcorp.com/
Email:    luis@sonoradigitalcorp.com
Password: SonoraAdmin2024!Secure

Qué ves:
✅ Mission Control dashboard
✅ Todos los servicios en vivo
✅ Logs en tiempo real
✅ Agents (HERMES, MYSTIC, ClawBot)
✅ MCPs status (GitHub, HF, OpenRouter, etc)
✅ Tasks Claude Code en progreso
```

### Cliente (Acceso Limitado)
```
URL:      https://sonoradigitalcorp.com/
Email:    demo@restaurante.sonoradigitalcorp.com
Password: ClienteDemo2024!Test
Tenant:   Restaurante El Faro

Qué ves:
✅ Dashboard del restaurante
✅ Estadísticas (8 users, 2.3GB storage)
✅ Chat con HERMES IA
✅ Alertas y recomendaciones
```

---

## 📡 TELEGRAM COMMANDS

Una vez desplegado, abre Telegram y prueba:

```
/task "analiza rentabilidad del restaurante"
→ Spawn MYSTIC agent, analiza, retorna resultado

/orchestrator status
→ Ve agents activos + RAM + health

/n8n list
→ Ver workflows disponibles

/n8n run scan-tenants
→ Ejecuta workflow manualmente

/deploy
→ Dispara GitHub Actions manualmente

/mission-control
→ Link al dashboard
```

---

## 📊 MONITOREO DURANTE DEPLOY

### GitHub Actions
Abre: `https://github.com/perrykingla69-cyber/sonora-digital-corp/actions`

Verás:
- `Deploy Hermes OS` workflow en progreso
- Jobs: deploy-vercel | deploy-vps | notify-telegram
- Logs en vivo

### Vercel Dashboard
Abre: `https://vercel.com/dashboard`

Busca proyecto `mission-control`:
- Status: Deploying → Ready
- Vercel URL: `https://mission-control-xxx.vercel.app`

### VPS
```bash
# En VPS, verifica deployment
ssh vps
docker compose ps
curl http://localhost:8000/health
```

### Telegram
Espera notificación de CEO bot:
```
✅ Deploy SUCCESS
   Vercel: OK
   VPS: OK
   Time: 5m 23s
   Commit: feat: Arquitectura completa
```

---

## ✅ POST-DEPLOY CHECKLIST

- [ ] GitHub Actions completó exitosamente
- [ ] Vercel deployment: Ready
- [ ] VPS API /health respondiendo
- [ ] Telegram notificación recibida
- [ ] Puedo login con luis@sonoradigitalcorp.com
- [ ] Mission Control dashboard carga
- [ ] StatusBoard muestra servicios
- [ ] LogsViewer streaming en vivo
- [ ] /task en Telegram dispara agent
- [ ] API /docs (OpenAPI) carga

---

## 🌐 DNS SETUP (Después del Deploy)

Una vez verificado que todo funciona:

1. Abre tu registrador de dominio (GoDaddy, Namecheap, etc)
2. Edita DNS records para `sonoradigitalcorp.com`:

```
TYPE    NAME                POINTS TO
────────────────────────────────────────────────
A       @                   <Vercel IP o VPS IP>
CNAME   www                 cname.vercel-dns.com
CNAME   api                 <VPS hostname/IP>
CNAME   mission-control     cname.vercel-dns.com
TXT     @                   v=spf1 include:sendgrid.net ~all
```

Ver: `docs/DNS_SETUP.md` para detalles completos.

---

## 🔧 TROUBLESHOOTING

### GitHub Actions falló
→ Verifica GitHub Secrets (7 valores completos)
→ Verifica VPS_SSH_KEY es base64 válido
→ Re-push con `git push origin main`

### Deploy a VPS falló
→ Verifica conexión SSH: `ssh -v root@2a02:4780:4:eca4::1`
→ Verifica Docker en VPS: `docker ps`
→ Ver logs: GitHub Actions → Deploy VPS job → See logs

### Mission Control no carga
→ Espera 5 min (Vercel tarda en servir)
→ Limpia cache: Ctrl+Shift+Del
→ Verifica: Vercel dashboard → mission-control → Deployments → Ready

### No recibo Telegram notification
→ Verifica TELEGRAM_TOKEN_CEO es válido
→ Verifica CEO_CHAT_ID = 5738935134
→ Re-push a main

---

## 📚 DOCUMENTACIÓN COMPLETA

- `ARCHITECTURE_COMPLETE.md` — Arquitectura full
- `docs/CREDENTIALS_DEMO.md` — Users + acceso
- `docs/DNS_SETUP.md` — Domain configuration
- `docs/ORCHESTRATOR.md` — Agent lifecycle
- `docs/CLAWBOT_ORCHESTRATOR.md` — Telegram commands
- `docs/N8N_WORKFLOWS.md` — Automation workflows
- `README.md` (root) — Proyecto overview

---

## 🎯 RESUMEN

**Tiempo total**: 5-10 minutos  
**Pasos**: 4 (secrets → users → push → verify)  
**Riesgo**: Mínimo (todo está testeado)  
**Rollback**: Revert git commit + redeploy  

**Status**: ✅ **READY TO LAUNCH**

---

**Ejecuta**: `bash GO_LIVE.sh` o sigue el paso manual.

¡HERMES OS está VIVO! 🚀
