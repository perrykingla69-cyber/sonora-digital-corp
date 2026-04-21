# DEPLOYMENT RUNBOOK — Hermes OS Contador Fiscal MX MVP

**Última actualización**: 2026-04-21  
**Status**: Production Ready  
**Ambiente**: Hostinger VPS (srv1459711)

---

## 🚀 QUICK START — Deploy en 5 pasos

```bash
# 1. SSH al VPS
ssh vps

# 2. En /home/mystic/hermes-os
git pull origin main
docker compose up -d --build

# 3. Esperar servicios UP (30-60s)
watch -n 2 'docker compose ps'

# 4. Verificar health
curl -s http://localhost:8000/health | jq .

# 5. Acceder dashboard
open http://localhost:3000/contador/dashboard
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

- [ ] Git branch limpio (`git status`)
- [ ] All commits synced (`git log -1`)
- [ ] PostgreSQL migration applied (check tables)
- [ ] N8N workflow imported (UI: Workflows → alert-fiscal-deadlines.json)
- [ ] Environment variables set (CEO_PASSWORD, MP_ACCESS_TOKEN, WHATSAPP_NUMBER)
- [ ] Health checks passing (`curl http://localhost:8000/health`)
- [ ] Tests passing (`pytest apps/api/app/tests/ -v`)

---

## 🔧 SERVICIOS — Start/Stop/Restart

```bash
# Ver estado
docker compose ps

# Logs en vivo
docker compose logs -f hermes_api

# Restart un servicio
docker compose restart hermes_api

# Full redeploy
docker compose down && docker compose up -d --build

# Escala un servicio
docker compose up -d --scale hermes_api=2
```

---

## 🧪 POST-DEPLOYMENT TESTS

```bash
# Health check
curl -s http://localhost:8000/health

# Fiscal Agent: Calcula impuestos
curl -X POST http://localhost:8000/api/v1/agents/fiscal/calculate_taxes \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" \
  -d '{"ingresos": 100000, "gastos": 30000, "period": "202404", "regimen": "PM"}'

# Gamification: Stats
curl -s http://localhost:8000/api/v1/gamification/stats

# Dashboard acceso
curl -s http://localhost:3000/contador/dashboard

# N8N status
curl -s http://localhost:5678/api/v1/workflows
```

---

## 🚨 TROUBLESHOOTING

### hermes_evolution restarting
```bash
# Logs
docker compose logs hermes_evolution
# Fix: Verificar infra/.env (evolution config)
# Re-deploy
docker compose restart hermes_evolution
```

### PostgreSQL health: starting
```bash
# Esperar 20s, usualmente OK después
docker compose logs hermes_postgres | tail -20
# Si persiste: check disk space, RAM
```

### API latency alto
```bash
# Check CPU/Memory
docker stats

# View slow queries
docker compose exec hermes_postgres \
  psql -U postgres hermes_db -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"
```

---

## 📊 MONITORING — Dashboards

- **Grafana**: http://localhost:3001 (dashboards, alerts)
- **Prometheus**: http://localhost:9090 (métricas)
- **N8N**: http://localhost:5678 (workflow logs)
- **API Docs**: http://localhost:8000/docs

---

## 🔄 ROLLBACK PLAN

```bash
# Si algo falla, revert último commit
git revert HEAD
git push

# VPS auto-redeploya via git hook
# Monitor: docker compose logs -f
```

---

## 📈 SCALING PLAN

```bash
# Vertical: Aumenta CPU/RAM en Hostinger
# Horizontal: Escala contenedores
docker compose up -d --scale hermes_api=3

# Load balancer: Nginx (ya configurado)
# RLS en PostgreSQL: Ya activo
```

---

## 🛡️ SECURITY CHECKLIST

- [ ] HSTS enabled en Nginx
- [ ] JWT tokens en HttpOnly cookies
- [ ] RLS policies enforced en PostgreSQL
- [ ] Rate limiting activo
- [ ] Secrets en .env (no en repo)
- [ ] TLS/HTTPS (Let's Encrypt)

---

**Problemas? Contacta: luis@sonoradigital.corp**
