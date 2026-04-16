# GitHub Workflows — HERMES OS

Este directorio contiene los workflows de GitHub Actions para el proyecto HERMES OS.

---

## 📋 Workflows Disponibles

### `deploy.yml` — Deploy Vercel + VPS + Telegram ⭐ PRINCIPAL

**Trigger**: Push a `main` o manual

**Qué hace**:
```
Push a main
    ↓
┌───────────────────────────────┐
│  Job 1: deploy-vercel         │  Paralelo
│  → Vercel (mission-control)   │
└───────────┬───────────────────┘
            │
┌───────────▼───────────────────┐
│  Job 2: deploy-vps            │  Paralelo
│  → VPS (FastAPI + Docker)     │
└───────────┬───────────────────┘
            │
┌───────────▼───────────────────┐
│  Job 3: notify                │
│  → Telegram (CEO bot)         │
└───────────────────────────────┘
            ↓
       Mensaje Telegram
```

**Duration**: 8-15 minutos

**Documentación**:
- [`docs/DEPLOY_QUICK_START.md`](../docs/DEPLOY_QUICK_START.md) — Guía rápida (5 min)
- [`docs/GITHUB_SECRETS_SETUP.md`](../docs/GITHUB_SECRETS_SETUP.md) — Cómo configurar secrets
- [`docs/CI_CD_WORKFLOW.md`](../docs/CI_CD_WORKFLOW.md) — Detalles técnicos

**Secrets Requeridos**:
```
VPS_HOST              ← IP o hostname VPS
VPS_SSH_USER          ← Usuario SSH (root)
VPS_SSH_KEY           ← Private key SSH (base64)
VERCEL_TOKEN          ← Token Vercel
VERCEL_PROJECT_ID     ← ID proyecto mission-control
VERCEL_ORG_ID         ← Organization ID (opcional)
TELEGRAM_TOKEN_CEO    ← Bot token Telegram
CEO_CHAT_ID           ← Chat ID Luis Daniel
```

**Setup**:
```bash
# 1. Generar valores
bash scripts/setup-github-secrets.sh

# 2. Agregar a GitHub
# https://github.com/perrykingla69-cyber/sonora-digital-corp/settings/secrets/actions

# 3. Test
# GitHub → Actions → Deploy — Vercel + VPS + Notify → Run workflow
```

---

### `ci.yml` — Tests and Linting

**Trigger**: Push a cualquier rama, PR

**Qué hace**:
- Tests Python
- Lint de código
- Type checking

**Duration**: 3-5 minutos

---

### `security.yml` — Security Scanning

**Trigger**: Push a main, Diario (2 AM UTC)

**Qué hace**:
- SAST (static analysis)
- Dependency vulnerabilities
- Secret scanning

**Duration**: 5-10 minutos

---

### `backup.yml` — Database Backups

**Trigger**: Diario (3 AM UTC)

**Qué hace**:
- Backup Postgres a S3
- Backup Redis keys
- Cleanup de backups viejos

**Duration**: 10-15 minutos

---

### `monitor.yml` — Health Checks

**Trigger**: Cada 5 minutos

**Qué hace**:
- Verifica status API
- Verifica health Docker
- Alerta si hay caída

**Duration**: 2-3 minutos

---

### `deploy-n8n.yml` — N8N Workflow Imports

**Trigger**: Manual, cuando hay cambios en `infra/n8n-workflows/`

**Qué hace**:
- Importa workflows JSON a N8N
- Valida sintaxis
- Backup de workflows existentes

**Duration**: 5-10 minutos

---

## 🚀 Quick Commands

### Test el workflow principal
```bash
# Manual (desde GitHub UI)
GitHub → Actions → Deploy — Vercel + VPS + Notify → Run workflow

# Automático (push a main)
echo "# Test" >> README.md
git add .
git commit -m "test: trigger deploy"
git push origin main
```

### Ver logs
```
GitHub → Actions → [Workflow name] → [Run ID] → [Job name]
```

### Rerun un workflow
```
GitHub → Actions → [Workflow name] → [Run ID] → Re-run failed jobs
```

---

## 🔐 Security Best Practices

✅ **Configurado**:
- Secrets encriptados (no visible en logs)
- SSH key sin passphrase (necesaria para automation)
- Environment variables por secret

⚠️ **Revisar regularmente**:
- Rotación de tokens (cada 30-90 días)
- Acceso a secrets (quién puede usarlos)
- Logs de workflows (no exponer datos sensibles)

---

## 📊 Status Badge

Agregar al README:

```markdown
[![Deploy Status](https://github.com/perrykingla69-cyber/sonora-digital-corp/actions/workflows/deploy.yml/badge.svg)](https://github.com/perrykingla69-cyber/sonora-digital-corp/actions/workflows/deploy.yml)
```

---

## 🐛 Troubleshooting

### Si un workflow falla

1. **Ver logs**: Actions → [Workflow] → [Run] → Expande job que falló
2. **Check secrets**: Settings → Secrets → Verifica que existan todos
3. **SSH key**: Verifica que esté sin passphrase
4. **Rollback manual**: Ver `docs/DEPLOY_QUICK_START.md`

### Errores comunes

| Error | Solución |
|-------|----------|
| `Permission denied (publickey)` | SSH key no está en VPS ~/ .ssh/authorized_keys |
| `Vercel: Project not found` | VERCEL_PROJECT_ID incorrecto |
| `curl: (7) Failed to connect` | VPS no responde, revisar docker logs |
| `400 Bad Request` (Telegram) | TELEGRAM_TOKEN_CEO o CEO_CHAT_ID inválido |

---

## 📞 Referencias

- **Deploy Guide**: `docs/DEPLOY_QUICK_START.md`
- **Secrets Setup**: `docs/GITHUB_SECRETS_SETUP.md`
- **Workflow Details**: `docs/CI_CD_WORKFLOW.md`
- **Script Helper**: `scripts/setup-github-secrets.sh`
- **GitHub Actions Docs**: https://docs.github.com/en/actions

---

**Última actualización**: 2026-04-16
