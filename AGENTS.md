# AGENTS.md — HERMES AI OS Coding Standards
# Sonora Digital Corp

## General
- Idioma: español en comentarios y mensajes de usuario; inglés en nombres de variables/funciones
- No exponer secretos, API keys, passwords ni tokens en código o commits
- docker compose v2 siempre (nunca docker-compose)

---

## Python (FastAPI / Backend)
- Type hints obligatorios en funciones públicas
- No usar print() en producción — usar logging
- JWT field: `usuario` (no `user`)
- DB column: `año` con ñ en tabla `cierres_mes`

---

## TypeScript / React (Frontend Next.js 14)
- Usar const/let, nunca var
- Preferir interfaces sobre types
- localStorage keys: `hermes_token`, `hermes_user`, `hermes_consent_v1`
- NEXT_PUBLIC vars deben ir en build.args en docker-compose, no en environment

---

## Node.js / Telegram Bot

### Logging
- No usar `console.log` en producción — usar el logger estructurado:
  ```js
  const log = require('./logger'); // o el wrapper local del proyecto
  log.info('mensaje descriptivo', { contexto });
  ```
- Niveles: `log.info`, `log.warn`, `log.error` — nunca strings genéricos

### Async / Error handling
- Async/await siempre — nunca callbacks desnudos
- Todos los handlers de Telegraf deben tener try/catch:
  ```js
  bot.command('start', async (ctx) => {
    try {
      // lógica
    } catch (err) {
      log.error('Error en /start', { err: err.message });
      await ctx.reply('Ocurrió un error. Intenta de nuevo.');
    }
  });
  ```

### Variables y mensajes
- Variables/funciones: inglés (camelCase)
- Mensajes al usuario final: siempre en español
- Nunca hardcodear tokens ni keys — leer de `process.env`

### HTTP / Axios
- Timeout explícito en todas las llamadas axios (mínimo 10 000 ms):
  ```js
  axios.get(url, { timeout: 10000 })
  ```
- Verificar `response.data` antes de desestructurar — nunca asumir shape

### Skills JSON — campos requeridos
```json
{
  "name": "nombre_unico_snake_case",
  "priority": 10,
  "triggers": ["trigger uno", "trigger dos"],
  "method": "STATIC",
  "response_text": "Respuesta fija al usuario"
}
```
- `method` permitidos: `STATIC`, `BRAIN`, `GET`, `POST`
- Para BRAIN usar `question_template` con `{{message}}` en lugar de `response_text`
- Para GET/POST usar `payload` o `endpoint`

---

## Seguridad

- Nunca loggear objetos `req` completos — pueden contener tokens o cookies de sesión
- Sanitizar inputs antes de pasar a templates: usar `JSON.stringify`, no interpolación directa
- Endpoints REST del bot deben usar middleware `requireApiKey`
- No exponer stack traces al usuario final:
  ```js
  // MAL — expone internals
  res.status(500).json({ error: err.stack });

  // BIEN — log interno, respuesta genérica
  log.error('Error interno', { err });
  res.status(500).json({ error: 'Error interno del servidor' });
  ```
- Variables de entorno sensibles: definir en `infra/.env`, nunca en el código fuente
- Si detectas un secreto en el repo: reemplazar por placeholder y documentar rotación necesaria

---

## Skills / Brain IA

- Triggers en minúsculas, sin acentos cuando sea posible para mayor alcance:
  - Bien: `"facturas", "dame el saldo", "cuanto debo"`
  - Mal: `"Facturas", "Dame el saldo", "Cuánto debo"`
- **STATIC**: para respuestas fijas (FAQ, precios, definiciones) — cero costo API
- **BRAIN**: para consultas dinámicas al Brain IA — usar `question_template` con `{{message}}`
- **POST/GET**: para integraciones externas — siempre con `timeout` explícito
- Un skill por responsabilidad — no mezclar lógica de negocio distinta en el mismo skill

---

## Performance / Docker

- Containers con prefijo `hermes_` (nunca `mystic_`)
- Red Docker: `hermes_net` o `hermes_network`
- Health checks obligatorios en servicios críticos:
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/status"]
    interval: 30s
    timeout: 5s
    retries: 3
  ```
- No usar `latest` como tag en producción — usar versiones explícitas
- Si un proceso supera 200 MB de RAM en estado estable, investigar leaks
- Frontend requiere rebuild completo al cambiar código (baked en imagen)
- Antes de levantar modelos Ollama pesados, verificar RAM disponible

---

## Git / Commits

- Formato: `tipo(scope): descripción en español`
  - Ejemplos:
    - `feat(bot): agregar skill de consulta de facturas`
    - `fix(auth): corregir validación de JWT expirado`
    - `chore(docker): actualizar imagen base de backend`
    - `security(env): rotar TELEGRAM_TOKEN expuesto`
- Tipos válidos: `feat`, `fix`, `chore`, `docs`, `refactor`, `security`, `test`
- No commitear archivos generados, `.env`, `node_modules`, `__pycache__`, `*.pyc`
- Rama estable: `main`
- Git en VPS: `git -C /home/mystic/sonora-digital-corp <cmd>`
