# HERMES OS — Sub-Agentes Claude Code
> Cómo Claude Code opera en modo autónomo para este proyecto

## Filosofía
Claude Code actúa como HERMES: orquesta, delega, sintetiza.
No ejecuta inline lo que puede delegar. No pregunta lo obvio.

---

## Mapa de Sub-Agentes

### `sdd-explore` — Investigador
**Cuándo:** antes de implementar algo no trivial
**Hace:** lee el código relevante, busca patrones, compara opciones
**No hace:** escribe código, modifica archivos

### `sdd-apply` — Implementador  
**Cuándo:** cuando el plan está claro (spec existe)
**Hace:** escribe código, crea/edita archivos, sigue spec
**No hace:** toma decisiones de arquitectura sin spec

### `sdd-verify` — Validador
**Cuándo:** después de `sdd-apply`
**Hace:** verifica que la implementación coincide con spec
**Reporta:** CRITICAL / WARNING / SUGGESTION

### `general-purpose` — Comodín
**Cuándo:** tareas que no encajan en las anteriores
**Hace:** cualquier cosa fuera del contexto principal

---

## Cuándo Claude Code actúa sin que me preguntes

| Situación | Acción autónoma |
|-----------|----------------|
| Nuevo tenant en DB | Trigger auto-seed Qdrant |
| Error en healthcheck Docker | Diagnósticar + reportar causa raíz |
| Cambio de código en hermes-os | Evaluar si hacer deploy |
| Archivo con posible secret | Advertir antes de guardar |
| Tarea completada importante | `mem_save` en Engram |

---

## Contexto que siempre está disponible

- **CLAUDE.md** (`/home/mystic/CLAUDE.md`) — estado del proyecto, stack, reglas
- **Engram** (`mem_context`) — historial de sesiones, decisiones previas
- **SOUL.md** de cada agente — identidad y reglas de HERMES/MYSTIC/ClawBot
- **NicheRegistry** — nichos de negocio y fuentes de conocimiento

---

## Lo que NO necesito que me expliques

Si está en CLAUDE.md o en Engram, lo sé. No repitas:
- Qué es HERMES o MYSTIC
- El stack tecnológico
- Las reglas críticas (docker compose, JWT, etc.)
- El CEO_CHAT_ID o tokens de Telegram

Si algo cambió desde la última sesión, dímelo explícitamente.

---

## Para dejar de estar en terminal todo el día

### GitHub Actions (ya configurado)
Push a `main` → deploy automático → notificación Telegram al CEO.
No necesitas hacer nada manualmente.

### N8N (pendiente configurar)
Flujos que corren solos:
- Trigger auto-seed cuando llega nuevo tenant
- Alertas MYSTIC diarias a las 8am
- Backup DB semanal
- Health check cada 30min → alerta si algo falla

### Cron en VPS (próximo paso)
```bash
# Auto-seed semanal (lunes 6am)
0 6 * * 1 cd /home/mystic/hermes-os && docker compose exec -T hermes-api python agents/seeders/auto_seeder.py weekly

# Backup diario (3am)
0 3 * * * /home/mystic/hermes-os/infra/scripts/backup.sh
```

### Telegram como panel de control
Con ClawBot configurado, puedes:
- `/status` — ver todos los containers
- `/logs hermes-api` — ver logs en tiempo real
- `/seed contador` — forzar seed de un nicho
- MYSTIC te avisa automáticamente si algo falla

**La meta: tú solo haces `/status` desde el teléfono. Todo lo demás es automático.**
