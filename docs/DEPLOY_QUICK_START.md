# Deploy Quick Start — HERMES OS

**TL;DR**: Configura 8 secrets en GitHub, haz push a `main`, y todo se deploya automáticamente.

---

## ⚡ 5 Minutos Setup

### 1. Generar valores de secrets

```bash
bash scripts/setup-github-secrets.sh
```

Este script te pedirá valores y te mostrará lo que debes copiar.

### 2. Agregar secrets a GitHub

Ve a:
```
https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions
```

Haz clic en **New repository secret** para cada uno:

| Secret | Origen |
|--------|--------|
| `VPS_HOST` | Tu IP/hostname VPS |
| `VPS_SSH_USER` | Usuario SSH (root) |
| `VPS_SSH_KEY` | Output del script anterior |
| `VERCEL_TOKEN` | vercel.com/account/tokens |
| `VERCEL_PROJECT_ID` | Vercel → mission-control → Settings |
| `VERCEL_ORG_ID` | Opcional (si tienes equipo en Vercel) |
| `TELEGRAM_TOKEN_CEO` | BotFather en Telegram |
| `CEO_CHAT_ID` | @userinfobot en Telegram |

### 3. Test del workflow

**Opción A** (manual):
1. GitHub → **Actions**
2. **Deploy — Vercel + VPS + Notify**
3. **Run workflow** (botón azul) → Branch: `main`

**Opción B** (automático):
```bash
# Haz un pequeño cambio y push
echo "# Test deploy" >> README.md
git add README.md
git commit -m "test: deploy workflow"
git push origin main

# Monitorea en GitHub → Actions
```

Deberías recibir un mensaje en Telegram cuando termine. ✅

---

## 📚 Documentación Completa

### Para entender el workflow
→ Ver **`docs/CI_CD_WORKFLOW.md`**

- Qué hace cada job
- Cómo funciona el retry logic
- Cómo debuggear errores

### Para configurar secrets paso a paso
→ Ver **`docs/GITHUB_SECRETS_SETUP.md`**

- Instrucciones detalladas por secret
- Cómo obtener cada valor
- Troubleshooting

### Para revisar la implementación
→ Ver **`.github/workflows/deploy.yml`**

- Workflow YAML completo
- Todos los pasos y scripts

---

## 🚀 Workflow

### Push a main
```bash
git commit -m "feat: new feature"
git push origin main
```

### GitHub Actions automáticamente

**1. Deploy to Vercel** (paralelo)
   - Código → `mission-control` 
   - URL: `mission-control-*.vercel.app`

**2. Deploy to VPS** (paralelo)
   - Docker pull + rebuild servicios
   - Health checks

**3. Notify Telegram** (después de ambos)
   - ✅ SUCCESS / ❌ FAILED
   - Detalles: commit, rama, actor, tiempo

Todo en **8-15 minutos**.

---

## 🔄 Rollback Manual

Si algo sale mal:

**VPS**:
```bash
cd /home/mystic/hermes-os
git log --oneline -n 5          # Ver commits
git reset --hard <SHA>          # Revertir
docker compose up -d --build    # Rereconstruir
```

**Vercel**:
1. [vercel.com](https://vercel.com)
2. Proyecto → Deployments
3. Selecciona deployment anterior
4. Promote to Production

---

## ⚙️ Configuración Adicional

### Cambiar el trigger
Edita `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches: [main]     # ← Cambiar ramas
  workflow_dispatch:     # ← Dejar para manual
  schedule:             # ← Agregar si quieres daily deploy
    - cron: '0 2 * * *'
```

### Agregar más health checks
En el job `deploy-vps`, amplía:

```bash
# Verificar más servicios
curl -f http://n8n:5678/health
curl -f http://qdrant:6333/health
```

### Notificaciones a múltiples canales
En el job `notify`, replica:

```yaml
- name: Send Slack notification
  uses: slack-notify/action@v1
  with:
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    message: "Deploy completed"
```

---

## 🐛 Troubleshooting

### ❌ SSH Connection Failed
```
Permission denied (publickey)
```
**Solución**: Verifica que la public key está en el VPS:
```bash
ssh vps "cat ~/.ssh/authorized_keys | grep github"
```
Si no está:
```bash
cat ~/.ssh/id_rsa.pub | ssh vps "cat >> ~/.ssh/authorized_keys"
```

### ❌ Vercel Deployment Failed
```
Error: Project not found
```
**Solución**: Verifica `VERCEL_PROJECT_ID` en GitHub → Settings → Secrets

### ❌ Telegram Message Not Sent
```
400 Bad Request
```
**Solución**: Verifica que:
- `TELEGRAM_TOKEN_CEO` es válido (BotFather)
- `CEO_CHAT_ID` es un número válido
- El bot no fue mutedo

Prueba manualmente:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### ❌ Docker Health Check Timeout
```
Health check failed after 3 attempts
```
**Solución**: 
1. SSH al VPS y revisa logs:
   ```bash
   docker logs hermes-api
   docker ps
   ```
2. Aumenta timeout en `.github/workflows/deploy.yml`
3. O agrega más reintentos en health check

---

## 📞 Debug Mode

Para ver todos los detalles del workflow:

1. GitHub → Actions → Deploy run
2. Expande cada job
3. Busca el step que falló
4. Lee el log completo

**Secrets no se muestran en logs** (GitHub los oculta automáticamente).

---

## 🔐 Seguridad

✅ **Está bien**:
- Secrets encriptados en GitHub
- SSH key sin passphrase (necesaria para automation)
- Tokens pueden rotarse en cualquier momento

⚠️ **Mejoras futuras**:
- Usar OIDC en lugar de SSH keys
- Short-lived tokens (30 días)
- Separate deploy keys por servicio

---

## 📋 Checklist Final

Antes de activar para producción:

- [ ] Todos los 8 secrets configurados en GitHub
- [ ] Test manual del workflow exitoso
- [ ] Mensaje Telegram recibido
- [ ] Vercel URL accesible
- [ ] VPS health check pasando
- [ ] SSH key sin passphrase configurada
- [ ] Backups automáticos configurados en VPS
- [ ] Rollback procedure documentado (en este archivo)

---

## 🎯 Próximos Pasos

1. **Ahora**: Ejecuta `bash scripts/setup-github-secrets.sh`
2. **Luego**: Configura secrets en GitHub
3. **Test**: Triggerear workflow manual
4. **Producción**: Push a main y observar

---

**Preguntas?** Ver documentación completa:
- `docs/CI_CD_WORKFLOW.md` — Detalles técnicos
- `docs/GITHUB_SECRETS_SETUP.md` — Cómo obtener cada valor
- `.github/workflows/deploy.yml` — Código fuente del workflow
