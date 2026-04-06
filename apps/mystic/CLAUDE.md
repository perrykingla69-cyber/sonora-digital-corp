# agent:mystic — Shadow Analyst MYSTIC
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "mystic shadow"` en Engram.

## Dominio
Agente de análisis estratégico. Scan horario. Alerta solo lo crítico al CEO.
Modelo: `thudm/glm-z1-rumination:free` vía OpenRouter.

## Archivo clave
- `agent.py` — loop de análisis, reglas de alerta, envío Telegram

## Reglas de alerta
| Nivel | Cuándo | Acción |
|---|---|---|
| 🔴 Crítico | Caída de servicio, error en prod | Telegram inmediato |
| 🟡 Importante | Anomalía, latencia alta | Resumen 8am |
| 🟢 OK | Todo normal | Silencio |

## Reglas críticas
- No spam — máx 1 alerta 🔴 cada 10 min por tipo
- Modelo: `OPENROUTER_API_KEY` → `thudm/glm-z1-rumination:free`
- Puerto interno: ninguno (solo outbound Telegram)
- Bot: `TELEGRAM_TOKEN_MYSTIC` → chat_id CEO: `5738935134`
