# AGENTS.md — HERMES AI OS Coding Standards
# Sonora Digital Corp

## General
- Idioma: español en comentarios y mensajes de usuario; inglés en nombres de variables/funciones
- No exponer secretos, API keys, passwords ni tokens en código o commits
- docker compose v2 siempre (nunca docker-compose)

## Python (FastAPI / Backend)
- Type hints obligatorios en funciones públicas
- No usar print() en producción — usar logging
- JWT field: `usuario` (no `user`)
- DB column: `año` con ñ en tabla `cierres_mes`

## TypeScript / React (Frontend Next.js 14)
- Usar const/let, nunca var
- Preferir interfaces sobre types
- localStorage keys: `hermes_token`, `hermes_user`, `hermes_consent_v1`
- NEXT_PUBLIC vars deben ir en build.args en docker-compose, no en environment

## Docker / Infra
- Nombres de containers: prefijo `hermes_`
- Red Docker: `hermes_net` o `hermes_network`
- Frontend requiere rebuild completo al cambiar código (baked en imagen)

## Git
- Commits en español descriptivo
- No commitear .env ni archivos con credenciales reales
- Rama estable: main
