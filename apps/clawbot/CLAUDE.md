# agent:bots — ClawBot Gateway
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "clawbot telegram"` en Engram.

## Dominio
Gateway multi-canal: 4 bots Telegram (CEO/Público/Alertas/MYSTIC) + WhatsApp (Evolution API).
Node.js + Telegraf. Puerto: `3003`. Health: `GET /health`.

## Archivos clave
- `index.js` o `bot.js` — entry point Telegraf
- `skills/` — JSON skills (STATIC / BRAIN / GET / POST)
- `logger.js` — wrapper de logging estructurado (usar siempre, no console.log)
- `middleware/requireApiKey.js` — protección endpoints REST

## Reglas críticas
- **Solo polling** para bots (nunca webhook en Telegraf — conflicto con hermes_agent)
- Dedup mensajes WhatsApp: Redis TTL 30s (fix Evolution API bug #1858)
- Skills triggers: minúsculas, sin acentos
- Axios timeout mínimo: 10 000 ms en toda llamada externa
- Variables de entorno: `process.env`, nunca hardcoded
- Mensajes al usuario: siempre español

## Bots Telegram
| Variable | Bot | Audiencia |
|---|---|---|
| `TELEGRAM_TOKEN_CEO` | HERMES CEO | Solo Luis Daniel (chat_id: 5738935134) |
| `TELEGRAM_TOKEN_PUBLIC` | HERMES Público | Clientes |
| `TELEGRAM_TOKEN_HERMES` | Alertas | Sistema |
| `TELEGRAM_TOKEN_MYSTIC` | MYSTIC | Análisis |

## Comando /code
Delega tareas a executor en `host.docker.internal:9001/run`.
